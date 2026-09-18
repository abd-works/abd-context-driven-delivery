"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from lifecycle import GuidanceArg, LifecycleAction
from harness.agent_tools.agent_tools import agent_toolset
from agent_tools.agent_tools import agent_tool
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp

@agent_toolset
class Render(LifecycleAction):
    """Render already-generated output for provided context tools."""

    @Mcp
    @Skill
    @agent_tool
    def render(self, guidance: GuidanceArg, format: str, content: str = "") -> list:
        """Convert already-generated content for each listed Guidance host into the requested format. Returns one render result per host. Pass a string to render that text once."""
        def on(item):
            if isinstance(item, str):
                return item
            return item.render(format, content)

        return self.run(guidance, on, action="render")
