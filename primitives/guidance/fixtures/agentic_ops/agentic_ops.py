"""Bare agentic toolset fixture for deploy tests."""
from __future__ import annotations

from primitives.agent_tools.agent_tools import (
    AgentToolSet,
    agent_instructions,
    agent_tool,
    agent_toolset,
)
from primitives.harness.marks import command, mcp, skill


@agent_toolset
class SampleAgenticOps(AgentToolSet):
    """sample agentic toolset overview"""

    domain_slug = "sample-ops"

    @skill
    @agent_instructions
    def generate(recipe) -> str:
        """compound generate instructions"""

    @command
    @agent_instructions
    def sketch(recipe) -> str:
        """compound sketch instructions"""

    @agent_tool
    def ping(self) -> str:
        """pong"""
        return "pong"

    @skill
    @agent_tool
    def listed(self) -> str:
        """listed-tool-result"""
        return "listed-tool-result"


@agent_toolset
class SampleMcpOps(AgentToolSet):
    domain_slug = "sample-mcp"

    @mcp
    @skill
    @agent_instructions
    def generate(recipe) -> str:
        """full generate instructions that must not appear in the slash file"""

    @mcp
    @command
    @agent_instructions
    def sketch(recipe) -> str:
        """full sketch instructions that must not appear in the slash file"""
