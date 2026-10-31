"""Skill, command, rule, and agent marks plus markdown install."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

from harness.installation.destination import Destination, Installation


class Skill(Destination):
    flag = "_skill"

    def __new__(cls, fn: Any = None, name: str | None = None):
        inst = object.__new__(cls)
        if isinstance(fn, str):
            inst.name = fn
            return inst
        inst.name = name
        if callable(fn):
            return inst.annotate(fn)
        return inst


class Command(Destination):
    flag = "_command"

    def __new__(cls, fn: Any = None, name: str | None = None):
        inst = object.__new__(cls)
        if isinstance(fn, str):
            inst.name = fn
            return inst
        inst.name = name
        if callable(fn):
            return inst.annotate(fn)
        return inst


class Rules(Destination):
    flag = "_rules"

    def __new__(cls, fn: Any = None):
        inst = object.__new__(cls)
        inst.name = None
        if callable(fn):
            return inst.annotate(fn)
        return inst


class Agent(Destination):
    flag = "_agent"

    def __new__(cls, fn: Any = None, name: str | None = None):
        inst = object.__new__(cls)
        if isinstance(fn, str):
            inst.name = fn
            return inst
        inst.name = name
        if callable(fn):
            return inst.annotate(fn)
        return inst


class AgentGuidance(Destination):
    flag = "_agent_guidance"

    def __new__(cls, fn: Any = None, name: str | None = None):
        inst = object.__new__(cls)
        if isinstance(fn, str):
            inst.name = fn
            return inst
        inst.name = name
        if callable(fn):
            return inst.annotate(fn)
        return inst


skill = Skill
command = Command
rules = Rules
agent = Agent
agent_guidance = AgentGuidance


class FileInstallation(Installation):
    """Write skill, command, and rules markdown files."""

    channel = "markdown"

    def __init__(
        self,
        ide: str,
        path: Path | str,
        destination: str = "",
        mcp_mode: bool = False,
        repo: Path | str | None = None,
    ) -> None:
        super().__init__(ide, path, repo=repo)
        self.destination = destination
        self.mcp_mode = mcp_mode

    def relative_path(
        self, destination: str, toolset: Any, member: Any, name: str | None = None
    ) -> Path:
        name = name or getattr(member, "__name__", "tool")
        folder = self.folder_for(toolset)
        op = self._op_slug(name)
        if destination == "skill":
            skill_folder = self._skill_folder(toolset, op)
            if self.ide == "Claude":
                skill_folder = self._flat_skill_folder(skill_folder)
            return Path("skills") / skill_folder / "SKILL.md"
        if destination == "command":
            base = Path("prompts") if self.ide == "VS Code" else Path("commands")
            return base / self._command_folder(toolset, folder) / f"{self._command_stem(toolset, op)}.md"
        if destination == "rules":
            suffix = ".md" if self.ide == "Claude" else ".mdc"
            kebab = self._kebab_folder(folder)
            if getattr(toolset, "practice_guidance", None) is not None:
                slug = getattr(toolset, "slug", None)
                stem = self._op_slug(str(slug)) if slug else self._command_stem(toolset, kebab.name)
                parent = kebab.parent if kebab.name else kebab
                return Path("rules") / parent / f"{stem}{suffix}"
            return Path("rules") / kebab.with_suffix(suffix)
        return folder / str(name)

    def _flat_skill_folder(self, folder: Path) -> Path:
        """Claude Code only discovers ``skills/<name>/SKILL.md``, so nested folders join into one name."""
        parts = [part for part in folder.parts if part not in {".", "/", "\\"}]
        return Path("-".join(parts) or "toolset")

    def _op_slug(self, name: str) -> str:
        return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name).replace("_", "-").lower()

    def _kebab_folder(self, folder: Path) -> Path:
        parts: list[str] = []
        for part in folder.parts:
            if part in {"/", "\\"} or (len(part) == 2 and part.endswith(":")):
                parts.append(part)
            else:
                parts.append(self._op_slug(part))
        return Path(*parts) if parts else folder

    def _command_folder(self, toolset: Any, folder: Path) -> Path:
        kebab = self._kebab_folder(folder)
        if getattr(toolset, "practice_guidance", None) is not None:
            return kebab.parent if kebab.name else kebab
        return kebab

    def _command_stem(self, toolset: Any, op: str) -> str:
        if getattr(toolset, "practice_guidance", None) is not None and op in {"instructions", "rules-markdown"}:
            slug = getattr(toolset, "slug", None)
            if slug:
                return self._op_slug(str(slug))
        if getattr(toolset, "practice_guidance", None) is not None:
            slug = getattr(toolset, "slug", None)
            if slug:
                return f"{self._op_slug(str(slug))}-{op}"
        return op

    def _skill_ops(self, toolset: Any) -> list[str]:
        bag = getattr(toolset, "tools", None) or {}
        values = bag.values() if isinstance(bag, dict) else bag
        names: list[str] = []
        for tool in values:
            if not getattr(tool, "install_to_skill", False):
                continue
            names.append(self._op_slug(getattr(tool, "deploy_name", None) or tool.name))
        return names

    def _skill_folder(self, toolset: Any, op: str) -> Path:
        folder = self._kebab_folder(self.folder_for(toolset))
        if getattr(toolset, "practice_guidance", None) is not None:
            slug = getattr(toolset, "slug", None)
            if slug:
                parent = folder.parent if folder.name else folder
                leaf = parent / self._op_slug(str(slug))
                if op in {"instructions", "rules-markdown"}:
                    return leaf
                if len(self._skill_ops(toolset)) > 1:
                    return leaf / op
                return leaf
        if op in {"instructions", "rules-markdown"}:
            return folder
        last = folder.name
        if len(self._skill_ops(toolset)) > 1:
            return folder / op
        if op == last:
            return folder
        return folder / op

    def _schema_guide(self, tool: Any, toolset: Any) -> str:
        """Practice schema joined into instructions, including a fidelity skill."""
        if getattr(tool, "name", "") != "instructions":
            return ""
        guide = getattr(toolset, "schema_guide", None)
        if not callable(guide):
            practice = getattr(toolset, "practice_guidance", None)
            guide = getattr(practice, "schema_guide", None) if practice is not None else None
        if not callable(guide):
            return ""
        return (guide() or "").strip()

    def _instructions_at_install(self, tool: Any, toolset: Any) -> str:
        """Expand ``@agent_instructions`` on the live toolset when writing slash markdown."""
        try:
            value = getattr(toolset, tool.name)
        except Exception:
            value = None
        if isinstance(value, str) and value.strip():
            return value.strip()
        return tool.docstring

    def _body_for(self, kind: str, tool: Any, toolset: Any) -> str:
        if self.mcp_mode:
            # An ``"""overview"""`` docstring names the section the MCP tool returns; it is not body text.
            return "" if tool.docstring.strip() == "overview" else tool.docstring
        if tool.kind == "instructions":
            return self._instructions_at_install(tool, toolset)
        if kind == "rules":
            result = getattr(toolset, tool.name, None)
            markdown = getattr(result, "markdown", None)
            if isinstance(markdown, str) and markdown.strip():
                return markdown.strip()
            format_rules = getattr(result, "format_rules", None)
            if callable(format_rules):
                return str(format_rules()).strip()
        return tool.docstring

    def _fidelity_one_liner(self, child: Any) -> str:
        name = getattr(child, "name", "") or ""
        overview = (getattr(child, "overview", None) or "").strip()
        summary = ""
        for line in overview.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("**"):
                summary = stripped
                break
        return f"{name} — {summary}" if summary else name

    def _repo_script_command(self, deploy_name: str) -> str | None:
        root = self.repo
        if root is None:
            return None
        script = root / "scripts" / f"{deploy_name}.py"
        if script.is_file():
            return f'python "{script.resolve()}"'
        return None

    def _shell_python_c(self, tool: Any) -> str:
        toolset = tool.toolset
        cls = type(toolset)
        ref = f"{cls.__module__}:{cls.__name__}"
        method = tool.name
        call = f'AgentToolSet.instantiate("{ref}").{method}()'
        code = (
            "from harness.agent_tools.agent_tools import AgentToolSet; "
            f"print({call})"
        )
        escaped = code.replace("\\", "\\\\").replace('"', '\\"')
        return f'python -c "{escaped}"'

    def _shell_command(self, tool: Any) -> str:
        scripted = self._repo_script_command(tool.deploy_name)
        if scripted is not None:
            return scripted
        return self._shell_python_c(tool)

    def _needs_shell_invoke(self, tool: Any, kind: str) -> bool:
        """``@agent_tool`` on skill/command without ``@mcp`` gets a Shell/python tail."""
        if kind not in {"skill", "command"}:
            return False
        if tool.kind != "tool":
            return False
        return not tool.install_to_mcp

    def _shell_invoke_line(self, tool: Any) -> str:
        command = self._shell_command(tool)
        return (
            "Run from the repository root with the Shell tool:\n\n"
            f"```text\n{command}\n```"
        )

    def _fidelity_invoke_parts(self, toolset: Any) -> list[str]:
        entries = getattr(getattr(toolset, "fidelities", None), "entries", None) or {}
        parts: list[str] = []
        for _name, child in entries.items():
            member = getattr(type(child), "instructions", None)
            getter = getattr(member, "fget", member)
            invoke = (
                f"Use MCP tool: `{getattr(child, 'slug', '')}()`"
                if getattr(getter, "_mcp", False)
                else ""
            )
            parts.append(
                "\n\n".join(piece for piece in (self._fidelity_one_liner(child), invoke) if piece)
            )
        return parts

    def render(self, section: str, member: Any, tool: Any | None = None) -> str:
        body = section.rstrip()
        return f"{body}\n" if body else ""

    def write(self, tool: Any) -> None:
        kind = self.destination
        if tool.kind == "tool":
            if kind not in {"skill", "command", "rules"}:
                return
        if not kind:
            return
        member = tool.callable
        toolset = tool.toolset
        parts = [self._body_for(kind, tool, toolset)]
        schema = self._schema_guide(tool, toolset)
        if schema and schema not in parts[0]:
            parts.append(schema)
        if self.mcp_mode:
            from harness.mcp.mcp_server import McpOperationDefinition

            fidelity_parts = (
                self._fidelity_invoke_parts(toolset)
                if tool.name == "instructions"
                else []
            )
            if fidelity_parts:
                parts.extend(fidelity_parts)
            else:
                parts.append(McpOperationDefinition.from_tool(tool).invoke_line())
        elif self._needs_shell_invoke(tool, kind):
            parts.append(self._shell_invoke_line(tool))
        text = self.render("\n\n".join(p for p in parts if p), member, toolset)
        rel = self.relative_path(kind, toolset, member, tool.deploy_name)
        if kind == "rules":
            from harness.guidance.rule import AppliesTo

            text = AppliesTo.strip_fence(text)
            text = self._rules_front_matter(text, toolset) + text
        elif kind == "skill":
            text = self._skill_front_matter(rel.parent.name, self._skill_overview(toolset, parts)) + text
        dest = self.path / rel
        text = self._with_installed_references(text, dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        self.track_write(dest)

    _REFERENCE_LINK = re.compile(r"\]\((?:\.\./)+references/([\w.-]+\.md)\)")
    _RULE_FILE_NAME = re.compile(r"`(practices/[\w/.-]+)\.mdc`")

    def _with_installed_references(self, text: str, dest: Path) -> str:
        """Point links into ``cdd_guidance/references`` at the copy in ``<ide>/references``, and name
        rule files with this IDE's extension."""
        text = self._REFERENCE_LINK.sub(lambda match: f"]({self._install_reference(match.group(1), dest)})", text)
        if self.ide == "Claude":
            text = self._RULE_FILE_NAME.sub(r"`\1.md`", text)
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
            if stripped.startswith("use mcp tool:"):
                continue
            if stripped.startswith("run from the repository root with the shell tool:"):
                skip_shell_block = True
                continue
            if skip_shell_block:
                if stripped.startswith("```"):
                    skip_shell_block = False
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    def _skill_front_matter(self, name: str, overview: str) -> str:
        description = overview.strip() or name
        return f"---\nname: {name}\n{self._folded_yaml_field('description', description)}---\n\n"

    def _folded_yaml_field(self, key: str, value: str) -> str:
        indented = "\n".join(f"  {line}" if line else "  " for line in value.splitlines())
        return f"{key}: >-\n{indented}\n"

    def _rules_front_matter(self, body: str, toolset: Any = None) -> str:
        description = "Practice rules."
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("-"):
                continue
            if stripped.startswith("```"):
                continue
            description = stripped.replace('"', "'")
            break
        applies = getattr(getattr(toolset, "rules", None), "appliesTo", None)
        always_apply = False
        globs = ""
        if applies is not None:
            globs = getattr(applies, "globs", "") or ""
            flagged = getattr(applies, "always_apply", None)
            if flagged is not None:
                always_apply = bool(flagged)
        if self.ide == "Claude":
            return self._claude_rules_front_matter(description, globs)
        lines = [
            "---",
            f"alwaysApply: {'true' if always_apply else 'false'}",
            f'description: "{description}"',
        ]
        if globs:
            lines.append(f"globs: {globs}")
        lines.append("---")
        return "\n".join(lines) + "\n\n"

    def _claude_rules_front_matter(self, description: str, globs: str) -> str:
        """Claude Code rules scope by ``paths``; a rule without paths loads in every session."""
        lines = ["---", f'description: "{description}"']
        patterns = [item.strip() for item in globs.split(",") if item.strip()]
        if patterns:
            lines.append("paths:")
            lines.extend(f'  - "{pattern}"' for pattern in patterns)
        lines.append("---")
        return "\n".join(lines) + "\n\n"
