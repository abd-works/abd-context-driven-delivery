"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool
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
        """Convert already-generated content for each listed Guidance into the requested format. Returns one render result per Guidance. Pass a module:Class Guidance ref, a {toolset, fidelity} object, or a list of those. Pass source when the incoming text is not the current format."""
        self._bind_guidance(guidance)

        def on(item):
            if isinstance(item, str):
                return item
            payload = item if content in ("", None) else content
            return item.render(format, payload, source=source)

        return self.each(on)
