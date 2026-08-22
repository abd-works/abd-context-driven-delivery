# @toolset-manifest python -m tools manifest primitives.actions.agent_with_actions:AgentWithActions
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.format python
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""AgentWithActions generator - scaffold @toolset classes with @agent_instructions recipes, bdd spec, and agent bdd spec."""

from __future__ import annotations

import context_tools  # noqa: F401 - Bdd and AgentBdd merge with BaseContextTool at import
from agent_bdd.agent_bdd import AgentBdd
from context_tools.base.base_context_tool import BaseContextTool
from context_tools.bdd.bdd import Bdd

from .action import agent_instructions  # noqa: F401


class AgentWithActions(BaseContextTool):
    """# Instructions"""

    def __init__(self, format: str = "python") -> None:
        super().__init__(format=format)

    def _bdd(self) -> Bdd:
        return Bdd(format=self.format)

    def _agent_bdd(self) -> AgentBdd:
        return AgentBdd(format=self.format)

    @agent_instructions
    def generate_output(self) -> str:
        """"""
        self._bdd().generate()
        self._agent_bdd().generate()
        return ""

    @agent_instructions
    def validate(self) -> str:
        self.contexts
        self._bdd().validate()
        self._agent_bdd().validate()
        self.scan()
        return "Validation report."

    @agent_instructions
    def satisfy(self) -> str:
        self.contexts
        self.templates
        self._bdd().satisfy()
        self._agent_bdd().satisfy()
        return "When done, run validate."

    @agent_instructions
    def repair(self, asset: str, violation: str) -> str:
        self.scan()
        self.contexts
        self.examples
        self.templates
        self._bdd().satisfy()
        self._agent_bdd().satisfy()
        self.validate()
        return "Repair {{asset}} until validate passes."
