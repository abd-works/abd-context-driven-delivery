"""Skill, command, rule, and agent marks plus markdown install."""
from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

from primitives.installer.installer import Destination, Installation


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
    ) -> None:
        super().__init__(ide, path)
        self.destination = destination
        self.mcp_mode = mcp_mode

    def relative_path(
        self, destination: str, guidance: Any, member: Any, name: str | None = None
    ) -> Path:
        name = name or member.__name__
        slug = guidance.slug
        from primitives.agent_tools.agent_tools import AgentToolSet
        from primitives.guidance.guidance import FidelityGuidance

        fidelity_name = guidance.name
        is_fidelity = isinstance(guidance, FidelityGuidance)
        if destination == "skill":
            folder = name if isinstance(guidance, AgentToolSet) else slug
            return Path("skills") / str(folder) / "SKILL.md"
        if destination == "command":
            base = Path("prompts") if self.ide == "VS Code" else Path("commands")
            if is_fidelity and fidelity_name:
                return base / f"{slug}-{fidelity_name}.md"
            return base / f"{name}.md"
        if destination == "rules":
            return Path("rules") / f"{name}.mdc"
        return Path(str(name))

    def render(self, section: str, member: Any, tool: Any | None = None) -> str:
        body = section.rstrip()
        return f"{body}\n" if body else ""

    def render_mcp_invoke(self, toolset_ref: str, member: Any) -> str:
        name = member.__name__
        slug = toolset_ref.split(":")[-1]
        if "." in toolset_ref and ":" not in toolset_ref:
            slug = toolset_ref
        else:
            slug = slug.replace("_", "-")
        try:
            signature = inspect.signature(member)
            params = inspect.Signature(
                [p for n, p in signature.parameters.items() if n != "self"]
            )
            suffix = str(params)
        except (TypeError, ValueError):
            suffix = "()"
        return f"Use MCP tool: `{slug}.{name}{suffix}`"

    def write(self, tool: Any) -> None:
        kind = self.destination
        if tool.kind == "tool":
            if kind not in {"skill", "command", "rules"}:
                return
        if not kind:
            return
        member = tool.callable
        toolset = tool.toolset
        parts = [tool.docstring]
        if self.mcp_mode:
            parts.append(self.render_mcp_invoke(tool.slug, member))
        text = self.render("\n\n".join(p for p in parts if p), member, toolset)
        rel = self.relative_path(kind, toolset, member, tool.deploy_name)
        dest = self.path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
