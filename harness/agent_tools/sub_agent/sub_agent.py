"""Sub-agent — launch non-blocking sub-agents with custom instructions."""
from __future__ import annotations

from harness.agent_tools import agent_instructions, agent_toolset
from harness.agent_tools.sub_agent.mark import SUB_AGENT_CALLER_PREAMBLE
from harness.mcp.mcp_server import mcp
from installation.files import skill


@agent_toolset
class SubAgent:
    """Launch a non-blocking sub-agent with custom instructions.

    Hand work to a background sub-agent and continue the current conversation
    without waiting for completion.
    """

    domain_slug = "sub-agent"

    @mcp
    @skill(name="sub-agent")
    @agent_instructions
    def sub_agent(self, instructions: str, summary: str = "") -> str:
        """Delegate {{summary}} using the sub-agent skill.

        Do not call this MCP tool from inside the sub-agent.
        """
        SUB_AGENT_CALLER_PREAMBLE
        "{{instructions}}"
        return "Launched sub-agent: {{summary}}"
