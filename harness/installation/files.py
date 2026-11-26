"""The skill, command, and rule annotations, and the installations that write their markdown files."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Protocol

from harness.agent_tools.agent_tools import AgentTool, AgentToolSet, InstalledName, InvokeLine
from harness.annotations.name import Name
from harness.installation.destination import Installation
from harness.markdown.front_matter import FrontMatter
from harness.annotations.annotation import Annotatable, Destination, annotation_kinds


class NamedDestination(Destination):
    """A file destination whose annotation may name what it installs: ``@skill("name")``, ``@skill(name="name")``, or
    bare ``@skill`` for the operation's own name."""

    def __new__(cls, target: Annotatable | None = None, name: str | None = None):
        annotation = object.__new__(cls)
        if isinstance(target, str):
            annotation.name = target
            return annotation
        annotation.name = name
        if callable(target):
            return annotation.annotate(target)
        return annotation


class Command(NamedDestination):
    """``@command``: install writes the operation as a slash command. Defined before *Skill*, so a command's name is
    the name an operation annotated as both is installed under."""

    flag = "_command"
    channel = "command"


class Skill(NamedDestination):
    """``@skill``: install writes the operation as a skill."""

    flag = "_skill"
    channel = "skill"


class Rules(Destination):
    """``@rules``: install writes what the member answers as a rules file; the member holds a collection of its
    toolset's tools, such as a practice's rules."""

    flag = "_rules"
    channel = "rules"
    marks_a_collection = True


skill = Skill
command = Command
rules = Rules


class RulesScope(Protocol):
    """The files a published rules collection applies to: every file, or those its globs match."""

    always_apply: bool | None
    globs: str


class PublishedRules(Protocol):
    """What a member annotated ``@rules`` answers, such as a practice's rules collection: its rules as an installed
    rules file holds them, as a list when it has no markdown of its own, and the files they apply to. The installation
    writes it as a rules file without knowing the class that answers it."""

    @property
    def prose(self) -> str: ...

    @property
    def applies_to(self) -> RulesScope: ...

    def formatted(self) -> str: ...


class InstructionsUnreadableAtInstall(Exception):
    """Reading an operation's instructions from its toolset failed while its slash command was being written.

    Writing the operation's docstring in their place would install a command that tells the agent something other
    than what the operation says, so the install stops and names the operation instead."""

    def __init__(self, toolset: AgentToolSet, operation: str, cause: BaseException) -> None:
        self.toolset_name = type(toolset).__name__
        self.operation = operation
        super().__init__(
            f"{self.toolset_name}.{operation}: reading its instructions to write its slash command failed: "
            f"{type(cause).__name__}: {cause}"
        )


