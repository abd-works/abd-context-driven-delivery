"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

import inspect
from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction, load_document
from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Render(GuidanceAction):
    """Render already-generated output for provided context tools."""

    @Mcp
    @Skill
    @agent_tool
    def render(
        self,
        guidance: GuidanceArg,
        format: str,
        paths: list[str] | str,
        content: str = "",
        source: str | None = None,
    ) -> list:
        """Convert already-generated content into format. Returns one result per guidance. After the conversion returns, follow place_rendered.
        format: the target channel, such as python, markdown, or drawio.
        paths: a file, a list of files, or a folder. Required on every call. Pass paths so this action reads locally. Do not pass the document body in content on MCP.
        content: in-process text when paths is empty. Leave this empty on an MCP call.
        source: the format content is already in. Use sketch for a sketch file. Otherwise markdown, python, typescript, java, javascript, json, or drawio. md is markdown. Omit source when content is already the current format."""
        self._bind_guidance(guidance)
        loaded = load_document(content, paths)
        workspace = _workspace(paths)

        def on(item):
            if isinstance(item, str):
                return item
            payload = item if loaded in ("", None) else loaded
            if workspace and "workspace" in inspect.signature(item.render).parameters:
                return item.render(format, payload, source=source, workspace=workspace)
            return item.render(format, payload, source=source)

        converted = self.each(on)
        tools(self.act_quickly)
        tools(self.place_rendered)
        return converted

    @agent_instructions
    def place_rendered(self) -> str:
        """After render, fold the result into the module the sketch names when that module already has code. Keep the behavior that module already implements. Add the rendered operations and properties onto those types. Join behavior specs into the spec that module already has. When the sketch names no existing module, put each class in the practice model folder for that channel — `{practice}/model/{format}/`. Shared graph types stay on the harness knowledge graph. Do not replace an existing file with the rendered text. Do not re-render. Do not invent types."""
        return "Fold rendered classes into the module the sketch names, or the practice model folder when that module is new."


def _workspace(paths: list[str] | str) -> str:
    """The folder the rendered file sits in: the first path when it is a folder, else its parent."""
    first = paths[0] if isinstance(paths, (list, tuple)) and paths else paths
    if not first or not isinstance(first, str):
        return ""
    path = Path(first)
    if path.is_dir():
        return str(path)
    return str(path.parent) if path.parent.is_dir() else ""
