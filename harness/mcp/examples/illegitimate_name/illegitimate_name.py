"""Published MCP operation whose advertised name Cursor will not load."""
from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.mcp.mcp_server import mcp


@agent_toolset
class IllegitimateName:
    domain_slug = "bad name"

    @mcp
    @agent_tool
    def report(self) -> str:
        """Should not be enrolled — the toolset slug is not a legal MCP name."""
        return "skipped"
