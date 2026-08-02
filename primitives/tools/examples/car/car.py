# @toolset-manifest python -m tools manifest tools.examples.car:Car
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Example @toolset class - tools and resources only."""
from __future__ import annotations

from tools.tool import resource, tool, toolset


@toolset
class Car:
    """Operate a car — start, stop, and read current state."""

    def __init__(self, make: str, model: str, year: int, personality: str) -> None:
        """create a new car based on the description given and assign it a personality that is fun and flavorful with a unique name and a unique description"""
        self._make = make
        self._model = model
        self._year = year
        self._personality = personality
        self._running = False
        self._speed = 0.0
        super().__init__()

    @property
    @resource
    def make(self) -> str:
        """Vehicle manufacturer."""
        return self._make

    @property
    @resource
    def model(self) -> str:
        """Vehicle model name."""
        return self._model

    @property
    @resource
    def year(self) -> int:
        """Model year."""
        return self._year

    @property
    @resource
    def personality(self) -> str:
        """Character and voice of the car."""
        return self._personality

    @property
    @resource
    def running(self) -> bool:
        """Whether the engine is running."""
        return self._running

    @tool
    def start(self) -> None:
        """Start the engine."""
        self._running = True

    @tool
    def stop(self) -> None:
        """Stop the engine."""
        self._running = False
        self._speed = 0.0

    @tool
    def drive(self, miles: float) -> str:
        """Drive the given number of miles. Engine must be running."""
        if not self._running:
            return f"{self._make} {self._model} cannot drive - engine is off"
        return f"Drove {miles} miles in the {self._make} {self._model}"

    @tool
    def accelerate(self, amount: float) -> str:
        """Speed up by the given amount."""
        if not self._running:
            return f"{self._make} {self._model} cannot accelerate - engine is off"
        self._speed += amount
        return f"Accelerated to {self._speed:.0f} mph"

    @tool
    def decelerate(self, amount: float) -> str:
        """Slow down by the given amount."""
        if not self._running:
            return f"{self._make} {self._model} cannot decelerate - engine is off"
        self._speed = max(0.0, self._speed - amount)
        return f"Decelerated to {self._speed:.0f} mph"

    @tool
    def speak(self, line: str) -> str:
        """Say something in character according to personality."""
        return f'{self._make} {self._model} says: "{line}"'
