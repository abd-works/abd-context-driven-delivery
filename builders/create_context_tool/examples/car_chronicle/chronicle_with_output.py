"""Context example - generate_output override for nested action expansion specs."""

from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions
from practices.base.base_context_tool import BaseContextTool
from harness.agent_tools.agent_tools import agent_tool


class ChronicleWithOutput(BaseContextTool):
    """# Instructions"""

    def __init__(self, path: str | None = None, session: str | None = None) -> None:
        super().__init__(path=path, session=session)

    @property
    def toolset_name(self) -> str:
        return "car_chronicle"

    @agent_instructions
    def generate_output(recipe) -> str:
        """Append each trip entry to the driving log before validating."""
        self.add_epic()
        return "Chronicle entries saved."

    @agent_tool
    def add_epic(self) -> str:
        """Add one epic block to the chronicle outline."""
        return "epic added"
