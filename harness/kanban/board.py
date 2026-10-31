"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.ticket import Ticket

STAGE_NAMES = ("Discovery", "Specification", "Implementation")
CLOSED_FOLDER = "closed"
BACKLOG_FOLDER = "_backlog"
NO_SESSION_FOLDER = "default"
CURRENT_SESSION_FILE = "session.json"


class Board:
    """*Board* shows every work session in a sessions folder as a ticket, placed by how far the chosen practices'
    fidelities have got through each stage's actions."""

    # every ticket is in exactly one column; the board stores no ticket state

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

    @property
    def sessions_folder(self) -> Path:
        return self._sessions_folder

    @property
    def practices(self) -> list[PracticeGuidance]:
        return list(self._practices)

    @property
    def columns(self) -> list[Column]:
        return list(self._columns)

    @property
    def tickets(self) -> list[Ticket]:
        from harness.kanban.ticket import Ticket

        return [Ticket(folder, self) for folder in self._ticket_folders()]

    @property
    def backlog_items(self) -> list[BacklogItem]:
        from harness.kanban.backlog_item import BacklogItem

        folder = self._sessions_folder / BACKLOG_FOLDER
        if not folder.is_dir():
            return []
        return [BacklogItem(path, self) for path in sorted(folder.glob("*.md"))]

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

    def new_ticket(self, title: str, scope: str, parent: Ticket | None) -> Ticket:
        """A new ticket is in Discovery, in progress, until its log shows work in a later stage."""
        from harness.kanban.ticket import Ticket

        name = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
        folder = self._sessions_folder / name
        folder.mkdir(parents=True, exist_ok=True)
        fields = {"name": name, "title": title, "scope": scope, "parent": parent.name if parent else ""}
        (folder / "session.json").write_text(json.dumps(fields), encoding="utf-8")
        (folder / "session.log").touch()
        return Ticket(folder, self)

    def to_json(self) -> dict[str, Any]:
        """Every column with its tickets or items: what the board pane and other IDEs read."""
        active = self.active
        return {"active": active.name if active else None, "columns": [column.to_json() for column in self._columns]}

    def _build_columns(self) -> list[Column]:
        from generate.generate import Generate
        from review.review import Review
        from validate.validate import Validate

        stages = [Stage(name, self, [Generate, Validate, Review]) for name in STAGE_NAMES]
        return [Backlog(self), *stages, Column("Complete", self)]

    def _ticket_folders(self) -> list[Path]:
        if not self._sessions_folder.is_dir():
            return []
        skipped = {CLOSED_FOLDER, NO_SESSION_FOLDER}
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
    def tickets(self) -> list[Ticket]:
        return [ticket for ticket in self._board.tickets if ticket.column is self]

    def to_json(self) -> dict[str, Any]:
        return {"name": self._name, "tickets": [ticket.to_json() for ticket in self.tickets]}


class Backlog(Column):
    """*Backlog* is the first column: the ideas a person has added to the backlog folder."""

    def __init__(self, board: Board) -> None:
        super().__init__("Backlog", board)

    @property
    def items(self) -> list[BacklogItem]:
        return self._board.backlog_items

    def to_json(self) -> dict[str, Any]:
        return {"name": self.name, "items": [item.to_json() for item in self.items]}


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
        return [fidelity for practice in self.practices for fidelity in _fidelities(practice) if fidelity.stage == stage]

    @property
    def next_stage(self) -> Stage | None:
        columns = self._board.columns
        following = columns[columns.index(self) + 1]
        return following if isinstance(following, Stage) else None

    @property
    def in_progress(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if not ticket.is_done]

    @property
    def done(self) -> list[Ticket]:
        return [ticket for ticket in self.tickets if ticket.is_done]

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "work_required": [_fidelity_slug(fidelity) for fidelity in self.work_required],
            "in_progress": [ticket.to_json() for ticket in self.in_progress],
            "done": [ticket.to_json() for ticket in self.done],
        }


def _fidelities(practice: PracticeGuidance) -> list[FidelityGuidance]:
    entries = practice.fidelities.entries
    return list(entries.values()) if isinstance(entries, dict) else list(entries)


def _fidelity_slug(fidelity: FidelityGuidance) -> str:
    from harness.kanban.ticket import practice_key

    return f"{practice_key(fidelity.practice_guidance)}-{fidelity.name}"
