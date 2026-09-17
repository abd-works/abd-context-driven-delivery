"""Canonical AgentToolSet shape — matching-by example for CreateAgentToolset."""
from __future__ import annotations

from agent_tools import agent_instructions, agent_tool, agent_toolset, tools


@agent_toolset
class Car:
    """Operate a car — start, stop, and narrate a short trip."""

    def __init__(self, make: str, model: str, year: int, personality: str) -> None:
        """Create the car and give it a distinct personality."""
        self._make = make
        self._model = model
        self._year = year
        self._personality = personality
        self._running = False
        super().__init__()

    @property
    def make(self) -> str:
        """Vehicle manufacturer."""
        return self._make

    @property
    def running(self) -> bool:
        """Whether the engine is running."""
        return self._running

    @agent_tool
    def start(self) -> None:
        """Start the engine."""
        self._running = True

    @agent_tool
    def stop(self) -> None:
        """Stop the engine."""
        self._running = False

    @agent_tool
    def speak(self, line: str) -> str:
        """Say something in character."""
        return f'{self._make} {self._model} says: "{line}"'

    @agent_instructions
    def travel_to(recipe, destination: str) -> str:
        """Drive to {destination} in character."""
        """Start, speak as the trip needs, then stop."""
        tools(recipe.toolset.start())
        tools(recipe.toolset.speak())
        tools(recipe.toolset.stop())
        return "Instructions for traveling to {{destination}}"
