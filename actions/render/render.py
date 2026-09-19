"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools.agent_tools import agent_toolset
from agent_tools.agent_tools import agent_tool
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

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
        content: str = "",
        source: str | None = None,
    ) -> list:
        """Convert already-generated content for each listed Guidance host into the requested format. Returns one render result per host. Pass a module:Class host ref, a {toolset, fidelity} object, or a list of those. Pass source when the incoming text is not the host's current format."""
        def on(item):
            if isinstance(item, str):
                return item
            return item.render(format, content, source=source)

        return self.run(guidance, on, action="render")
