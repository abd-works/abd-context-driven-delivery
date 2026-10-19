"""Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."""

from __future__ import annotations

import agent_bdd.conf  # noqa: F401 - repo root on sys.path
from cdd_guidance.practices.bdd.bdd import Bdd
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset  # noqa: F401
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class AgentBdd(PracticeGuidance):
    """# Instructions"""

    def __init__(self, format: str = "python", path: str | None = None, session: str | None = None) -> None:
        super().__init__(format=format)
        if path is not None or session is not None:
            self._attach_workspace(path=path, session=session)

    def _bdd(self) -> Bdd:
        return Bdd(format=self.format, path=self.path, session=self.session)

    @agent_instructions
    def generate_output(self) -> str:
        """"""
        from generate.generate import Generate

        Generate().generate(guidance=[self._bdd()])
        return ""
