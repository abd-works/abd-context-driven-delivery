# @toolset-manifest python -m tools manifest agent_bdd.agent_bdd:AgentBdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.format python
# invoke-edit: action satisfy | context.format python
# invoke-check: action validate | context.format python
"""Agent BDD generator - write agent specs against the agent() harness, composing vanilla bdd."""

from __future__ import annotations

import agent_bdd.conf  # noqa: F401 - repo root on sys.path
import context_tools  # noqa: F401 - Bdd merges with BaseContextTool at import
from primitives.actions.action import action  # noqa: F401
from context_tools.bdd.bdd import Bdd
from context_tools.base.base_context_tool import BaseContextTool


class AgentBdd(BaseContextTool):
    """# Instructions"""

    def __init__(self, format: str = "python", path: str | None = None, session: str | None = None) -> None:
        super().__init__(format=format, path=path, session=session)

    def _bdd(self) -> Bdd:
        sprint = self.active.name or None
        return Bdd(format=self.format, path=self.active.path, session=sprint)

    @action
    def generate_output(self) -> str:
        """"""
        self._bdd().generate()
        return ""

    @action
    def validate(self) -> str:
        self.contexts
        self._bdd().validate()
        self.scan()
        return "Validation report."

    @action
    def satisfy(self) -> str:
        self.contexts
        self.templates
        self._bdd().satisfy()
        return "When done, run validate."

    @action
    def repair(self, asset: str, violation: str) -> str:
        self.scan()
        self.contexts
        self.examples
        self.templates
        self._bdd().satisfy()
        self.validate()
        return "Repair {{asset}} until validate passes."
