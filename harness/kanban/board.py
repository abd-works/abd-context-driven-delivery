"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import language_adapter
from harness.kanban.data import BoardData, ColumnData, HelpData
from harness.mcp.mcp_server import mcp
from cdd_guidance.practices.stages import DISCOVERY, IMPLEMENTATION, SPECIFICATION
from space.session import Session
from space.work_state import project_checkout

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.ticket import Ticket
    from space.repo.repo import Repo

BACKLOG_COLUMN = "Backlog"
COMPLETE_COLUMN = "Complete"
GENERATE = "generate"
VALIDATE = "validate"
REVIEW = "review"
# What every fidelity goes through in its stage, named as the session log names them.
STAGE_ACTIONS = (GENERATE, VALIDATE, REVIEW)
FORGE = "https://forge.abdworks.net/abd-context-driven-delivery"
FIDELITIES_WITHOUT_PAGE = ("ddd-model", "bdd-realization")
UNCHOSEN_FOLDERS = frozenset({"node_modules", "__pycache__"})


class ColumnNotFoundError(LookupError):
    """Raised when a caller names a column the board does not have. It names the column."""

    def __init__(self, column: str) -> None:
        self.column = column
        super().__init__(f"no column named {column!r} on the board")


class PracticeNotFoundError(LookupError):
    """Raised when a caller names a practice, such as clean_engineering, that the board or ticket does not have. It
    names the practice and what was searched for it."""

    def __init__(self, practice: str, within: str) -> None:
        self.practice = practice
        self.within = within
        super().__init__(f"no practice named {practice!r} on {within}")


class FidelityNotFoundError(LookupError):
    """Raised when a caller names a fidelity, such as stories-story_map, that a ticket or practice does not have. It
    names the fidelity and the ticket or practice searched, so a caller can say which request was refused."""

    def __init__(self, fidelity: str, within: str) -> None:
        self.fidelity = fidelity
        self.within = within
        super().__init__(f"no fidelity named {fidelity!r} on {within}")


