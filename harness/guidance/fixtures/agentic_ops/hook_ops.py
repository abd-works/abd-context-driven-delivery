"""Hook-published agent-instructions fixture."""
from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from installation.harness_files.harness_files import Skill
from installation.hooks.hooks import Hook


@agent_toolset
class SampleHookOps:
    domain_slug = "sample-hooks"

    @Hook("stop")
    @Skill
    @agent_instructions
    def auto_turn(self) -> str:
        """hook skill body for stop"""
