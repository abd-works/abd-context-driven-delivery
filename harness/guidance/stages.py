"""The stages of the CDD approach: Discovery, Specification, and Implementation.

Each fidelity names its stage in its practice markdown as **Stage:**. The session board, the chat bar, and the catalog
draw the stages from here, so a stage's order, scope, and actions are written once.
"""

from __future__ import annotations

from harness.annotations.annotation import Annotatable, Annotation
from harness.guidance.action_catalogue import ACTION_CATALOGUE, Action, ActionCatalogue
from harness.installation.data_class import data_field

DISCOVERY: str = "discovery"
SPECIFICATION: str = "specification"
IMPLEMENTATION: str = "implementation"

# The steps every fidelity goes through in its stage, named as the session log names them.
GENERATE: str = "generate"
VALIDATE: str = "validate"
# The action that converts a fidelity's output into other formats, so it needs output to convert.
RENDER: str = "render"


# What an action does on a fidelity's stage, beside its place among the stage's actions: every fidelity goes through it
# (``STEP``, as generate and validate do), it takes the formats a person picks (``TAKES_FORMATS``, as generate and render
# do), or it checks a fidelity's files rather than writing them (``CHECKS``, as validate does).
STEP: str = "step"
TAKES_FORMATS: str = "takes_formats"
CHECKS: str = "checks"


class OnStage(Annotation):
    """Annotate an action's operation, such as generate, with where it sits among the actions a person runs on a
    fidelity in its stage: its place in the order a board lists them (``rank``) and what it does there (``STEP``,
    ``TAKES_FORMATS``, ``CHECKS``), as ``@on_stage(1, STEP, TAKES_FORMATS)``. Each stage reads its actions from the
    action catalogue by this annotation (``OnStage.recorded_on``), so an action is added to the stages, renamed, or
    moved by changing its own annotation, never a list of names kept here."""

    flag = "_on_stage"
    copied = False

    def __new__(cls, rank: int, *traits: str):
        return object.__new__(cls)

    def __init__(self, rank: int, *traits: str) -> None:
        self.rank = rank
        self._traits = frozenset(traits)

    @property
    def step(self) -> bool:
        """Whether every fidelity goes through the action in its stage."""
        return STEP in self._traits

    @property
    def takes_formats(self) -> bool:
        """Whether the action's command takes the formats a person picks."""
        return TAKES_FORMATS in self._traits

    @property
    def checks(self) -> bool:
        """Whether the action checks a fidelity's files rather than writing them."""
        return CHECKS in self._traits

    def annotate(self, target: Annotatable) -> Annotatable:
        setattr(target, self.flag, self)
        return target


on_stage = OnStage


class StageScope:
    """How much of the solution a stage's work covers, drawn as a shape that narrows and deepens along the board:
    Discovery takes in the whole solution wide and shallow, Implementation one story narrow and deep."""

    def __init__(self, shape: str, name: str, reach: str) -> None:
        self._shape = shape
        self._name = name
        self._reach = reach
        self._covers = ""

    def covering(self, covers: str) -> StageScope:
        """This scope with what its work decides, such as `outcomes · scope · boundaries`; a scope made without it
        decides nothing it names."""
        return _CoveredScope(self, covers)

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


class _CoveredScope(StageScope):
    """A stage's scope with what its work decides, which ``StageScope.covering`` makes."""

    def __init__(self, scope: StageScope, covers: str) -> None:
        super().__init__(scope.shape, scope.name, scope.reach)
        self._covers = covers


class ApproachStage:
    """One stage of the CDD approach: the name each fidelity's **Stage:** gives it, its title, its scope, and the
    actions a person runs on a fidelity in it, which are the actions of its catalogue annotated ``@on_stage``. The
    session board's stage columns and the catalog's columns are each built on one."""

    def __init__(self, name: str, scope: StageScope, catalogue: ActionCatalogue) -> None:
        self._name = name
        self._scope = scope
        self._catalogue = catalogue

    @property
    def _placed(self) -> list[tuple[OnStage, Action]]:
        """Each action of the catalogue run on a fidelity in this stage, with where it sits, in the order it sits."""
        placed = [(place, action) for action in self._catalogue.actions if (place := OnStage.recorded_on(action.operation)) is not None]
        return sorted(placed, key=lambda entry: entry[0].rank)

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
        """What every fidelity goes through in this stage, in order: generate, then validate. A fidelity is done once
        its latest validate passes."""
        return [action.name for place, action in self._placed if place.step]

    @property
    @data_field
    def actions(self) -> list[str]:
        """Every action a person can run on a fidelity in this stage, in the order they sit: partition, which turns a
        source into what generate works from, then its steps, then the others a person runs in place of the next step."""
        return [action.name for _place, action in self._placed]

    @property
    @data_field
    def producing_actions(self) -> list[str]:
        """The actions that write a fidelity's files: every action but validate, which checks them."""
        return [action.name for place, action in self._placed if not place.checks]

    @property
    @data_field
    def actions_with_formats(self) -> list[str]:
        """The actions whose command takes the formats a person picks: generate writes a fidelity in them and render
        converts it into them; every other action writes or reads a fidelity's files in the formats they already have."""
        return [action.name for place, action in self._placed if place.takes_formats]


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
    ApproachStage(DISCOVERY, StageScope("solution", "Whole solution", "wide / shallow").covering("outcomes · scope · boundaries"), ACTION_CATALOGUE),
    ApproachStage(SPECIFICATION, StageScope("sprint", "Sprint", "narrow / deeper").covering("behaviour · design · logic"), ACTION_CATALOGUE),
    ApproachStage(IMPLEMENTATION, StageScope("story", "Story", "narrowest / deep").covering("tests · code · interface"), ACTION_CATALOGUE),
))
