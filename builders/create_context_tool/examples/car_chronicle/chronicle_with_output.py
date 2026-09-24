"""Context example - generate_output override for nested action expansion specs."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class ChronicleWithOutput(PracticeGuidance):
    """# Instructions"""

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
