"""Hosting demo toolset for mcp-server BDD specs."""
from __future__ import annotations

from mcp_server import mcp_instruction, tool
from tools.tool import agent_tool, toolset


@toolset
class HostingDemo:
    """Small toolset hosting AI tools and agent guidance for MCP specs."""

    TOOLSET_SLUG = "hosting_demo"

    def __init__(self) -> None:
        self._count = 0
        super().__init__()

    @agent_tool
    def increment(self, step: int = 1) -> int:
        """Increase the running count."""
        self._count += int(step)
        return self._count

    @agent_tool
    def read_count(self) -> int:
        """Return the current count."""
        return self._count

    def _ordinary_helper(self) -> str:
        return "plain-result"

    @mcp_instruction
    def plan_work(self, concept: str) -> dict[str, object]:
        """Think about the concept before acting."""
        count = tool(self.increment, step=2)
        return {"concept": concept, "count": count}

    @mcp_instruction
    def guidance_only(self) -> str:
        """Guidance with no orchestrated AI tools."""
        return "guidance-text"

    @mcp_instruction
    def orchestrate_with_plain(self) -> dict[str, object]:
        """Mix explicit AI tool use with ordinary code."""
        plain = self._ordinary_helper()
        count = tool(self.increment, step=1)
        return {"plain": plain, "count": count}
