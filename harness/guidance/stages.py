"""The stages of the CDD approach: Discovery, Specification, and Implementation.

Each fidelity names its stage in its practice markdown as **Stage:**. The session board, the chat bar, and the catalog
draw the stages from here, so a stage's order, scope, and actions are written once.
"""

from __future__ import annotations

from harness.installation.data_class import data_field

DISCOVERY: str = "discovery"
SPECIFICATION: str = "specification"
IMPLEMENTATION: str = "implementation"

class StageScope:
    """How much of the solution a stage's work covers, drawn as a shape that narrows and deepens along the board:
    Discovery takes in the whole solution wide and shallow, Implementation one story narrow and deep."""

    def __init__(self, shape: str, name: str, reach: str, covers: str = "") -> None:
        self._shape = shape
        self._name = name
        self._reach = reach
        # What its work decides, such as `outcomes · scope · boundaries`; a scope made without it decides nothing it
        # names.
        self._covers = covers

    @property
    @data_field
    def shape(self) -> str:
        """The shape the board draws, such as `solution`, `sprint`, or `story`."""
        return self._shape

    @property
    @data_field
    def name(self) -> str:
        """What the stage's work takes in, such as `Whole solution`."""
        return self._name

    @property
    @data_field
    def reach(self) -> str:
        """How wide and deep the work goes, such as `wide / shallow`."""
        return self._reach

    @property
    @data_field
    def covers(self) -> str:
        """What the work decides, such as `outcomes · scope · boundaries`."""
        return self._covers


class ApproachStage:
    """One stage of the CDD approach: the name each fidelity's **Stage:** gives it, its title, and its scope. The actions
    a person runs on a fidelity are the same in every stage, so the action catalogue answers them (``ACTION_CATALOGUE``:
    ``steps``, ``on_fidelities``, ``producing``, ``taking_formats``). The session board's stage columns and the catalog's
    columns are each built on one."""

    def __init__(self, name: str, scope: StageScope) -> None:
        self._name = name
        self._scope = scope

    @property
    @data_field
    def name(self) -> str:
        """The stage as a fidelity's **Stage:** names it, such as `discovery`."""
        return self._name

    @property
    @data_field
    def title(self) -> str:
        """The stage as a board heads its column, such as `Discovery`."""
        return self._name.capitalize()

    @property
    @data_field
    def scope(self) -> StageScope:
        return self._scope


class ApproachStages:
    """The stages in the order the approach walks them; the one place a stage's name meets its scope and actions."""

    def __init__(self, stages: tuple[ApproachStage, ...]) -> None:
        self._stages = stages

    def __iter__(self):
        return iter(self._stages)

    def __len__(self) -> int:
        return len(self._stages)

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(stage.name for stage in self._stages)

    def of(self, name: str) -> ApproachStage | None:
        """The stage a fidelity's **Stage:** names, such as `discovery`; none for a name that is no stage."""
        return next((stage for stage in self._stages if stage.name == name), None)


STAGES = ApproachStages((
    ApproachStage(DISCOVERY, StageScope("solution", "Whole solution", "wide / shallow", "outcomes · scope · boundaries")),
    ApproachStage(SPECIFICATION, StageScope("sprint", "Sprint", "narrow / deeper", "behaviour · design · logic")),
    ApproachStage(IMPLEMENTATION, StageScope("story", "Story", "narrowest / deep", "tests · code · interface")),
))
