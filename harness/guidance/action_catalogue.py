"""The one list of CDD actions, found from the action folders under ``cdd_guidance/actions``."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from harness.agent_tools.agent_tools import InstallDestination
from harness.name.name import Name
from harness.installation.files import Skill  # noqa: F401 - defining Skill registers the skill channel this reads
from harness.marks.mark import mark_kinds

_ACTIONS_FOLDER = Path(__file__).resolve().parents[2] / "cdd_guidance" / "actions"


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
    def toolset_ref(self) -> str:
        """The toolset as a toolset ref names it, by its module's full name, such as
        ``cdd_guidance.actions.generate.generate:Generate``."""
        return f"{self._toolset_class.__module__}:{self._toolset_class.__name__}"

    @property
    def operation(self):
        return vars(self._toolset_class)[self._name]

    @property
    def folder(self) -> Path:
        """The toolset's folder under ``cdd_guidance/actions``, which holds its guide and module context."""
        return Path(inspect.getfile(self._toolset_class)).resolve().parent

    def __repr__(self) -> str:
        return f"Action({self._name!r}, {self._toolset_class.__name__})"


class ActionCatalogue:
    """Every action CDD ships, read from its action folders: each folder under ``cdd_guidance/actions`` whose name
    does not start with ``_`` holds its toolset in the module of the folder's name, as the class of that name in Pascal
    case (``grill_context/grill_context.py`` holds ``GrillContext``). Each operation the toolset installs as a skill is
    one action; an operation marked ``@noDeploy`` is not installed, so it is no action an agent or a person can run. A
    new action folder joins the catalogue by being there, so no other list has to learn about it.

    The toolsets are imported on first use and kept for the process, as the practice catalogue keeps its practices."""

    _toolsets: tuple[type, ...] | None = None

    @classmethod
    def toolsets(cls) -> tuple[type, ...]:
        """Each action folder's toolset class, in folder order."""
        if cls._toolsets is None:
            cls._toolsets = tuple(cls._toolset_in(folder.name) for folder in cls._folders())
        return cls._toolsets

    @classmethod
    def actions(cls) -> tuple[Action, ...]:
        """Every action, toolset by toolset in folder order, and within a toolset in the order it declares them."""
        return tuple(
            Action(name, toolset)
            for toolset in cls.toolsets()
            for name, member in vars(toolset).items()
            if mark_kinds.publishes(InstallDestination.SKILL, member)
        )

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

    @classmethod
    def _folders(cls) -> list[Path]:
        return [
            folder for folder in sorted(_ACTIONS_FOLDER.iterdir())
            if folder.is_dir() and folder.name[0] not in "_." and (folder / f"{folder.name}.py").is_file()
        ]

    @classmethod
    def _toolset_in(cls, folder: str) -> type:
        module = importlib.import_module(f"cdd_guidance.actions.{folder}.{folder}")
        return getattr(module, Name(folder).title_pascal)
