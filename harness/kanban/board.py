"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import language_adapter
from harness.kanban.data import BoardData, ColumnData, HelpData
from harness.mcp.mcp_server import mcp
from space.session import Session
from space.work_state import project_checkout

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.ticket import Ticket
    from space.repo.repo import Repo

STAGE_NAMES = ("Discovery", "Specification", "Implementation")
# What every fidelity goes through in its stage, named as the session log names them.
STAGE_ACTIONS = ("generate", "validate", "review")
FORGE = "https://forge.abdworks.net/abd-context-driven-delivery"
FIDELITIES_WITHOUT_PAGE = ("ddd-model", "bdd-realization")
UNCHOSEN_FOLDERS = frozenset({"node_modules", "__pycache__"})


@cache
def _every_practice() -> tuple[PracticeGuidance, ...]:
    """The practices a board shows, built once per process: they do not change between tool calls, and building them
    took about 30 ms on every call. A board that changes one, such as the fidelity a ticket reads files for, puts it
    back before the call ends."""
    from bdd.bdd import Bdd
    from clean_engineering.clean_engineering import CleanEngineering
    from ddd.ddd import Ddd
    from stories.stories import Stories
    from ux.ux import Ux

    return (Stories(), Ddd(), Ux(), CleanEngineering(), Bdd())


def name_of(title: str) -> str:
    """The folder and file name a title gets: `Pet visits` is `pet-visits`."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


@language_adapter(language="typescript")
@agent_toolset
class Board:
    """Show every work session as a ticket on a kanban: Backlog, Discovery, Specification, Implementation, and Complete."""

    # The board is read after every cdd call and every prompt, so its tools stay out of the session log.
    # Every ticket is in exactly one column; the board stores no ticket state.

    def __init__(self, repo_root: Path | str, practices: list[PracticeGuidance]) -> None:
        self._repo_root = Path(repo_root).resolve()
        self._practices = list(practices)
        self._columns = self._build_columns()

    @classmethod
    def load(cls, repo_root: Path | str) -> Board:
        """A board with every practice chosen."""
        return cls(repo_root, list(_every_practice()))

    @classmethod
    @tool_subject
    def current(cls) -> Board:
        """The board of the project being worked on, found the way sessions find it."""
        return cls.load(project_checkout())

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    @property
    def repo(self) -> Repo:
        from space.repo.repo import Repo

        return Repo(self.repo_root)

    @property
    def practices(self) -> list[PracticeGuidance]:
        return list(self._practices)

    @property
    def columns(self) -> list[Column]:
        return list(self._columns)

    @property
    def tickets(self) -> list[Ticket]:
        from harness.kanban.ticket import Ticket

        return [Ticket(session, self) for session in Session.all_in(self.repo_root)]

    @property
    def backlog_items(self) -> list[BacklogItem]:
        from harness.kanban.backlog_item import BacklogItem

        folder = Session.backlog_folder(self.repo_root)
        if not folder.is_dir():
            return []
        # An item is a file in the Backlog, or a folder holding a file of its own name: a ticket moved back keeps its
        # whole folder, history and all. A folder beside a file of its name is that file's ticket, not a second item.
        files = list(folder.glob("*.md"))
        kept = [entry / f"{entry.name}.md" for entry in folder.iterdir() if entry.is_dir() and not (folder / f"{entry.name}.md").exists()]
        return [BacklogItem(path, self) for path in sorted([*files, *(path for path in kept if path.is_file())], key=lambda path: path.stem)]

    @property
    def cards(self) -> list[Card]:
        return [*self.tickets, *self.backlog_items]

    @property
    def active(self) -> Ticket | None:
        """The ticket of the session saved as open; none while main is, since main is not on the board."""
        return self.ticket(Session.active_name(self.repo_root))

    def column(self, name: str) -> Column:
        return next(column for column in self._columns if column.name == name)

    def ticket(self, name: str) -> Ticket | None:
        return next((ticket for ticket in self.tickets if ticket.name == name), None)

    def backlog_item(self, title: str) -> BacklogItem | None:
        return next((item for item in self.backlog_items if item.title == title), None)

    @mcp
    @agent_tool
    @noSessionLog
    def show(self) -> Board:
        """Return the session board: Backlog, Discovery, Specification, Implementation, and Complete, with every ticket's progress through Generate, Validate, and Review, and the active ticket."""
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def set_wip_limit(self, stage: str, limit: int) -> Board:
        """Set how many tickets stage holds before its count shows as over its limit."""
        limits = {**self._saved_wip_limits, stage: limit}
        Session.board_file(self.repo_root).write_text(json.dumps({"wip_limits": limits}), encoding="utf-8")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def folders(self, path: str = "") -> list[str]:
        """List the folders inside path, a folder in the repository (its top when empty), as paths from the project, for a person choosing a root. Installed packages, caches, and hidden folders hold no one's work, so they are left out."""
        parent = self.repo_root / path
        found = [entry for entry in parent.iterdir() if entry.is_dir() and entry.name not in UNCHOSEN_FOLDERS and not entry.name.startswith(".")]
        return sorted(entry.relative_to(self.repo_root).as_posix() for entry in found)

    @mcp
    @agent_tool
    @noSessionLog
    def help(self, practice: str, fidelity: str = "") -> HelpData:
        """Return the overview, guidance, and rules of practice, or of its fidelity when one is named, with the stage that fidelity belongs to and its page on the forge."""
        from harness.kanban.ticket import practice_key

        guidance = next(entry for entry in self._practices if practice_key(entry) == practice)
        subject = guidance.fidelities[fidelity] if fidelity else guidance
        return {
            "practice": practice,
            "fidelity": fidelity,
            "stage": subject.stage.capitalize() if fidelity else "",
            "overview": (subject.overview or "").strip(),
            "guidance": (subject.guidance or "").strip(),
            "rules": [{"slug": rule.slug, "text": rule.body.strip()} for rule in subject.rules],
            "href": self._forge_page(practice, fidelity),
        }

    def wip_limit(self, stage: str) -> int:
        return self._saved_wip_limits.get(stage, Session.default_wip)

    def to_json(self) -> BoardData:
        """Every column with its tickets or items: what the board pane and other IDEs read."""
        active = self.active
        return {
            "project": self.repo_root.name,
            "active": active.name if active else None,
            "columns": [column.to_json() for column in self._columns],
        }

    @property
    def _saved_wip_limits(self) -> dict[str, int]:
        path = Session.board_file(self.repo_root)
        return json.loads(path.read_text(encoding="utf-8")).get("wip_limits", {}) if path.is_file() else {}

    def _forge_page(self, practice: str, fidelity: str) -> str:
        slug = f"{practice}-{fidelity}"
        if not fidelity or slug in FIDELITIES_WITHOUT_PAGE:
            return f"{FORGE}/context-tools/{practice}.html"
        return f"{FORGE}/fidelities/{slug}.html"

    def _build_columns(self) -> list[Column]:
        stages = [Stage(name, self, list(STAGE_ACTIONS)) for name in STAGE_NAMES]
        return [Backlog(self), *stages, Column("Complete", self)]


