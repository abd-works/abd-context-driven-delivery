"""CarStory — actions that orchestrate Car context tools for scripted trips."""
from __future__ import annotations

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, tools, instructions
from installation.files import Skill
from harness.mcp.mcp_server import Mcp

@agent_toolset
class CarStory(GuidanceAction):
    """Scripted trip actions over one or more Car context tools."""

    @Mcp
    @Skill
    @agent_instructions
    def travelTo(self, guidance: GuidanceArg, destination: str, conditions: str) -> str:
        """Scripted trip to a destination under stated conditions."""
        "Tell an interesting story about how the car gets to {destination}."
        "Conditions: {conditions}. Start the engine, then decide what to do according to personality."
        self._bind_guidance(guidance)
        for car in self.listed():
            tools(car.start())
            """Options include accelerate, decelerate, or stop - invoke as the story needs."""
            tools(car.accelerate())
            tools(car.decelerate())
            tools(car.stop())
            """Speak at intervals that make the story more interesting."""
            tools(car.speak())
        return f"Instructions for traveling to {destination}"

    @Mcp
    @Skill
    @agent_instructions
    def inspect_trip(self, guidance: GuidanceArg, plan: str) -> str:
        """Collect the trip plan into one string, call wrap_story, emit the fenced block only."""
        """Do not execute the plan — inspection output is the entire result of this invocation."""
        self._bind_guidance(guidance)
        for car in self.listed():
            tools(car.wrap_story())
        return "Trip plan inspection complete — nothing executed."
