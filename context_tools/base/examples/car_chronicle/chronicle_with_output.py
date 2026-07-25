# @toolset-manifest python -m tools manifest context_tools.base.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate
"""Context example — generate_output override for nested action expansion specs."""

from __future__ import annotations

from primitives.actions.action import action
from context_tools import context_tool  # noqa: F401
from tools.tool import tool


@context_tool
class ChronicleWithOutput:
    """§ Instructions"""

    def __init__(self, path: str | None = None, session: str | None = None) -> None:
        super().__init__(path=path, session=session)

    @property
    def toolset_name(self) -> str:
        return "car_chronicle"

    @action
    def generate_output(self) -> str:
        """Append each trip entry to the driving log before validating."""
        self.add_epic()
        return "Chronicle entries saved."

    @tool
    def add_epic(self) -> str:
        """Add one epic block to the chronicle outline."""
        return "epic added"
