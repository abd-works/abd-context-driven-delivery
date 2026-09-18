"""Render — convert already-generated content on each provided context tool."""

from __future__ import annotations

from lifecycle import LifecycleAction
from harness.agent_tools.agent_tools import agent_toolset
from agent_tools.agent_tools import agent_tool
from installation.harness_files.harness_files import skill
from installation.mcp.mcp_server import mcp

@agent_toolset
class Render(LifecycleAction):
    """Render already-generated output for provided context tools."""

    @mcp
    @skill
    @agent_tool
    def render(self, tools: list, format: str, content: str = "") -> list:
        """Convert already-generated content for each listed context tool into the requested format. Returns one render result per tool."""
        self.begin(tools, action="render")
        results = []
        for tool in self.listed():
            results.append(tool.render(format, content))
        self.end()
        return results
