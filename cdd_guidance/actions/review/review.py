"""Review — record a person's approval of each listed guidance at its current fidelity."""

from __future__ import annotations

from harness.agent_tools import agent_instructions, agent_toolset
from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.installation.files import Command


@agent_toolset
class Review(GuidanceAction):
    """Record that a person has reviewed and approved guidance."""

    @Command
    @agent_instructions
    def review(self, guidance: GuidanceArg) -> str:
        """Record that a person has reviewed and approved each listed guidance at its current fidelity. Run this only when the person says the artifact is approved; the session board counts the fidelity done once its Validate has passed and this review follows.

        guidance: the slugs you type, such as stories, clean-engineering-model, or bdd-behavior."""
        self.run(guidance, self._approve, action="review")
        return "Review recorded."

    def _approve(self, item) -> None:
        return None
