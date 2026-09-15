"""Example action whose instructions load from an md file with {{}} templating."""
from __future__ import annotations

from primitives.actions.action import agent_instructions, agentic_toolset


@agentic_toolset
class TemplatedMdDemo:
    """Demo toolset for md instruction templating."""

    def __init__(self, label: str) -> None:
        self.label = label
        super().__init__()

    @agent_instructions
    def greet(self, name: str) -> str:
        """greet_instructions"""
        return f"Greeted {name}"
