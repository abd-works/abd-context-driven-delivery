"""The one list of CDD actions: the action toolsets the package that defines them registers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Iterator, Protocol

from harness.installation.files import Skill
from harness.annotations.annotation import Annotation, annotation_kinds
from harness.annotations.class_folder import class_folder
from harness.annotations.class_registry import ClassRegistry

# What an action does on a fidelity's stage, beside its place among the stage's actions: every fidelity goes through it
# (``STEP``, as generate and validate do), it takes the formats a person picks (``TAKES_FORMATS``, as every action that
# writes or converts a fidelity's files from its guidance does), it checks a fidelity's files rather than writing them
# (``CHECKS``, as validate does), or it converts a fidelity's files into other formats (``CONVERTS``, as render does). An
# action that checks or converts waits until there is output.
STEP: str = "step"
TAKES_FORMATS: str = "takes_formats"
CHECKS: str = "checks"
CONVERTS: str = "converts"


class OnStage(Annotation):
    """Annotate an action's operation, such as generate, with where it sits among the actions a person runs on a
    fidelity in its stage: its place in the order a board lists them (``rank``) and what it does there (``STEP``,
    ``TAKES_FORMATS``, ``CHECKS``, ``CONVERTS``), as ``@on_stage(1, STEP, TAKES_FORMATS)``. The action catalogue reads
    each action's place by this annotation (``Action.place``), so an action is added to the stages, renamed, or moved by
    changing its own annotation, never a list of names."""

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

    @property
    def needs_output(self) -> bool:
        """Whether the action works on output a fidelity already has: one that checks it or converts it."""
        return CHECKS in self._traits or CONVERTS in self._traits


on_stage = OnStage


class WorkedFidelity(Protocol):
    """The fidelity an action runs on, as this module names it: guidance.py's *FidelityGuidance* answers it. Naming only
    what a fidelity is here keeps the catalogue from importing the guidance that holds it."""

    @property
    def slug(self) -> str: ...


class ActionRunner(Protocol):
    """How an action runs on one fidelity. The framework names no action class: the module that defines how actions
    run registers its runner with ``ACTION_CATALOGUE.run_actions_with`` when it is imported."""

    def works_on_fidelities(self, action: Action) -> bool:
        """Whether action works on the guidance a caller names, so it can run on a fidelity."""

    def run(self, action: Action, fidelity: WorkedFidelity, arguments: dict[str, Any]) -> Any:
        """Run action on fidelity, in the session its practice works in, with arguments."""


class Action:
    """One action CDD ships: an operation an action toolset installs as a skill, such as generate, repair, or
    validate. One toolset can install several, as Improvement installs repair and verify_fix. The catalogue that made
    it runs it, through the runner registered with it."""

    def __init__(self, name: str, toolset_class: type, catalogue: ActionCatalogue) -> None:
        self._name = name
        self._toolset_class = toolset_class
        self._catalogue = catalogue

    @property
    def name(self) -> str:
        """The operation's name, as a chat or a session log line names the action."""
        return self._name

    @property
    def toolset_class(self) -> type:
        """The action toolset that holds the operation, such as Improvement for repair."""
        return self._toolset_class

    @property
    def operation(self) -> Callable[..., Any]:
        return vars(self._toolset_class)[self._name]

    @property
    def folder(self) -> Path:
        """The toolset's own folder, which holds its guide and module context."""
        return class_folder(self._toolset_class)

    @property
    def place(self) -> OnStage | None:
        """Where the action sits among the actions a person runs on a fidelity in its stage; none for an action run on
        no fidelity's stage, such as repair."""
        return OnStage.recorded_on(self.operation)

    def _run_on(self, fidelity: WorkedFidelity, **arguments: Any) -> Any:
        """Run this action on fidelity with arguments, through the runner its catalogue holds."""
        return self._catalogue._registered_runner.run(self, fidelity, arguments)

    def __repr__(self) -> str:
        return f"Action({self._name!r}, {self._toolset_class.__name__})"


class ActionsNotRegistered(LookupError):
    """A fidelity's action was run, and no module that runs actions has registered how in this process."""

    def __init__(self) -> None:
        super().__init__("no action runner is registered with ACTION_CATALOGUE in this process")


class FidelityAction:
    """One action held for one fidelity, which a caller runs as ``fidelity.actions.generate(format="drawio")``."""

    def __init__(self, action: Action, fidelity: WorkedFidelity) -> None:
        self.action = action
        self.fidelity = fidelity

    @property
    def name(self) -> str:
        return self.action.name

    def __call__(self, **arguments: Any) -> Any:
        return self.action._run_on(self.fidelity, **arguments)


