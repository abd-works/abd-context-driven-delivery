"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class Render(GuidanceAction):
    """Render already-generated output for provided context tools."""

    def __init__(self, path: str = ".", session: str = "") -> None:
        self.path = path
        self._session_name = session
        self._guidance_text: str | None = None
        self._tool_items: list = []
        self.workspace = None

    @Mcp
    @Skill
    @agent_tool
    def render(
        self,
        guidance: GuidanceArg,
        format: str,
        content: str = "",
        source: str | None = None,
    ) -> list:
        """Convert already-generated content for each listed Guidance into the requested format. Returns one render result per Guidance. Pass a module:Class Guidance ref, a {toolset, fidelity} object, or a list of those. Pass source when the incoming text is not the current format. After the conversion returns, follow place_rendered."""
        self._bind_guidance(guidance)

        def on(item):
            if isinstance(item, str):
                return item
            payload = item if content in ("", None) else content
            return item.render(format, payload, source=source)

        converted = self.each(on)
        tools(self.place_rendered)
        return converted

    @agent_instructions
    def place_rendered(self) -> str:
        """After render, do an AI pass on the written files. Put each class in the practice model folder for that channel — `{practice}/model/{format}/`, the same layout as json, markdown, and codeql. Shared graph types stay on the harness knowledge graph. Small nips and tucks only: names, bases, constructors, imports, and file splits so the tree follows the architecture and the sketch intent. Do not re-render. Do not invent types."""
        return "Place rendered classes in the channel packages and tidy to the architecture."
