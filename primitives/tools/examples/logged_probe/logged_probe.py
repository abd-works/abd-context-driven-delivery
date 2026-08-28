# @toolset-manifest python -m tools manifest tools.examples.logged_probe:LoggedProbe
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
"""Minimal @toolset used by sessions specs — tools/actions with explicit SessionLog run append."""
from __future__ import annotations

from primitives.actions.action import agent_instructions, agentic_toolset
from workspace import SessionLog, summarize_mapping
from tools.tool import agent_tool


@agentic_toolset
class LoggedProbe:
    """Probe toolset for session logging specs."""

    def __init__(self) -> None:
        super().__init__()

    @agent_tool
    def ping(self, message: str) -> str:
        """Echo a message."""
        result = f"pong:{message}"
        SessionLog.instance().append(
            toolset="tools.examples.logged_probe:LoggedProbe",
            name="ping",
            summary=summarize_mapping({"message": message}),
            ok=True,
            role="run",
            payload={"request": {"message": message}, "response": {"result": result}},
        )
        return result

    @agent_tool
    def quiet(self) -> str:
        """Tool with no run append."""
        return "silent"

    @agent_instructions
    def narrate(self, message: str) -> str:
        """Narrate by pinging once."""
        self.ping(message)
        return "told"

    @agent_instructions
    def mute(self) -> str:
        """Action without a run append in the recipe."""
        self.quiet()
        return "muted"
