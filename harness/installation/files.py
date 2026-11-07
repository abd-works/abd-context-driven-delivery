"""The skill, command, and rule annotations, and the installation that writes their markdown files."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from harness.agent_tools.agent_tools import AgentTool, InstallDestination
from harness.annotations.name import Name
from harness.installation.destination import Installation
from harness.installation.ide_layout import IdeLayout
from harness.markdown.front_matter import FrontMatter
from harness.markdown.markdown import MarkdownText
from harness.annotations.annotation import Destination, NamedDestination, annotation_kinds


class Skill(NamedDestination):
    flag = "_skill"
    channel = InstallDestination.SKILL


class Command(NamedDestination):
    flag = "_command"
    channel = InstallDestination.COMMAND


class Rules(Destination):
    flag = "_rules"
    channel = InstallDestination.RULE


skill = Skill
command = Command
rules = Rules


class InstructionsUnreadableAtInstall(Exception):
    """Reading an operation's instructions from its toolset failed while its slash command was being written.

    Writing the operation's docstring in their place would install a command that tells the agent something other
    than what the operation says, so the install stops and names the operation instead."""

    def __init__(self, toolset: Any, operation: str, cause: BaseException) -> None:
        self.toolset_name = type(toolset).__name__
        self.operation = operation
        super().__init__(
            f"{self.toolset_name}.{operation}: reading its instructions to write its slash command failed: "
            f"{type(cause).__name__}: {cause}"
        )


class FileInstallation(Installation):
    """Write the markdown files of one channel — skills, slash commands, or rules — where the IDE reads them."""

    channel = "markdown"
    # Operations whose file is the practice's or fidelity's own, named after it rather than after the operation.
    _GUIDANCE_OWN_OPERATIONS = frozenset({"instructions", "rules-markdown"})
    _REFERENCE_LINK = re.compile(r"\]\((?:\.\./)+references/([\w.-]+\.md)\)")
    _RULE_FILE_NAME = re.compile(r"`(practices/[\w/.-]+)\.mdc`")

    # The channels a file installation writes, in the order a tool's files are written.
    CHANNELS = (InstallDestination.SKILL, InstallDestination.COMMAND, InstallDestination.RULE)

    def __init__(
        self,
        layout: IdeLayout,
        path: Path | str,
        destination: str = "",
        mcp_mode: bool = False,
        repo: Path | str | None = None,
    ) -> None:
        super().__init__(layout, path, repo=repo)
        self.destination = destination
        self.mcp_mode = mcp_mode

    def relative_path(self, toolset: Any, name: str) -> Path:
        """Where the file for toolset's operation name goes, from the IDE folder."""
        folder = self._kebab_folder(self.folder_for(toolset))
        operation = Name(name).kebab
        if self.destination == InstallDestination.SKILL:
            skill_folder = self._skill_folder(toolset, operation)
            return Path("skills") / (skill_folder if self.layout.nests_skills else self._flat_skill_folder(skill_folder)) / "SKILL.md"
        if self.destination == InstallDestination.COMMAND:
            parent = folder.parent if getattr(toolset, "practice_guidance", None) is not None and folder.name else folder
            return Path(self.layout.commands_folder) / parent / f"{self._command_stem(toolset, operation)}.md"
        if self.destination == InstallDestination.RULE:
            return self._rule_path(toolset, folder)
        return self.folder_for(toolset) / name

    def write(self, tool: AgentTool) -> None:
        if not self.destination or (tool.kind == "tool" and self.destination not in self.CHANNELS):
            return
        parts = self._parts(tool)
        relative = self.relative_path(tool.toolset, tool.deploy_name)
        body = "\n\n".join(part for part in parts if part).rstrip()
        text = f"{body}\n" if body else ""
        if self.destination == InstallDestination.RULE:
            text = MarkdownText(text).without_yaml
            text = self._rules_front_matter(text, tool.toolset) + text
        elif self.destination == InstallDestination.SKILL:
            text = self._skill_front_matter(relative.parent.name, self._skill_overview(tool.toolset, parts)) + text
        self._write_file(self.path / relative, text)

    def write_standing_rule(self, source: Path) -> None:
        """Install one always-on rule from ``cdd_guidance/rules``: ``.md`` scoped by ``paths`` for
        Claude Code, the source front matter as written for every other IDE."""
        text = source.read_text(encoding="utf-8")
        if self.layout.scopes_rules_by_paths:
            front_matter = FrontMatter(text)
            fields, body = front_matter.fields, front_matter.content
            globs = "" if fields.get("alwaysApply") == "true" else fields.get("globs", "")
            text = self._claude_rules_front_matter(fields.get("description", source.stem), globs) + body
        self._write_file(Path(self.path) / "rules" / f"{source.stem}{self.layout.rule_suffix}", text)

    def _parts(self, tool: AgentTool) -> list[str]:
        """The body, the practice's schema, and the line that tells the agent how to run the operation."""
        parts = [self._body_for(tool)]
        schema = self._schema_guide(tool)
        if schema and schema not in parts[0]:
            parts.append(schema)
        if self.mcp_mode:
            fidelity_parts = self._fidelity_invoke_parts(tool.toolset) if tool.name == "instructions" else []
            parts.extend(fidelity_parts or [tool.invoke_line()])
        elif self._needs_shell_invoke(tool):
            parts.append(self._shell_invoke_line(tool))
        return parts

    def _write_file(self, dest: Path, text: str) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self._with_installed_references(text, dest), encoding="utf-8")
        self.track_write(dest)

    def _guidance_slug(self, toolset: Any) -> str | None:
        """The kebab slug of a practice or fidelity's guidance toolset, whose files are named after it; none for any
        other toolset."""
        if getattr(toolset, "practice_guidance", None) is None:
            return None
        slug = getattr(toolset, "slug", None)
        return Name(str(slug)).kebab if slug else None

    def _rule_path(self, toolset: Any, folder: Path) -> Path:
        suffix = self.layout.rule_suffix
        if getattr(toolset, "practice_guidance", None) is None:
            return Path("rules") / folder.with_suffix(suffix)
        parent = folder.parent if folder.name else folder
        return Path("rules") / parent / f"{self._guidance_slug(toolset) or self._command_stem(toolset, folder.name)}{suffix}"

    def _flat_skill_folder(self, folder: Path) -> Path:
        """Claude Code only discovers ``skills/<name>/SKILL.md``, so nested folders join into one name."""
        parts = [part for part in folder.parts if part not in {".", "/", "\\"}]
        return Path("-".join(parts) or "toolset")

    def _kebab_folder(self, folder: Path) -> Path:
        parts = [
            part if part in {"/", "\\"} or (len(part) == 2 and part.endswith(":")) else Name(part).kebab
            for part in folder.parts
        ]
        return Path(*parts) if parts else folder

    def _command_stem(self, toolset: Any, operation: str) -> str:
        slug = self._guidance_slug(toolset)
        if slug is None:
            return operation
        return slug if operation in self._GUIDANCE_OWN_OPERATIONS else f"{slug}-{operation}"

    def _skill_operations(self, toolset: Any) -> list[str]:
        bag = getattr(toolset, "tools", None) or {}
        values = bag.values() if isinstance(bag, dict) else bag
        return [Name(getattr(tool, "deploy_name", None) or tool.name).kebab for tool in values if getattr(tool, "install_to_skill", False)]

    def _skill_folder(self, toolset: Any, operation: str) -> Path:
        folder = self._kebab_folder(self.folder_for(toolset))
        shares_folder = len(self._skill_operations(toolset)) > 1
        slug = self._guidance_slug(toolset)
        if slug is not None:
            leaf = (folder.parent if folder.name else folder) / slug
            return leaf / operation if shares_folder and operation not in self._GUIDANCE_OWN_OPERATIONS else leaf
        if operation in self._GUIDANCE_OWN_OPERATIONS or (not shares_folder and operation == folder.name):
            return folder
        return folder / operation

    def _schema_guide(self, tool: AgentTool) -> str:
        """Practice schema joined into instructions, including a fidelity skill."""
        if tool.name != "instructions":
            return ""
        toolset = tool.toolset
        guide = getattr(toolset, "schema_guide", None)
        if not callable(guide):
            practice = getattr(toolset, "practice_guidance", None)
            guide = getattr(practice, "schema_guide", None) if practice is not None else None
        return (guide() or "").strip() if callable(guide) else ""

    def _instructions_at_install(self, tool: AgentTool) -> str:
        """Expand ``@agent_instructions`` on the live toolset when writing slash markdown."""
        try:
            value = getattr(tool.toolset, tool.name)
        except Exception as exc:  # noqa: BLE001 - raised again as the named failure, with the operation it was for
            raise InstructionsUnreadableAtInstall(tool.toolset, tool.name, exc) from exc
        if isinstance(value, str) and value.strip():
            return value.strip()
        return tool.docstring

    def _body_for(self, tool: AgentTool) -> str:
        if self.mcp_mode:
            # An ``"""overview"""`` docstring names the section the MCP tool returns; it is not body text.
            return "" if tool.docstring.strip() == "overview" else tool.docstring
        if tool.kind == "instructions":
            return self._instructions_at_install(tool)
        if self.destination == InstallDestination.RULE:
            result = getattr(tool.toolset, tool.name, None)
            markdown = getattr(result, "markdown", None)
            if isinstance(markdown, str) and markdown.strip():
                return markdown.strip()
            formatted = getattr(result, "formatted", None)
            if callable(formatted):
                return str(formatted()).strip()
        return tool.docstring

    def _fidelity_one_liner(self, child: Any) -> str:
        name = getattr(child, "name", "") or ""
        overview = (getattr(child, "overview", None) or "").strip()
        summary = next(
            (line.strip() for line in overview.splitlines() if line.strip() and not line.strip().startswith(("#", "**"))),
            "",
        )
        return f"{name} — {summary}" if summary else name

    def _shell_command(self, tool: AgentTool) -> str:
        """The command a slash command or skill without MCP runs: the repository's own script for the operation, or a
        Python one-liner that makes the toolset and calls it."""
        script = self.repo / "scripts" / f"{tool.deploy_name}.py" if self.repo is not None else None
        if script is not None and script.is_file():
            return f'python "{script.resolve()}"'
        cls = type(tool.toolset)
        call = f'AgentToolSet.instantiate("{cls.__module__}:{cls.__name__}").{tool.name}()'
        code = f"from harness.agent_tools.agent_tools import AgentToolSet; print({call})"
        escaped = code.replace("\\", "\\\\").replace('"', '\\"')
        return f'python -c "{escaped}"'

    def _needs_shell_invoke(self, tool: AgentTool) -> bool:
        """``@agent_tool`` on skill/command without ``@mcp`` gets a Shell/python tail."""
        return self.destination in {InstallDestination.SKILL, InstallDestination.COMMAND} and tool.kind == "tool" and not tool.install_to_mcp

    def _shell_invoke_line(self, tool: AgentTool) -> str:
        return f"Run from the repository root with the Shell tool:\n\n```text\n{self._shell_command(tool)}\n```"

    def _fidelity_invoke_parts(self, toolset: Any) -> list[str]:
        entries = getattr(getattr(toolset, "fidelities", None), "entries", None) or {}
        parts: list[str] = []
        for child in entries.values():
            member = getattr(type(child), "instructions", None)
            getter = getattr(member, "fget", member)
            invoke = (
                f"Use MCP tool: `{getattr(child, 'slug', '')}()`"
                if annotation_kinds.annotated_for(InstallDestination.MCP, getter)
                else ""
            )
            parts.append("\n\n".join(piece for piece in (self._fidelity_one_liner(child), invoke) if piece))
        return parts

    def _with_installed_references(self, text: str, dest: Path) -> str:
        """Point links into ``cdd_guidance/references`` at the copy in ``<ide>/references``, and name
        rule files with this IDE's extension."""
        text = self._REFERENCE_LINK.sub(lambda match: f"]({self._install_reference(match.group(1), dest)})", text)
        if self.layout.rule_suffix != ".mdc":
            text = self._RULE_FILE_NAME.sub(rf"`\1{self.layout.rule_suffix}`", text)
        return text

    def _install_reference(self, name: str, dest: Path) -> str:
        """Copy one ``cdd_guidance/references`` file into ``<ide>/references``; return its link from ``dest``."""
        repo = self.repo or Path(__file__).resolve().parents[2]
        source = repo / "cdd_guidance" / "references" / name
        target = Path(self.path) / "references" / name
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            self.track_write(target)
        return Path(os.path.relpath(target, dest.parent)).as_posix()

    def _skill_overview(self, toolset: Any, parts: list[str]) -> str:
        raw = getattr(toolset, "overview", None)
        source = raw.strip() if isinstance(raw, str) and raw.strip() else (parts[0] if parts else "")
        return self._first_paragraph(self._without_mcp_invoke(source))

    def _first_paragraph(self, text: str) -> str:
        """The skill description is the opening paragraph, without the section heading or rule lines."""
        lines = [line for line in text.splitlines() if not line.lstrip().startswith("#") and line.strip() != "---"]
        return "\n".join(lines).strip().split("\n\n")[0].strip()

    def _without_mcp_invoke(self, text: str) -> str:
        lines: list[str] = []
        skip_shell_block = False
        for line in text.splitlines():
            stripped = line.strip().lower()
            if skip_shell_block:
                skip_shell_block = not stripped.startswith("```")
                continue
            if stripped.startswith("run from the repository root with the shell tool:"):
                skip_shell_block = True
            elif not stripped.startswith("use mcp tool:"):
                lines.append(line)
        return "\n".join(lines).strip()

    def _skill_front_matter(self, name: str, overview: str) -> str:
        description = overview.strip() or name
        indented = "\n".join(f"  {line}" if line else "  " for line in description.splitlines())
        return f"---\nname: {name}\ndescription: >-\n{indented}\n---\n\n"

    def _rules_front_matter(self, body: str, toolset: Any = None) -> str:
        description = next(
            (
                line.strip().replace('"', "'")
                for line in body.splitlines()
                if line.strip() and not line.strip().startswith(("#", "-", "```"))
            ),
            "Practice rules.",
        )
        applies = getattr(getattr(toolset, "rules", None), "applies_to", None)
        globs = (getattr(applies, "globs", "") or "") if applies is not None else ""
        if self.layout.scopes_rules_by_paths:
            return self._claude_rules_front_matter(description, globs)
        always_apply = bool(getattr(applies, "always_apply", None)) if applies is not None else False
        lines = ["---", f"alwaysApply: {'true' if always_apply else 'false'}", f'description: "{description}"']
        if globs:
            lines.append(f"globs: {globs}")
        return "\n".join([*lines, "---"]) + "\n\n"

    def _claude_rules_front_matter(self, description: str, globs: str) -> str:
        """Claude Code rules scope by ``paths``; a rule without paths loads in every session."""
        lines = ["---", f'description: "{description}"']
        patterns = [item.strip() for item in globs.split(",") if item.strip()]
        if patterns:
            lines.append("paths:")
            lines.extend(f'  - "{pattern}"' for pattern in patterns)
        lines.append("---")
        return "\n".join(lines) + "\n\n"
