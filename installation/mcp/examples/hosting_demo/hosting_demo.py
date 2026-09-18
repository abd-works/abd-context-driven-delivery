"""Hosting demo toolset for MCP host specs."""
from __future__ import annotations

from typing import TypedDict

from harness.agent_tools.agent_tools import agent_tool, agent_toolset
from installation.mcp.mcp_server import Mcp


class PlanWorkResult(TypedDict):
    concept: str
    count: int


class OrchestrateResult(TypedDict):
    plain: str
    count: int


@agent_toolset
class HostingDemo:
    """Small toolset hosting AI tools and agent guidance for MCP specs."""

    def __init__(self) -> None:
        self._count = 0
        super().__init__()

    @Mcp
    @agent_tool
    def increment(self, step: int = 1) -> int:
        """Increase the running count."""
        self._count += int(step)
        return self._count

    @Mcp
    @agent_tool
    def read_count(self) -> int:
        """Return the current count."""
        return self._count

    def _ordinary_helper(self) -> str:
        return "plain-result"

    @Mcp
    @agent_tool
    def plan_work(self, concept: str) -> PlanWorkResult:
        """Think about the concept before acting."""
        count = self.increment(step=2)
        return {"concept": concept, "count": int(count)}

    @Mcp
    @agent_tool
    def guidance_only(self) -> str:
        """Guidance with no orchestrated AI tools."""
        return "guidance-text"

    @Mcp
    @agent_tool
    def orchestrate_with_plain(self) -> OrchestrateResult:
        """Mix explicit AI tool use with ordinary code."""
        plain = self._ordinary_helper()
        count = self.increment(step=1)
        return {"plain": plain, "count": int(count)}