@language_adapter(language="typescript")
@agent_toolset
class Board:
    """Show every work session as a ticket on a kanban: Backlog, Discovery, Specification, Implementation, and Complete."""

    # The board is read after every cdd call and every prompt, so its tools stay out of the session log.
    # Every ticket is in exactly one column; the board stores no ticket state.

    _built_practices: ClassVar[tuple[PracticeGuidance, ...] | None] = None

    def __init__(self, repo: Repo, practices: list[PracticeGuidance]) -> None:
        self._repo = repo
        self._practices = list(practices)
        self._columns = self._build_columns()

    @classmethod
    def load(cls, repo_root: Path | str) -> Board:
        """The board of the repository at repo_root, with every practice chosen."""
        from space.repo.repo import Repo

        return cls(Repo(repo_root), list(cls._every_practice()))

    @classmethod
    @tool_subject
    def current(cls) -> Board:
        """The board of the project the running call names. One cdd server answers every chat, so it reads the
        project from each request's X-CDD-Project header and runs the call inside working_on(project), which is
        what project_checkout() returns here."""
        return cls.load(project_checkout())

    @classmethod
    def _every_practice(cls) -> tuple[PracticeGuidance, ...]:
        """Built once per process: the practices do not change between tool calls, and building them took about 30 ms
        on every call."""
        if cls._built_practices is None:
            from bdd.bdd import Bdd
            from clean_engineering.clean_engineering import CleanEngineering
            from ddd.ddd import Ddd
            from stories.stories import Stories
            from ux.ux import Ux

            Board._built_practices = (Stories(), Ddd(), Ux(), CleanEngineering(), Bdd())
        return Board._built_practices

    @property
    def repo(self) -> Repo:
        return self._repo

    def worktree_of(self, ticket: str) -> Path | None:
        """The folder of the worktree that has ticket's branch checked out; none when it has no worktree."""
        return self._worktrees.get(ticket)

    @cached_property
    def _worktrees(self) -> dict[str, Path]:
        """Each branch's worktree, listed once per board read: the board is read after every call. A project that is no
        git clone has none."""
        if not self._repo.is_clone:
            return {}
        return {tree.branch: tree.path for tree in self._repo.list_worktrees()}

    @property
    def practices(self) -> list[PracticeGuidance]:
        return list(self._practices)

    @property
    def columns(self) -> list[Column]:
        return list(self._columns)

    @property
    def tickets(self) -> list[Ticket]:
        from harness.kanban.ticket import Ticket

        return [Ticket(session, self) for session in Session.all_in(self._repo.root)]

    @property
    def backlog_items(self) -> list[BacklogItem]:
        from harness.kanban.backlog_item import BacklogItem

        folder = Session.backlog_folder(self._repo.root)
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
        return self.ticket(Session.active_name(self._repo.root))

    def column(self, name: str) -> Column:
        found = next((column for column in self._columns if column.name == name), None)
        if found is None:
            raise ColumnNotFoundError(name)
        return found

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
        Session.board_file(self._repo.root).write_text(json.dumps({"wip_limits": limits}), encoding="utf-8")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def folders(self, path: str = "") -> list[str]:
        """List the folders inside path, a folder in the repository (its top when empty), as paths from the project, for a person choosing a workpath or a practice root. Installed packages, caches, and hidden folders hold no one's work, so they are left out."""
        parent = self._repo.root / path
        found = [entry for entry in parent.iterdir() if entry.is_dir() and entry.name not in UNCHOSEN_FOLDERS and not entry.name.startswith(".")]
        return sorted(entry.relative_to(self._repo.root).as_posix() for entry in found)

    @mcp
    @agent_tool
    @noSessionLog
    def help(self, practice: str, fidelity: str = "") -> HelpData:
        """Return the overview, guidance, and rules of practice, or of its fidelity when one is named, with the stage that fidelity belongs to and its page on the forge."""
        guidance = self.practice(practice)
        subject = self._fidelity_of(guidance, fidelity) if fidelity else guidance
        return {
            "practice": practice,
            "fidelity": fidelity,
            "stage": subject.stage.capitalize() if fidelity else "",
            "overview": (subject.overview or "").strip(),
            "guidance": (subject.guidance or "").strip(),
            "rules": [{"slug": rule.slug, "text": rule.body.strip()} for rule in subject.rules],
            "href": self._forge_page(practice, fidelity),
        }

    def practice(self, key: str) -> PracticeGuidance:
        """The board's practice whose folder name is key, such as clean_engineering."""
        found = next((entry for entry in self._practices if entry.key == key), None)
        if found is None:
            raise PracticeNotFoundError(key, "the board")
        return found

    def wip_limit(self, stage: str) -> int:
        return self._saved_wip_limits.get(stage, Session.default_wip)

    def to_json(self) -> BoardData:
        """Every column with its tickets or items: what the board pane and other IDEs read."""
        active = self.active
        return {
            "project": self._repo.root.name,
            "active": active.name if active else None,
            "columns": [column.to_json() for column in self._columns],
        }

    @property
    def _saved_wip_limits(self) -> dict[str, int]:
        path = Session.board_file(self._repo.root)
        return json.loads(path.read_text(encoding="utf-8")).get("wip_limits", {}) if path.is_file() else {}

    def _fidelity_of(self, guidance: PracticeGuidance, name: str) -> FidelityGuidance:
        try:
            return guidance.fidelities[name]
        except KeyError as missing:
            raise FidelityNotFoundError(name, guidance.key) from missing

    def _forge_page(self, practice: str, fidelity: str) -> str:
        slug = f"{practice}-{fidelity}"
        if not fidelity or slug in FIDELITIES_WITHOUT_PAGE:
            return f"{FORGE}/context-tools/{practice}.html"
        return f"{FORGE}/fidelities/{slug}.html"

    def _build_columns(self) -> list[Column]:
        # The stage names come from the one place a fidelity's **Stage:** is read against, written as column titles.
        stages = [Stage(name.capitalize(), self, list(STAGE_ACTIONS)) for name in (DISCOVERY, SPECIFICATION, IMPLEMENTATION)]
        return [Backlog(self), *stages, Column(COMPLETE_COLUMN, self)]


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
        super().__init__(BACKLOG_COLUMN, board)

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
    def work_required(self) -> list[FidelityGuidance]:
        """Every fidelity of every chosen practice whose stage is this stage, in practice order."""
        stage = self.name.lower()
        return [fidelity for practice in self._board.practices for fidelity in practice.fidelities if fidelity.stage == stage]

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
        in_progress, done = self.in_progress, self.done
        return {
            "name": self.name,
            "work_required": [self._slug(fidelity) for fidelity in self.work_required],
            "formats": {self._slug(fidelity): list(fidelity.outputs) for fidelity in self.work_required},
            "default_formats": {self._slug(fidelity): fidelity.default_format for fidelity in self.work_required},
            "wip_limit": self.wip_limit,
            "is_over_limit": len(in_progress) + len(done) > self.wip_limit,
            "in_progress": [ticket.to_json() for ticket in in_progress],
            "done": [ticket.to_json() for ticket in done],
        }

    def _slug(self, fidelity: FidelityGuidance) -> str:
        return f"{fidelity.practice_guidance.key}-{fidelity.name}"


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
