"""CreateAgentToolset — scaffold @agent_toolset classes with @agent_tool and @agent_instructions."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_toolset

from cdd_guidance.builders.builder import Builder


@agent_toolset
class CreateAgentToolset(Builder):
    """Scaffold a new agent toolset: an @agent_toolset class with @agent_tool and @agent_instructions operations."""
