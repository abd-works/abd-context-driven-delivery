"""The stages of the CDD approach: Discovery, Specification, and Implementation.

Each fidelity names its stage in its practice markdown as **Stage:**. The session board, the chat bar, and the catalog
draw the stages from here, so a stage's order, scope, and actions are written once.
"""

from __future__ import annotations

from harness.installation.data_class import data_field

DISCOVERY: str = "discovery"
SPECIFICATION: str = "specification"
IMPLEMENTATION: str = "implementation"

# The steps every fidelity goes through in its stage, named as the session log names them.
GENERATE: str = "generate"
VALIDATE: str = "validate"
# The action that converts a fidelity's output into other formats, so it needs output to convert.
RENDER: str = "render"


class StageScope:
    """How much of the solution a stage's work covers, drawn as a shape that narrows and deepens along the board:
    Discovery takes in the whole solution wide and shallow, Implementation one story narrow and deep."""

    def __init__(self, shape: str, name: str, reach: str, covers: str) -> None:
        self._shape = shape
        self._name = name
        self._reach = reach
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
    """One stage of the CDD approach: the name each fidelity's **Stage:** gives it, its title, its scope, and the
    actions a person runs on a fidelity in it. The session board's stage columns and the catalog's columns are each
    built on one."""

    # The steps every fidelity goes through, then the other actions a person can run on a fidelity in place of the
    # next step. Each is an operation in the action catalogue; a fidelity is done once its latest validate passes.
    _STEPS = (GENERATE, VALIDATE)
    _OTHER_ACTIONS = ("iterate", "sketch", RENDER, "document", "partition")
    # Generate writes a fidelity in the formats a person picks, and render converts it into them; every other action
    # writes or reads a fidelity's files in the formats they already have.
    _ACTIONS_WITH_FORMATS = (GENERATE, RENDER)

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

    @property
    @data_field
    def steps(self) -> list[str]:
        """What every fidelity goes through in this stage, in order: generate, then validate."""
        return list(self._STEPS)

    @property
    @data_field
    def actions(self) -> list[str]:
        """Every action a person can run on a fidelity in this stage: its steps first, then the others."""
        return [*self._STEPS, *self._OTHER_ACTIONS]

    @property
    @data_field
    def producing_actions(self) -> list[str]:
        """The actions that write a fidelity's files: every action but validate, which checks them."""
        return [action for action in self.actions if action != VALIDATE]

    @property
    @data_field
    def actions_with_formats(self) -> list[str]:
        """The actions whose command takes the formats a person picks: generate writes a fidelity in them and render
        converts it into them."""
        return list(self._ACTIONS_WITH_FORMATS)


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
