# @toolset-manifest python -m tools manifest context_tools.create_context_tool.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
# invoke-new: action generate
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Context example - generate_output override for nested action expansion specs."""

from __future__ import annotations

from primitives.actions.action import agent_instructions
from context_tools.base.base_context_tool import BaseContextTool
from tools.tool import agent_tool


class ChronicleWithOutput(BaseContextTool):
    """# Instructions"""

    def __init__(self, path: str | None = None, session: str | None = None) -> None:
        super().__init__(path=path, session=session)

    @property
    def toolset_name(self) -> str:
        return "car_chronicle"

    @agent_instructions
    def generate_output(self) -> str:
        """Append each trip entry to the driving log before validating."""
        self.add_epic()
        return "Chronicle entries saved."

    @agent_tool
    def add_epic(self) -> str:
        """Add one epic block to the chronicle outline."""
        return "epic added"
