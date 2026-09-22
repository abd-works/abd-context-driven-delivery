"""Skill, command, rule, and agent marks plus markdown install."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from installation.destination import Destination, Installation


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
            return Path("skills") / self._skill_folder(folder, op, toolset) / "SKILL.md"
        if destination == "command":
            base = Path("prompts") if self.ide == "VS Code" else Path("commands")
            return base / folder / f"{op}.md"
        if destination == "rules":
            return Path("rules") / folder.with_suffix(".mdc")
        return folder / str(name)

    def _op_slug(self, name: str) -> str:
        return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name).replace("_", "-").lower()

    def _skill_ops(self, toolset: Any) -> list[str]:
        bag = getattr(toolset, "tools", None) or {}
        values = bag.values() if isinstance(bag, dict) else bag
        names: list[str] = []
        for tool in values:
            if not getattr(tool, "install_to_skill", False):
                continue
            names.append(self._op_slug(getattr(tool, "deploy_name", None) or tool.name))
        return names

    def _skill_folder(self, folder: Path, op: str, toolset: Any = None) -> Path:
        if getattr(toolset, "practice_guidance", None) is not None:
            slug = getattr(toolset, "slug", None)
            if slug:
                parent = folder.parent if folder.name else folder
                return parent / str(slug)
        if op in {"instructions", "rules-markdown"}:
            return folder
        last = folder.name.replace("_", "-").lower()
        if len(self._skill_ops(toolset)) > 1:
            return folder / op
        if op == last:
            return folder
        return folder / op

    def _body_for(self, kind: str, tool: Any, toolset: Any) -> str:
        if self.mcp_mode:
            return tool.docstring
        try:
            result = getattr(toolset, tool.name, None)
        except Exception:
            return tool.docstring
        if isinstance(result, str) and result.strip():
            return result.strip()
        if kind == "rules":
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
        if kind == "skill" and getattr(tool.toolset, "practice_guidance", None) is not None:
            return
        member = tool.callable
        toolset = tool.toolset
        parts = [self._body_for(kind, tool, toolset)]
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
        text = self.render("\n\n".join(p for p in parts if p), member, toolset)
        rel = self.relative_path(kind, toolset, member, tool.deploy_name)
        if kind == "rules":
            from actions.validate.rule import AppliesTo

            text = AppliesTo.strip_fence(text)
            text = self._rules_front_matter(text, toolset) + text
        elif kind == "skill":
            text = self._skill_front_matter(rel.parent.name, self._skill_overview(toolset, parts)) + text
        dest = self.path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        self.track_write(dest)

    def _skill_overview(self, toolset: Any, parts: list[str]) -> str:
        raw = getattr(toolset, "overview", None)
        source = raw.strip() if isinstance(raw, str) and raw.strip() else (parts[0] if parts else "")
        return self._without_mcp_invoke(source)

    def _without_mcp_invoke(self, text: str) -> str:
        lines = [
            line
            for line in text.splitlines()
            if not line.strip().lower().startswith("use mcp tool:")
        ]
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
        always_apply = True
        globs = ""
        if applies is not None:
            globs = getattr(applies, "globs", "") or ""
            flagged = getattr(applies, "always_apply", None)
            if flagged is not None:
                always_apply = bool(flagged)
            elif globs:
                always_apply = False
        lines = [
            "---",
            f"alwaysApply: {'true' if always_apply else 'false'}",
            f'description: "{description}"',
        ]
        if globs:
            lines.append(f"globs: {globs}")
        lines.append("---")
        return "\n".join(lines) + "\n\n"
