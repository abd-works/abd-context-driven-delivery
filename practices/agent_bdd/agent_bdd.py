"""Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."""

from __future__ import annotations

import agent_bdd.conf  # noqa: F401 - repo root on sys.path
import practices  # noqa: F401 - Bdd merges with BaseContextTool at import
from primitives.agent_tools.agent_tools import agent_instructions  # noqa: F401
from practices.bdd.bdd import Bdd
from practices.base.base_context_tool import BaseContextTool


class AgentBdd(BaseContextTool):
    """# Instructions"""

    def __init__(self, format: str = "python", path: str | None = None, session: str | None = None) -> None:
        super().__init__(format=format, path=path, session=session)

    @agent_instructions
    def guidance(recipe) -> str:
        """Provide guidance for writing agent BDD specs against the agent harness."""
        return super().guidance()

    def _bdd(self) -> Bdd:
        active = self.active
        sprint = active.name if active is not None else None
        path = active.path if active is not None else self._raw_path
        return Bdd(format=self.format, path=path, session=sprint)

    @agent_instructions
    def generate_output(recipe) -> str:
        """"""
        from generate.generate import Generate

        Generate().generate(tools=[self._bdd()])
        return ""
