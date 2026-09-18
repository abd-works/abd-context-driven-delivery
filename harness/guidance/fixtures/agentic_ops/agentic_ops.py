"""Bare agentic toolset fixture for deploy tests."""
from __future__ import annotations

from harness.agent_tools.agent_tools import (
    agent_instructions,
    agent_tool,
    agent_toolset,
)
from installation.harness_files.harness_files import Command, Skill
from installation.mcp.mcp_server import Mcp


@agent_toolset
class SampleAgenticOps:
    """sample agentic toolset overview"""

    domain_slug = "sample-ops"

    @Skill
    @agent_instructions
    def generate(self) -> str:
        """compound generate instructions"""

    @Command
    @agent_instructions
    def sketch(self) -> str:
        """compound sketch instructions"""

    @agent_tool
    def ping(self) -> str:
        """pong"""
        return "pong"

    @Skill
    @agent_tool
    def listed(self) -> str:
        """listed-tool-result"""
        return "listed-tool-result"


@agent_toolset
class SampleMcpOps:
    domain_slug = "sample-mcp"

    @Mcp
    @Skill
    @agent_instructions
    def generate(self) -> str:
        """full generate instructions that must not appear in the slash file"""

    @Mcp
    @Command
    @agent_instructions
    def sketch(self) -> str:
        """full sketch instructions that must not appear in the slash file"""