class FileInstallation(Installation):
    """Write the markdown files of one file channel where the IDE reads them: *SkillInstallation*,
    *CommandInstallation*, and *RulesInstallation* each say where a tool's file goes (`relative_path`), the front
    matter that opens it (`front_matter`), and its body (`body`). A tool also published where a server answers an
    agent's calls, as MCP does, gets a file that tells the agent to call that tool rather than run a shell command."""

    _REFERENCE_LINK = re.compile(r"\]\((?:\.\./)+references/([\w.-]+\.md)\)")
    _RULE_FILE_NAME = re.compile(r"`(practices/[\w/.-]+)\.mdc`")

    # The line before the command a skill or command without MCP runs, which a skill's description leaves out.
    _SHELL_INVOKE = "Run from the repository root with the Shell tool:"
    # Whether a tool's file on this channel tells the agent how to run it: a skill's and a command's do.
    tells_how_to_run = True

    def relative_path(self, tool: AgentTool) -> Path:
        """Where the file for tool goes, from the IDE folder, named as its toolset says (``installed_as``)."""
        raise NotImplementedError

    def front_matter(self, tool: AgentTool, relative: Path, parts: list[str], text: str) -> str:
        """The front matter that opens the file for tool at relative, with its parts and text; none by default."""
        return ""

    def body(self, tool: AgentTool) -> str:
        """The body of the file for tool when it is not answered by a server: its instructions, expanded on the live
        toolset, or its docstring."""
        if tool.kind == "instructions":
            return self._instructions_at_install(tool)
        return tool.docstring

    def write(self, tool: AgentTool) -> None:
        parts = self._parts(tool)
        relative = self.relative_path(tool)
        body = "\n\n".join(part for part in parts if part).rstrip()
        text = f"{body}\n" if body else ""
        self._write_file(self.path / relative, self.front_matter(tool, relative, parts, text) + text)

    def _served(self, tool: AgentTool) -> bool:
        """Whether a server answers an agent's calls to tool, as MCP does."""
        return tool.is_published_to(annotation_kinds.answering_calls)

    def _parts(self, tool: AgentTool) -> list[str]:
        """The body, then the line that tells the agent how to run the operation: for a toolset's own tool, a line for
        each part the toolset lists, with the call to that part's own tool."""
        parts = [self._body_for(tool)]
        if self._served(tool):
            listed = self._listed_part_lines(tool.toolset) if self._installed_as(tool).is_own else []
            parts.extend(listed or [tool.invoke_line.text])
        elif self._needs_shell_invoke(tool):
            parts.append(self._shell_invoke_line(tool))
        return parts

    def _write_file(self, dest: Path, text: str) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(self._with_installed_references(text, dest), encoding="utf-8")
        self.wrote(dest)

    def _installed_as(self, tool: AgentTool) -> InstalledName:
        """Where tool's toolset puts its files and what it names them."""
        return tool.toolset.installed_as(tool)

    def _installed_folder(self, name: InstalledName) -> Path:
        """The folder name says, from the repository, in kebab case."""
        return self._kebab_folder(self.relative_folder(name.folder))

    def _kebab_folder(self, folder: Path) -> Path:
        parts = [
            part if part in {"/", "\\"} or (len(part) == 2 and part.endswith(":")) else Name(part).kebab
            for part in folder.parts
        ]
        return Path(*parts) if parts else folder

    def _stem(self, name: InstalledName, operation: str) -> str:
        """The file name of operation within name's folder: its toolset's stem, joined to the operation unless the
        tool is the toolset's own; the operation alone for a toolset named by its folder."""
        if name.stem is None:
            return operation
        return name.stem if name.is_own else f"{name.stem}-{operation}"

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
        return tool.served_body if self._served(tool) else self.body(tool)

    def _part_summary(self, part: AgentToolSet) -> str:
        """A part's name and the first line of prose of its overview."""
        name = part.name or ""
        overview = (part.overview or "").strip()
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
        call = f'ToolsetReference.parsed("{tool.toolset.reference}").made().{tool.name}()'
        code = f"from harness.agent_tools.agent_tools import ToolsetReference; print({call})"
        escaped = code.replace("\\", "\\\\").replace('"', '\\"')
        return f'python -c "{escaped}"'

    def _needs_shell_invoke(self, tool: AgentTool) -> bool:
        """``@agent_tool`` on skill/command without ``@mcp`` gets a Shell/python tail."""
        return self.tells_how_to_run and tool.kind == "tool" and not self._served(tool)

    def _shell_invoke_line(self, tool: AgentTool) -> str:
        return f"{self._SHELL_INVOKE}\n\n```text\n{self._shell_command(tool)}\n```"

    def _listed_part_lines(self, toolset: AgentToolSet) -> list[str]:
        """One line for each part toolset lists, such as each fidelity of a practice: its name and summary, then the
        MCP tool its own tool is published as, written by that tool."""
        lines: list[str] = []
        for part in toolset.listed_parts():
            own = next((tool for tool in part.tools.values() if part.installed_as(tool).is_own), None)
            invoke = own.invoke_line.text if own is not None and self._served(own) else ""
            lines.append("\n\n".join(piece for piece in (self._part_summary(part), invoke) if piece))
        return lines

    def _with_installed_references(self, text: str, dest: Path) -> str:
        """Point links into ``cdd_guidance/references`` at the copy in ``<ide>/references``, and name
        rule files with this IDE's extension."""
        text = self._REFERENCE_LINK.sub(lambda match: f"]({self._install_reference(match.group(1), dest)})", text)
        if self.layout.rule_suffix != ".mdc":
            text = self._RULE_FILE_NAME.sub(rf"`\1{self.layout.rule_suffix}`", text)
        return text

    def _install_reference(self, name: str, dest: Path) -> str:
        """Copy one ``cdd_guidance/references`` file of the repository being installed into ``<ide>/references``; return
        its link from ``dest``. An installation made for no repository has none to copy."""
        source = self.repository.references_folder / name if self.repository is not None else None
        target = Path(self.path) / "references" / name
        if source is not None and source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            self.wrote(target)
        return Path(os.path.relpath(target, dest.parent)).as_posix()

    def _claude_rules_front_matter(self, description: str, globs: str) -> str:
        """Claude Code rules scope by ``paths``; a rule without paths loads in every session."""
        lines = ["---", f'description: "{description}"']
        patterns = [item.strip() for item in globs.split(",") if item.strip()]
        if patterns:
            lines.append("paths:")
            lines.extend(f'  - "{pattern}"' for pattern in patterns)
        lines.append("---")
        return "\n".join(lines) + "\n\n"


