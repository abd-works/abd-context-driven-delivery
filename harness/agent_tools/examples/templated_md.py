"""Example action whose instructions use {{}} templating."""
from __future__ import annotations

from harness.agent_tools.agent_tools import agent_instructions, agent_toolset


@agent_toolset
class TemplatedMdDemo:
    """Demo toolset for md instruction templating."""

    def __init__(self, label: str) -> None:
        self.label = label

    @agent_instructions
    def greet(self, name: str) -> str:
        """Greet someone on behalf of this toolset."""
        (
            "Greet {{name}} on behalf of {{self.label}}. Keep the tone brief.\n"
            "Leave authoring markers like {Placeholder} untouched."
        )
        return f"Greeted {name}"
