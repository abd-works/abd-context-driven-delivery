"""Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."""

from __future__ import annotations

from cdd_guidance.practices.bdd.bdd import Bdd
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset, instructions
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class AgentBdd(PracticeGuidance):
    """# Instructions"""

    def __init__(self, format: str = "python") -> None:
        super().__init__(format=format)

    @agent_instructions
    def generate_output(self) -> str:
        """Write the agent specs the way vanilla BDD writes its specs at the fidelity the session works in."""
        instructions(self.bdd.instructions)
        instructions(self.bdd.generate_output)
        return ""

    @property
    def bdd(self) -> Bdd:
        """The session's own BDD practice, at the fidelity and in the format the session works in: agent specs compose
        vanilla BDD."""
        return self.session.graph.practice_of(Bdd)