class Column:
    """*Column* is one place on the board: Backlog, a stage, or Complete."""

    def __init__(self, name: str, board: Board) -> None:
        self._name = name
        self._board = board

    @property
    def name(self) -> str:
        return self._name

    @property
    def cards(self) -> list[Card]:
        return [card for card in self._board.cards if card.column is self]

    def to_json(self) -> ColumnData:
        return {"name": self._name, "tickets": [card.to_json() for card in self.cards]}


class Backlog(Column):
    """*Backlog* is the first column: the ideas a person has added to the backlog folder."""

    def __init__(self, board: Board) -> None:
        super().__init__("Backlog", board)

    def to_json(self) -> ColumnData:
        return {"name": self.name, "items": [card.to_json() for card in self.cards]}


class Stage(Column):
    """*Stage* is a column where work is done: every chosen practice's fidelity for it goes through its actions."""

    def __init__(self, name: str, board: Board, actions: list[str]) -> None:
        super().__init__(name, board)
        self._actions = list(actions)

    @property
    def actions(self) -> list[str]:
        return list(self._actions)

    @property
    def practices(self) -> list[PracticeGuidance]:
        return self._board.practices

    @property
    def work_required(self) -> list[FidelityGuidance]:
        """Every fidelity of every chosen practice whose stage is this stage, in practice order."""
        stage = self.name.lower()
        return [fidelity for practice in self.practices for fidelity in self._fidelities_of(practice) if fidelity.stage == stage]

    @property
    def next_stage(self) -> Stage | None:
        columns = self._board.columns
        following = columns[columns.index(self) + 1]
        return following if isinstance(following, Stage) else None

    @property
    def previous_stage(self) -> Stage | None:
        columns = self._board.columns
        earlier = columns[columns.index(self) - 1]
        return earlier if isinstance(earlier, Stage) else None

    @property
    def in_progress(self) -> list[Ticket]:
        return [ticket for ticket in self.cards if not ticket.is_done]

    @property
    def done(self) -> list[Ticket]:
        return [ticket for ticket in self.cards if ticket.is_done]

    @property
    def wip_limit(self) -> int:
        return self._board.wip_limit(self.name)

    def to_json(self) -> ColumnData:
        tickets = self.cards
        return {
            "name": self.name,
            "work_required": [self._slug(fidelity) for fidelity in self.work_required],
            "formats": {self._slug(fidelity): list(fidelity.output_files) for fidelity in self.work_required},
            "default_formats": {self._slug(fidelity): fidelity.default_format for fidelity in self.work_required},
            "wip_limit": self.wip_limit,
            "is_over_limit": len(tickets) > self.wip_limit,
            "in_progress": [ticket.to_json() for ticket in tickets if not ticket.is_done],
            "done": [ticket.to_json() for ticket in tickets if ticket.is_done],
        }

    def _fidelities_of(self, practice: PracticeGuidance) -> list[FidelityGuidance]:
        entries = practice.fidelities.entries
        return list(entries.values()) if isinstance(entries, dict) else list(entries)

    def _slug(self, fidelity: FidelityGuidance) -> str:
        from harness.kanban.ticket import practice_key

        return f"{practice_key(fidelity.practice_guidance)}-{fidelity.name}"


class Card(ABC):
    """*Card* is anything on the board that a person moves: a ticket or a backlog item."""

    def __init__(self, board: Board) -> None:
        self._board = board

    @property
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def column(self) -> Column: ...

    @property
    @abstractmethod
    def last_activity(self) -> str: ...

    @abstractmethod
    def move_next(self) -> Card: ...

    @abstractmethod
    def move_previous(self) -> Card: ...

    def to_json(self) -> dict[str, Any]:
        return {"title": self.title, "last_activity": self.last_activity}

    def _timestamp(self, moment: datetime) -> str:
        return Session.timestamp(moment)