class SkillInstallation(FileInstallation):
    """Write each ``@skill`` operation as a skill, ``skills/<name>/SKILL.md``, opened by its name and the first
    paragraph of its toolset's overview."""

    destination = Skill

    def relative_path(self, tool: AgentTool) -> Path:
        skill_folder = self._skill_folder(tool)
        return Path("skills") / (skill_folder if self.layout.nests_skills else self._flat_skill_folder(skill_folder)) / "SKILL.md"

    def front_matter(self, tool: AgentTool, relative: Path, parts: list[str], text: str) -> str:
        description = self._skill_overview(tool.toolset, parts).strip() or relative.parent.name
        indented = "\n".join(f"  {line}" if line else "  " for line in description.splitlines())
        return f"---\nname: {relative.parent.name}\ndescription: >-\n{indented}\n---\n\n"

    def _flat_skill_folder(self, folder: Path) -> Path:
        """Claude Code only discovers ``skills/<name>/SKILL.md``, so nested folders join into one name."""
        parts = [part for part in folder.parts if part not in {".", "/", "\\"}]
        return Path("-".join(parts) or "toolset")

    def _skill_operations(self, toolset: AgentToolSet) -> list[str]:
        return [Name(tool.deploy_name).kebab for tool in toolset.tools.values() if tool.is_published_to(Skill)]

    def _skill_folder(self, tool: AgentTool) -> Path:
        """The skill's folder: the toolset's own tool is its toolset's folder, or its stem's within it; another tool's
        has a folder of its own beneath that when the toolset publishes more than one skill."""
        name = self._installed_as(tool)
        operation = Name(tool.deploy_name).kebab
        folder = self._installed_folder(name)
        shares_folder = len(self._skill_operations(tool.toolset)) > 1
        if name.stem is not None:
            leaf = folder / name.stem
            return leaf / operation if shares_folder and not name.is_own else leaf
        if name.is_own or (not shares_folder and operation == folder.name):
            return folder
        return folder / operation

    def _skill_overview(self, toolset: AgentToolSet, parts: list[str]) -> str:
        overview = (toolset.overview or "").strip()
        source = overview or (parts[0] if parts else "")
        return self._first_paragraph(self._without_mcp_invoke(source))

    def _first_paragraph(self, text: str) -> str:
        """The skill description is the opening paragraph, without the section heading or rule lines."""
        lines = [line for line in text.splitlines() if not line.lstrip().startswith("#") and line.strip() != "---"]
        return "\n".join(lines).strip().split("\n\n")[0].strip()

    def _without_mcp_invoke(self, text: str) -> str:
        lines: list[str] = []
        skip_shell_block = False
        for line in text.splitlines():
            stripped = line.strip().casefold()
            if skip_shell_block:
                skip_shell_block = not stripped.startswith("```")
                continue
            if stripped.startswith(self._SHELL_INVOKE.casefold()):
                skip_shell_block = True
            elif not InvokeLine(line).is_invoke_line:
                lines.append(line)
        return "\n".join(lines).strip()


class CommandInstallation(FileInstallation):
    """Write each ``@command`` operation as a slash command in the IDE's commands folder."""

    destination = Command

    def relative_path(self, tool: AgentTool) -> Path:
        name = self._installed_as(tool)
        stem = self._stem(name, Name(tool.deploy_name).kebab)
        return Path(self.layout.commands_folder) / self._installed_folder(name) / f"{stem}.md"


class RulesInstallation(FileInstallation):
    """Write what each ``@rules`` member answers as a rules file, and the always-on rules of ``cdd_guidance/rules``,
    each opened by front matter that says which files it applies to."""

    destination = Rules
    tells_how_to_run = False

    def relative_path(self, tool: AgentTool) -> Path:
        name = self._installed_as(tool)
        folder = self._installed_folder(name)
        suffix = self.layout.rule_suffix
        if name.stem is None:
            return Path("rules") / folder.with_suffix(suffix)
        return Path("rules") / folder / f"{name.stem}{suffix}"

    def front_matter(self, tool: AgentTool, relative: Path, parts: list[str], text: str) -> str:
        return self._rules_front_matter(text, self._published_rules(tool))

    def body(self, tool: AgentTool) -> str:
        published = self._published_rules(tool)
        return published.prose.strip() or published.formatted().strip()

    def write_standing_rule(self, source: Path) -> None:
        """Install one always-on rule from ``cdd_guidance/rules``: ``.md`` scoped by ``paths`` for
        Claude Code, the source front matter as written for every other IDE."""
        front_matter = FrontMatter.of_file(source)
        text = front_matter.text
        if self.layout.scopes_rules_by_paths:
            fields, body = front_matter.fields, front_matter.content
            globs = "" if fields.get("alwaysApply") == "true" else fields.get("globs", "")
            text = self._claude_rules_front_matter(fields.get("description", source.stem), globs) + body
        self._write_file(Path(self.path) / "rules" / f"{source.stem}{self.layout.rule_suffix}", text)

    def _published_rules(self, tool: AgentTool) -> PublishedRules:
        """What the ``@rules`` member tool publishes answers, read from its toolset."""
        return getattr(tool.toolset, tool.name)

    def _rules_front_matter(self, body: str, published: PublishedRules) -> str:
        description = next(
            (
                line.strip().replace('"', "'")
                for line in body.splitlines()
                if line.strip() and not line.strip().startswith(("#", "-", "```"))
            ),
            "Practice rules.",
        )
        applies = published.applies_to
        globs = applies.globs or ""
        if self.layout.scopes_rules_by_paths:
            return self._claude_rules_front_matter(description, globs)
        always_apply = bool(applies.always_apply)
        lines = ["---", f"alwaysApply: {'true' if always_apply else 'false'}", f'description: "{description}"']
        if globs:
            lines.append(f"globs: {globs}")
        return "\n".join([*lines, "---"]) + "\n\n"
