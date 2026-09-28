"""Minimal @agent_toolset used by agent_tools specs — narrate expands to ping."""
from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset, tools


@agent_toolset
class LoggedProbe:
    """Probe toolset for instruction expansion specs."""

    @agent_tool
    def ping(self, message: str) -> str:
        """Echo a message."""
        return f"pong:{message}"

    @agent_instructions
    def narrate(self, message: str) -> str:
        """Narrate by pinging once."""
        tools(self.ping(message))
        return "told"
