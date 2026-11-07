"""Published MCP operation whose advertised name Cursor will not load."""
from __future__ import annotations

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from harness.mcp.mcp_server import mcp


@agent_toolset
class IllegitimateName:
    """A toolset slug is always kebab case, so only an operation's own name can make a published name illegal: Python
    accepts a letter outside ASCII in a name, and MCP clients such as Cursor refuse a tool named with one."""

    @mcp
    @agent_tool
    def résumé(self) -> str:
        """Should not be enrolled — the operation name is not a legal MCP name."""
        return "skipped"
