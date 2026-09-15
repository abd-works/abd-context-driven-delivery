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
        from generate.generate import Generate

        Generate().generate(tools=[self._bdd()])
        Generate().generate(tools=[self._agent_bdd()])
        return ""
