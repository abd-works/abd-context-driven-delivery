"""Bare agentic toolset fixture for deploy tests."""
from __future__ import annotations

from harness.agent_tools.agent_tools import (
    agent_instructions,
    agent_tool,
    agent_toolset,
)
from installation.files import command, skill
from harness.mcp.mcp_server import mcp


@agent_toolset
class SampleAgenticOps:
    """sample agentic toolset overview"""

    domain_slug = "sample-ops"

    @skill
    @agent_instructions
    def generate(self) -> str:
        """compound generate instructions"""

    @command
    @agent_instructions
    def sketch(self) -> str:
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
class SampleMcpOps:
    domain_slug = "sample-mcp"

    @mcp
    @skill
    @agent_instructions
    def generate(self) -> str:
        """full generate instructions that must not appear in the slash file"""

    @mcp
    @command
    @agent_instructions
    def sketch(self) -> str:
        """full sketch instructions that must not appear in the slash file"""
