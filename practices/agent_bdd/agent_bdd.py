"""Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."""

from __future__ import annotations

import agent_bdd.conf  # noqa: F401 - repo root on sys.path
from practices.bdd.bdd import Bdd
from practices.workspace_bind import init_practice_guidance
from primitives.agent_tools.agent_tools import agent_instructions, agent_toolset  # noqa: F401
from primitives.guidance.guidance import PracticeGuidance


@agent_toolset
class AgentBdd(PracticeGuidance):
    """# Instructions"""

    domain_slug = "agent_bdd"

    def __init__(self, format: str = "python", path: str | None = None, session: str | None = None) -> None:
        init_practice_guidance(
            self,
            format=format,
            path=path,
            session=session,
        )

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for writing agent BDD specs against the agent harness."""
        return super().guidance()

    def _bdd(self) -> Bdd:
        active = self.workspace.current_work_session if self.workspace else None
        sprint = active.name if active is not None else None
        path = active.path if active is not None else self.path
        return Bdd(format=self.format, path=path, session=sprint)

    @agent_instructions
    def generate_output(self) -> str:
        """"""
        from generate.generate import Generate

        Generate().generate(tools=[self._bdd()])
        return ""
