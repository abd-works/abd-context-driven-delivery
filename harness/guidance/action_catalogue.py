"""The one list of CDD actions, found from the action folders under ``cdd_guidance/actions``."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from harness.agent_tools.name import Name
from harness.installation.files import Skill

_ACTIONS_FOLDER = Path(__file__).resolve().parents[2] / "cdd_guidance" / "actions"


class Action:
    """One action CDD ships: an operation an action kit publishes as a skill, such as generate, repair, or createRule.
    One kit can publish several, as Validate publishes validate and createRule."""

    def __init__(self, name: str, kit_class: type) -> None:
        self._name = name
        self._kit_class = kit_class

    @property
    def name(self) -> str:
        """The operation's name, as a chat or a session log line names the action."""
        return self._name

    @property
    def kit_class(self) -> type:
        """The action kit that holds the operation, such as Validate for createRule."""
        return self._kit_class

    @property
    def kit_ref(self) -> str:
        """The kit as a toolset ref names it, by its module's full name, such as
        ``cdd_guidance.actions.generate.generate:Generate``."""
        return f"{self._kit_class.__module__}:{self._kit_class.__name__}"

    @property
    def operation(self):
        return vars(self._kit_class)[self._name]

    @property
    def folder(self) -> Path:
        """The kit's folder under ``cdd_guidance/actions``, which holds its guide and module context."""
        return Path(inspect.getfile(self._kit_class)).resolve().parent

    def __repr__(self) -> str:
        return f"Action({self._name!r}, {self._kit_class.__name__})"


class ActionCatalogue:
    """Every action CDD ships, read from its action folders: each folder under ``cdd_guidance/actions`` whose name
    does not start with ``_`` holds its kit in the module of the folder's name, as the class of that name in Pascal
    case (``grill_context/grill_context.py`` holds ``GrillContext``). Each operation the kit marks as a skill is one
    action. A new action folder joins the catalogue by being there, so no other list has to learn about it.

    The kits are imported on first use and kept for the process, as the practice catalogue keeps its practices."""

    _kits: tuple[type, ...] | None = None

    @classmethod
    def kits(cls) -> tuple[type, ...]:
        """Each action folder's kit class, in folder order."""
        if cls._kits is None:
            cls._kits = tuple(cls._kit_in(folder.name) for folder in cls._folders())
        return cls._kits

    @classmethod
    def actions(cls) -> tuple[Action, ...]:
        """Every action, kit by kit in folder order, and within a kit in the order it declares them."""
        return tuple(
            Action(name, kit) for kit in cls.kits() for name, member in vars(kit).items() if Skill.marks(member)
        )

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(action.name for action in cls.actions())

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls.names()

    @classmethod
    def action(cls, name: str) -> Action | None:
        """The action called name, such as createRule; none when no kit publishes it."""
        return next((action for action in cls.actions() if action.name == name), None)

    @classmethod
    def _folders(cls) -> list[Path]:
        return [
            folder for folder in sorted(_ACTIONS_FOLDER.iterdir())
            if folder.is_dir() and folder.name[0] not in "_." and (folder / f"{folder.name}.py").is_file()
        ]

    @classmethod
    def _kit_in(cls, folder: str) -> type:
        module = importlib.import_module(f"cdd_guidance.actions.{folder}.{folder}")
        return getattr(module, Name(folder).title_pascal)
