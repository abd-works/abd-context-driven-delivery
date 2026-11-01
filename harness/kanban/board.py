"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

import json
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.mcp.mcp_server import mcp

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.ticket import Ticket
    from space.repo.repo import Repo

STAGE_NAMES = ("Discovery", "Specification", "Implementation")
SESSIONS_FOLDER = ".sessions"
CLOSED_FOLDER = "closed"
BACKLOG_FOLDER = "_backlog"
MAIN_SESSION_FOLDER = "main"
CURRENT_SESSION_FILE = "session.json"
BOARD_FILE = "_board.json"
DEFAULT_WIP_LIMIT = 3
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
FORGE = "https://forge.abdworks.net/abd-context-driven-delivery"
FIDELITIES_WITHOUT_PAGE = ("ddd-model", "bdd-realization")


def name_of(title: str) -> str:
    """The folder and file name a title gets: `Pet visits` is `pet-visits`."""
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


@agent_toolset
class Board:
    """Show every work session as a ticket on a kanban: Backlog, Discovery, Specification, Implementation, and Complete."""

    # The board is read after every cdd call and every prompt, so its tools stay out of the session log.
    # Every ticket is in exactly one column; the board stores no ticket state.

    def __init__(self, sessions_folder: Path | str, practices: list[PracticeGuidance]) -> None:
        self._sessions_folder = Path(sessions_folder)
        self._practices = list(practices)
        self._columns = self._build_columns()

    @classmethod
    def load(cls, sessions_folder: Path | str) -> Board:
        """A board with every practice chosen."""
        from bdd.bdd import Bdd
        from clean_engineering.clean_engineering import CleanEngineering
        from ddd.ddd import Ddd
        from stories.stories import Stories
        from ux.ux import Ux

        return cls(sessions_folder, [Stories(), Ddd(), Ux(), CleanEngineering(), Bdd()])

    @classmethod
    @tool_subject
    def current(cls) -> Board:
        """The board of the project being worked on: `CDD_PROJECT`, else the current folder."""
        project = Path(os.environ.get("CDD_PROJECT") or os.getcwd()).resolve()
        return cls.load(project / SESSIONS_FOLDER)

    @property
    def sessions_folder(self) -> Path:
        return self._sessions_folder

    @property
    def repo_root(self) -> Path:
        return self._sessions_folder.parent

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
        from space.session import Session

        return [Ticket(Session.at(folder, self.repo_root), self) for folder in self._ticket_folders()]

    @property
    def backlog_items(self) -> list[BacklogItem]:
        from harness.kanban.backlog_item import BacklogItem

        folder = self._sessions_folder / BACKLOG_FOLDER
        if not folder.is_dir():
            return []
        return [BacklogItem(path, self) for path in sorted(folder.glob("*.md"))]

    @property
    def cards(self) -> list[Card]:
        return [*self.tickets, *self.backlog_items]

    @property
    def active(self) -> Ticket | None:
        current = self._sessions_folder / CURRENT_SESSION_FILE
        if not current.is_file():
            return None
        name = json.loads(current.read_text(encoding="utf-8")).get("session", "")
        return self.ticket(name) if name else None

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
        (self._sessions_folder / BOARD_FILE).write_text(json.dumps({"wip_limits": limits}), encoding="utf-8")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def help(self, practice: str, fidelity: str = "") -> dict[str, Any]:
        """Return the overview, guidance, and rules of practice, or of its fidelity when one is named, with its page on the forge."""
        from harness.kanban.ticket import practice_key

        guidance = next(entry for entry in self._practices if practice_key(entry) == practice)
        subject = guidance.fidelities[fidelity] if fidelity else guidance
        return {
            "title": fidelity.replace("_", "-") or type(guidance).__name__,
            "overview": (subject.overview or "").strip(),
            "guidance": (subject.guidance or "").strip(),
            "rules": [{"slug": rule.slug, "text": rule.body.strip()} for rule in subject.rules],
            "href": self._forge_page(practice, fidelity),
        }

    def wip_limit(self, stage: str) -> int:
        return self._saved_wip_limits.get(stage, DEFAULT_WIP_LIMIT)

    def to_json(self) -> dict[str, Any]:
        """Every column with its tickets or items: what the board pane and other IDEs read."""
        active = self.active
        return {
            "project": self.repo_root.name,
            "active": active.name if active else None,
            "columns": [column.to_json() for column in self._columns],
        }

    @property
    def _saved_wip_limits(self) -> dict[str, int]:
        path = self._sessions_folder / BOARD_FILE
        return json.loads(path.read_text(encoding="utf-8")).get("wip_limits", {}) if path.is_file() else {}

    def _forge_page(self, practice: str, fidelity: str) -> str:
        slug = f"{practice}-{fidelity}"
        if not fidelity or slug in FIDELITIES_WITHOUT_PAGE:
            return f"{FORGE}/context-tools/{practice}.html"
        return f"{FORGE}/fidelities/{slug}.html"

    def _build_columns(self) -> list[Column]:
        from generate.generate import Generate
        from review.review import Review
        from validate.validate import Validate

        stages = [Stage(name, self, [Generate, Validate, Review]) for name in STAGE_NAMES]
        return [Backlog(self), *stages, Column("Complete", self)]

    def _ticket_folders(self) -> list[Path]:
        if not self._sessions_folder.is_dir():
            return []
        skipped = {CLOSED_FOLDER, MAIN_SESSION_FOLDER}
        open_folders = [
            folder for folder in sorted(self._sessions_folder.iterdir())
            if folder.is_dir() and folder.name not in skipped and not folder.name.startswith("_")
        ]
        closed = self._sessions_folder / CLOSED_FOLDER
        closed_folders = sorted(folder for folder in closed.iterdir() if folder.is_dir()) if closed.is_dir() else []
        return open_folders + closed_folders


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

    def to_json(self) -> dict[str, Any]:
        return {"name": self._name, "tickets": [card.to_json() for card in self.cards]}


class Backlog(Column):
    """*Backlog* is the first column: the ideas a person has added to the backlog folder."""

    def __init__(self, board: Board) -> None:
        super().__init__("Backlog", board)

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "items": [card.to_json() for card in self.cards]}


class Stage(Column):
    """*Stage* is a column where work is done: every chosen practice's fidelity for it goes through its actions."""

    def __init__(self, name: str, board: Board, actions: list[type]) -> None:
        super().__init__(name, board)
        self._actions = list(actions)

    @property
    def actions(self) -> list[type]:
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

    def to_json(self) -> dict[str, Any]:
        tickets = self.cards
        return {
            "name": self.name,
            "work_required": [self._slug(fidelity) for fidelity in self.work_required],
            "formats": {self._slug(fidelity): list(fidelity.output_files) for fidelity in self.work_required},
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
        return moment.astimezone(timezone.utc).strftime(TIMESTAMP_FORMAT)
