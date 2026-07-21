# @toolset-manifest python -m tools manifest generator.examples.car_chronicle.chronicle_with_output:ChronicleWithOutput
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate
"""Generator example — generate_output override for nested action expansion specs."""

from __future__ import annotations

from agents.action import action
from generator import generator  # noqa: F401
from tools.tool import tool


@generator
class ChronicleWithOutput:
    """§ Instructions"""

    def __init__(self) -> None:
        super().__init__()

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
