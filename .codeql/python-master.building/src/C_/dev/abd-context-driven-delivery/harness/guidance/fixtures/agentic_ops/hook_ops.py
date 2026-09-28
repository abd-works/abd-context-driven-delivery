"""Hook-published agent-instructions fixture."""
from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from installation.files import skill
from harness.hooks.hooks import hook


@agent_toolset
class SampleHookOps:
    domain_slug = "sample-hooks"

    @hook("stop")
    @skill
    @agent_instructions
    def auto_turn(self) -> str:
        """hook skill body for stop"""
