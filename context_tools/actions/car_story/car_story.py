# @toolset-manifest python -m tools manifest car_story.car_story:CarStory
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""CarStory — actions that orchestrate Car context tools for scripted trips."""
from __future__ import annotations

from harness.harness_tool import prompt
from lifecycle import LifecycleAction
from primitives.actions.action import agent_instructions, agentic_toolset


@agentic_toolset
class CarStory(LifecycleAction):
    """Scripted trip actions over one or more Car context tools."""

    @prompt(name="travel-to")
    @agent_instructions
    def travelTo(self, tools: list, destination: str, conditions: str) -> str:
        """Tell an interesting story about how the car gets to {destination}."""
        """Conditions: {conditions}. Start the engine, then decide what to do according to personality."""
        for car in self.context_tools(tools):
            car.start()
            """Options include accelerate, decelerate, or stop - invoke as the story needs."""
            car.accelerate()
            car.decelerate()
            car.stop()
            """Speak at intervals that make the story more interesting."""
            car.speak()
        return f"Instructions for traveling to {destination}"

    @prompt(name="car-inspect")
    @agent_instructions
    def inspect_trip(self, tools: list, plan: str) -> str:
        """Collect the trip plan into one string, call wrap_story, emit the fenced block only."""
        """Do not execute the plan — inspection output is the entire result of this invocation."""
        for car in self.context_tools(tools):
            car.wrap_story()
        return "Trip plan inspection complete — nothing executed."
