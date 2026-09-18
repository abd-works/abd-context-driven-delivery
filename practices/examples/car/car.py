"""Car — example context tool for in-character road stories and vehicle tools."""
from __future__ import annotations

from practices.stages import DISCOVERY, ENGINEER, SPEC, resolve_stage_fidelity
from practices.workspace_bind import init_practice_guidance
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import Skill
from installation.mcp.mcp_server import Mcp
from agent_tools.agent_tools import agent_tool

_TRIP_HEADER = "===== TRIP LOG (read only) ====="
_TRIP_FOOTER = "===== END TRIP LOG ====="

_FIDELITY_FORMAT_DEFAULTS = {
    "trip_outline": "markdown",
    "road_story": "markdown",
    "full_journey": "markdown",
}

@agent_toolset
class Car(PracticeGuidance):
    """# Instructions

    Example context tool — qualitative guidance for in-character driving stories,
    plus vehicle tools agents invoke while narrating.
    """

    domain_slug = "car"
    default_workspace_folder: str = "."
    context_index_key: str = "car"
    _fidelity_format_defaults = dict(_FIDELITY_FORMAT_DEFAULTS)
    supported_formats = frozenset({"markdown"})

    STAGE_TO_FIDELITY = {
        DISCOVERY: "trip_outline",
        SPEC: "road_story",
        ENGINEER: "full_journey",
    }

    @classmethod
    def resolve_fidelity(cls, fidelity: str) -> str:
        return resolve_stage_fidelity(fidelity, cls.STAGE_TO_FIDELITY)

    def __init__(
        self,
        fidelity: str = "road_story",
        make: str = "Dodge",
        model: str = "Charger",
        year: int = 1969,
        personality: str = "loyal",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        fidelity = type(self).resolve_fidelity(fidelity)
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. "
                f"Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        init_practice_guidance(
            self,
            format=resolved_format,
            path=path,
            session=session,
            workspace=workspace,
            fidelity=fidelity,
            stage_to_fidelity=self.STAGE_TO_FIDELITY,
        )
        self._make = make
        self._model = model
        self._year = year
        self._personality = personality
        self._running = False
        self._speed = 0.0

    @property
    def make(self) -> str:
        """Vehicle manufacturer."""
        return self._make

    @property
    def model(self) -> str:
        """Vehicle model name."""
        return self._model

    @property
    def year(self) -> int:
        """Model year."""
        return self._year

    @property
    def personality(self) -> str:
        """Character and voice of the car."""
        return self._personality

    @property
    def running(self) -> bool:
        """Whether the engine is running."""
        return self._running

    @property
    @Mcp
    @Skill
    @agent_instructions
    def instructions(self) -> str:
        """Provide guidance for in-character road stories at the current fidelity.
        At trip_outline fidelity: write bullet beats only — destination, conditions, tool order.
        At road_story fidelity: write full prose with start, drive, speak, and stop woven in.
        At full_journey fidelity: write prose and call wrap_story when a trip log is needed for inspection.
        Every tool call uses this toolset with context make, model, year, and personality.
        When the story needs a scripted trip, call travelTo on the CarStory companion and pass this Car as a tool argument."""
        return super().instructions

    @property
    @agent_instructions
    def guidance(self) -> str:
        """Expand this practice's Guidance section."""
        super().guidance
        return (
            "When the story needs a scripted trip, call travelTo on the CarStory companion "
            "and pass this Car as a tool argument. Do not inline vehicle tools into prose."
        )

    @agent_instructions
    def generate(self) -> str:
        """Generate the road-story artifact for the current fidelity."""
        return self.generate_output()

    @agent_instructions
    def generate_output(self) -> str:
        """Write the artifact for the active fidelity — outline, prose, or full journey."""
        if self.fidelity == "trip_outline":
            return "Write bullet beats: destination, conditions, start, drive, speak, stop."
        if self.fidelity == "road_story":
            return "Write full in-character prose; invoke vehicle tools as the story needs."
        return "Write full journey prose; use wrap_story when inspection output is required."

    @agent_tool
    def start(self) -> None:
        """Start the engine."""
        self._running = True

    @agent_tool
    def stop(self) -> None:
        """Stop the engine."""
        self._running = False
        self._speed = 0.0

    @agent_tool
    def drive(self, miles: float) -> str:
        """Drive the given number of miles. Engine must be running."""
        if not self._running:
            return f"{self._make} {self._model} cannot drive - engine is off"
        return f"Drove {miles} miles in the {self._make} {self._model}"

    @agent_tool
    def accelerate(self, amount: float) -> str:
        """Speed up by the given amount."""
        if not self._running:
            return f"{self._make} {self._model} cannot accelerate - engine is off"
        self._speed += amount
        return f"Accelerated to {self._speed:.0f} mph"

    @agent_tool
    def decelerate(self, amount: float) -> str:
        """Slow down by the given amount."""
        if not self._running:
            return f"{self._make} {self._model} cannot decelerate - engine is off"
        self._speed = max(0.0, self._speed - amount)
        return f"Decelerated to {self._speed:.0f} mph"

    @agent_tool
    def speak(self, line: str) -> str:
        """Say something in character according to personality."""
        return f'{self._make} {self._model} says: "{line}"'

    @agent_tool
    def wrap_story(self, body: str) -> str:
        """Wrap {body} in trip-log fences for inspection."""
        return f"{_TRIP_HEADER}\n{body}\n{_TRIP_FOOTER}"
