"""Hook-published agent-instructions fixture."""
from __future__ import annotations

from primitives.agent_tools.agent_tools import AgentToolSet, agent_instructions, agent_toolset
from primitives.harness.marks import hook, skill


@agent_toolset
class SampleHookOps(AgentToolSet):
    domain_slug = "sample-hooks"

    @hook(event="stop")
    @skill
    @agent_instructions
    def auto_turn(recipe) -> str:
        """hook skill body for stop"""
