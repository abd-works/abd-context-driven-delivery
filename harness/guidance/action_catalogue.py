"""The one list of CDD actions: the action toolsets the package that defines them registers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Iterator, Protocol

from harness.agent_tools.agent_tools import InstallDestination
from harness.installation.files import Skill  # noqa: F401 - defining Skill registers the skill channel this reads
from harness.annotations.annotation import annotation_kinds
from harness.annotations.class_folder import class_folder

class WorkedFidelity(Protocol):
    """The fidelity an action runs on, as this module names it: guidance.py's *FidelityGuidance* answers it. Naming only
    what a fidelity is here keeps the catalogue from importing the guidance that holds it."""

    @property
    def slug(self) -> str: ...


class ActionRunner(Protocol):
    """How an action runs on one fidelity. The framework names no action class: the module that defines how actions
    run registers its runner with ``ActionCatalogue.run_actions_with`` when it is imported."""

    def works_on_fidelities(self, action: Action) -> bool:
        """Whether action works on the guidance a caller names, so it can run on a fidelity."""

    def run(self, action: Action, fidelity: WorkedFidelity, arguments: dict[str, Any]) -> Any:
        """Run action on fidelity, in the session its practice works in, with arguments."""


class Action:
    """One action CDD ships: an operation an action toolset installs as a skill, such as generate, repair, or
    validate. One toolset can install several, as Improvement installs repair and verify_fix."""

    def __init__(self, name: str, toolset_class: type) -> None:
        self._name = name
        self._toolset_class = toolset_class

    @property
    def name(self) -> str:
        """The operation's name, as a chat or a session log line names the action."""
        return self._name

    @property
    def toolset_class(self) -> type:
        """The action toolset that holds the operation, such as Improvement for repair."""
        return self._toolset_class

    @property
    def operation(self):
        return vars(self._toolset_class)[self._name]

    @property
    def folder(self) -> Path:
        """The toolset's own folder, which holds its guide and module context."""
        return class_folder(self._toolset_class)

    def run_on(self, fidelity: WorkedFidelity, **arguments: Any) -> Any:
        """Run this action on fidelity with arguments, through the runner the actions registered."""
        return ActionCatalogue.runner().run(self, fidelity, arguments)

    def __repr__(self) -> str:
        return f"Action({self._name!r}, {self._toolset_class.__name__})"


class ActionsNotRegistered(LookupError):
    """A fidelity's action was run, and no module that runs actions has registered how in this process."""

    def __init__(self) -> None:
        super().__init__("no action runner is registered with ActionCatalogue in this process")


class FidelityAction:
    """One action held for one fidelity, which a caller runs as ``fidelity.actions.generate(format="drawio")``."""

    def __init__(self, action: Action, fidelity: WorkedFidelity) -> None:
        self.action = action
        self.fidelity = fidelity

    @property
    def name(self) -> str:
        return self.action.name

    def __call__(self, **arguments: Any) -> Any:
        return self.action.run_on(self.fidelity, **arguments)


class FidelityActions:
    """The actions that work on one fidelity, each held for it and made once, by the action's name."""

    def __init__(self, fidelity: WorkedFidelity) -> None:
        self._held = {action.name: FidelityAction(action, fidelity) for action in ActionCatalogue.fidelity_actions()}

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
    them here when it is imported (``register``), as every process that loads the repository's toolsets imports it. Each
    operation a toolset installs as a skill is one action; an operation annotated ``@noDeploy`` is not installed, so it
    is no action an agent or a person can run. The actions are made once from the registered toolsets and kept for the
    process, as the practice catalogue keeps its practices."""

    _toolsets: ClassVar[tuple[type, ...]] = ()
    _actions: ClassVar[tuple[Action, ...] | None] = None
    _runner: ClassVar[ActionRunner | None] = None

    @classmethod
    def register(cls, *toolset_classes: type) -> None:
        """Hold toolset_classes as the action toolsets CDD ships, in the order they are listed."""
        ActionCatalogue._toolsets = tuple(toolset_classes)
        ActionCatalogue._actions = None

    @classmethod
    def run_actions_with(cls, runner: ActionRunner) -> None:
        """Have every fidelity run its actions through runner."""
        ActionCatalogue._runner = runner

    @classmethod
    def runner(cls) -> ActionRunner:
        """The runner the module that defines how actions run registered when it was imported."""
        if ActionCatalogue._runner is None:
            raise ActionsNotRegistered()
        return ActionCatalogue._runner

    @classmethod
    def fidelity_actions(cls) -> tuple[Action, ...]:
        """The actions that work on a fidelity, in catalogue order; none while no runner is registered."""
        runner = ActionCatalogue._runner
        return tuple(action for action in cls.actions() if runner is not None and runner.works_on_fidelities(action))

    @classmethod
    def toolsets(cls) -> tuple[type, ...]:
        """Each registered action toolset class, in the order it was registered."""
        return cls._toolsets

    @classmethod
    def actions(cls) -> tuple[Action, ...]:
        """Every action, toolset by toolset in folder order, and within a toolset in the order it declares them; made
        once and kept."""
        if cls._actions is None:
            ActionCatalogue._actions = tuple(
                Action(name, toolset)
                for toolset in cls.toolsets()
                for name, member in vars(toolset).items()
                if annotation_kinds.publishes(InstallDestination.SKILL, member)
            )
        return cls._actions

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(action.name for action in cls.actions())

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls.names()

    @classmethod
    def action(cls, name: str) -> Action | None:
        """The action called name, such as repair; none when no toolset installs it."""
        return next((action for action in cls.actions() if action.name == name), None)

