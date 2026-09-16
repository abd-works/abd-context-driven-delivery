"""Hook-published agent-instructions fixture."""
from __future__ import annotations

from primitives.agentic_toolset import AgenticToolset, agent_instructions, agentic_toolset
from primitives.harness.marks import hook, skill


@agentic_toolset
class SampleHookOps(AgenticToolset):
    domain_slug = "sample-hooks"

    @hook(event="stop")
    @skill
    @agent_instructions
    def auto_turn(self) -> str:
        """hook skill body for stop"""
