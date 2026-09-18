"""Skill, command, rule, and agent marks plus markdown install."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from installation.installer import Destination, Installation


class skill(Destination):
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


class command(Destination):
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


class rules(Destination):
    flag = "_rules"

    def __new__(cls, fn: Any = None):
        inst = object.__new__(cls)
        inst.name = None
        if callable(fn):
            return inst.annotate(fn)
        return inst


class agent(Destination):
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


class agent_guidance(Destination):
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


class MarkdownInstallation(Installation):
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
        if destination == "skill":
            return Path("skills") / self._skill_folder(folder, name) / "SKILL.md"
        if destination == "command":
            base = Path("prompts") if self.ide == "VS Code" else Path("commands")
            return base / folder / f"{name}.md"
        if destination == "rules":
            return Path("rules") / folder.with_suffix(".mdc")
        return folder / str(name)

    def _skill_folder(self, folder: Path, name: str) -> Path:
        op = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name).replace("_", "-").lower()
        if op in {"instructions", "rules-markdown"}:
            return folder
        last = folder.name.replace("_", "-").lower()
        if op == last or last.startswith(op) or op.startswith(last):
            return folder
        return folder / op

    def _body_for(self, kind: str, tool: Any, toolset: Any) -> str:
        try:
            result = getattr(toolset, tool.name, None)
        except Exception:
            return tool.docstring
        if isinstance(result, str) and result.strip():
            return result.strip()
        if kind == "rules":
            format_rules = getattr(result, "format_rules", None)
            if callable(format_rules):
                return str(format_rules()).strip()
        return tool.docstring

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
        if self.mcp_mode:
            from installation.mcp.mcp_server import McpOperationDefinition

            parts.append(McpOperationDefinition.from_tool(tool).invoke_line())
        text = self.render("\n\n".join(p for p in parts if p), member, toolset)
        rel = self.relative_path(kind, toolset, member, tool.deploy_name)
        dest = self.path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