class FidelityActions:
    """The actions of catalogue that work on one fidelity, each held for it and made once, by the action's name."""

    def __init__(self, fidelity: WorkedFidelity, catalogue: ActionCatalogue) -> None:
        self._held = {action.name: FidelityAction(action, fidelity) for action in catalogue._fidelity_actions}

    def __getattr__(self, name: str) -> FidelityAction:
        held = self.__dict__.get("_held", {})
        if name in held:
            return held[name]
        raise AttributeError(f"no action {name!r} works on this fidelity; the actions are {', '.join(held)}")

    def __iter__(self) -> Iterator[FidelityAction]:
        return iter(self._held.values())

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._held)


class ActionCatalogue:
    """Every action CDD ships. The framework names no action: the package that defines the action toolsets registers
    them with the process's one catalogue (``ACTION_CATALOGUE.register``) when it is imported, as every process that
    loads the repository's toolsets imports it. Each operation a toolset installs as a skill is one action; an
    operation annotated ``@noDeploy`` is not installed, so it is no action an agent or a person can run. The actions are
    made once from the registered toolsets and kept, as the practice catalogue keeps its practice classes."""

    def __init__(self) -> None:
        self._toolsets: ClassRegistry[object] = ClassRegistry(lambda toolset_class: class_folder(toolset_class).name)
        self._actions: tuple[Action, ...] | None = None
        self._on_fidelities: tuple[Action, ...] | None = None
        self._runner: ActionRunner | None = None

    def register(self, *toolset_classes: type) -> None:
        """Hold toolset_classes as the action toolsets CDD ships, in the order they are listed."""
        self._toolsets.register(*toolset_classes)
        self._actions = None
        self._on_fidelities = None

    def run_actions_with(self, runner: ActionRunner) -> None:
        """Have every action of this catalogue run on a fidelity through runner."""
        self._runner = runner

    @property
    def _registered_runner(self) -> ActionRunner:
        """The runner the module that defines how actions run registered when it was imported."""
        if self._runner is None:
            raise ActionsNotRegistered()
        return self._runner

    @property
    def _fidelity_actions(self) -> tuple[Action, ...]:
        """The actions that work on a fidelity, in catalogue order; none while no runner is registered."""
        runner = self._runner
        return tuple(action for action in self.actions if runner is not None and runner.works_on_fidelities(action))

    @property
    def toolsets(self) -> tuple[type, ...]:
        """Each registered action toolset class, in the order it was registered."""
        return self._toolsets.classes

    @property
    def actions(self) -> tuple[Action, ...]:
        """Every action, toolset by toolset in folder order, and within a toolset in the order it declares them; made
        once and kept."""
        if self._actions is None:
            self._actions = tuple(
                Action(name, toolset, self)
                for toolset in self.toolsets
                for name, member in vars(toolset).items()
                if Skill.publishes(member)
            )
        return self._actions

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(action.name for action in self.actions)

    @property
    def on_fidelities(self) -> tuple[Action, ...]:
        """Every action a person runs on a fidelity in its stage, in the order they sit: partition, which turns a source
        into what generate works from, then the steps, then the others a person runs in place of the next step. The same
        in every stage; made once and kept."""
        if self._on_fidelities is None:
            placed = [(place, action) for action in self.actions if (place := action.place) is not None]
            self._on_fidelities = tuple(action for _place, action in sorted(placed, key=lambda entry: entry[0].rank))
        return self._on_fidelities

    @property
    def steps(self) -> tuple[Action, ...]:
        """What every fidelity goes through in its stage, in order: generate, then validate. A fidelity is done once its
        latest validate passes."""
        return tuple(action for action in self.on_fidelities if action.place.step)

    @property
    def writing_step(self) -> Action:
        """The step that writes a fidelity's files: generate."""
        return next(action for action in self.steps if not action.place.checks)

    @property
    def checking_step(self) -> Action:
        """The step that checks a fidelity's files: validate."""
        return next(action for action in self.steps if action.place.checks)

    @property
    def producing(self) -> tuple[Action, ...]:
        """The actions that write a fidelity's files: every action on a fidelity but validate, which checks them."""
        return tuple(action for action in self.on_fidelities if not action.place.checks)

    @property
    def taking_formats(self) -> tuple[Action, ...]:
        """The actions whose command takes the formats a person picks: generate, iterate, sketch and document write a
        fidelity in them and render converts it into them, so each writes the same formats once they are picked;
        validate reads a fidelity's files in the formats they already have, and partition indexes a source."""
        return tuple(action for action in self.on_fidelities if action.place.takes_formats)

    @property
    def needing_output(self) -> tuple[Action, ...]:
        """The actions that work on a fidelity's output, so they wait until there is some: validate and render."""
        return tuple(action for action in self.on_fidelities if action.place.needs_output)


# The actions are classes' operations, and a class is defined once per process, so the catalogue of them is one per
# process too.
ACTION_CATALOGUE = ActionCatalogue()
