"""Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."""

from __future__ import annotations

from cdd_guidance.practices.bdd.bdd import Bdd
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset  # noqa: F401
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class AgentBdd(PracticeGuidance):
    """# Instructions"""

    def __init__(self, format: str = "python") -> None:
        super().__init__(format=format)

    @agent_instructions
    def generate_output(self) -> str:
        """"""
        from cdd_guidance.actions.generate.generate import Generate

        Generate(self.session).generate(guidance=[Bdd(format=self.format)])
        return ""
