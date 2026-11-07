"""ChronicleWithOutput — a practice that overrides generate_output with a recipe calling its own tool."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.guidance.guidance import PracticeGuidance


@agent_toolset
class ChronicleWithOutput(PracticeGuidance):
    """A driving chronicle whose generate appends each trip to the driving log."""

    @agent_instructions
    def generate_output(self) -> str:
        """Append each trip entry to the driving log before validating."""
        tools(self.add_epic)
        return "Chronicle entries saved."

    @agent_tool
    def add_epic(self) -> str:
        """Add one epic block to the chronicle outline."""
        return "epic added"
