# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.format python
# invoke-edit: action satisfy | context.format python
# invoke-check: action validate | context.format python
"""Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."""

from __future__ import annotations

import agent_bdd.conf  # noqa: F401 - repo root on sys.path
import context_tools  # noqa: F401 - Bdd merges with BaseContextTool at import
from primitives.actions.action import agent_instructions  # noqa: F401
from context_tools.bdd.bdd import Bdd
from context_tools.base.base_context_tool import BaseContextTool


class AgentBdd(BaseContextTool):
    """# Instructions"""

    def __init__(self, format: str = "python", path: str | None = None, session: str | None = None) -> None:
        super().__init__(format=format, path=path, session=session)

    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance for writing agent BDD specs against the agent harness."""
        return super().guidance()

    def _bdd(self) -> Bdd:
        active = self.active
        sprint = active.name if active is not None else None
        path = active.path if active is not None else self._raw_path
        return Bdd(format=self.format, path=path, session=sprint)

    @agent_instructions
    def generate_output(self) -> str:
        """"""
        from generate.generate import Generate

        Generate().generate(tools=[self._bdd()])
        return ""
