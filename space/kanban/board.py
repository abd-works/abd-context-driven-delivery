"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.guidance.rule import Rule
from harness.installation.destination import data_field, identity, language_adapter
from harness.mcp.mcp_server import mcp
from cdd_guidance.practices.stages import STAGES, ApproachStage, StageScope
from space.repo.repo import Repo
from space.session.session_log import SessionLog
from space.session.sessions import Sessions

if TYPE_CHECKING:
    from pathlib import Path

    from space.kanban.backlog_item import BacklogItem
    from space.kanban.ticket import Ticket
    from space.repo.repo import Branch
    from space.repo.worktree import Worktree

BACKLOG_COLUMN = "Backlog"
COMPLETE_COLUMN = "Complete"
# How many tickets a stage holds before its count shows as over its limit, until a person sets another.
DEFAULT_WIP_LIMIT = 3
# The file in `.sessions` that holds what the sessions share on the board, such as each stage's work-in-progress limit.
_BOARD_FILE = "_board.json"
FORGE = "https://forge.abdworks.net/abd-context-driven-delivery"
FIDELITIES_WITHOUT_PAGE = ("ddd-model", "bdd-realization")


class ColumnNotFoundError(LookupError):
    """Raised when a caller names a column the board does not have. It names the column."""

    def __init__(self, column: str) -> None:
        self.column = column
        super().__init__(f"no column named {column!r} on the board")


class NotAStageError(ValueError):
    """Raised when a caller names a column that is not a stage, such as the Backlog or Complete, where a stage is wanted:
    a ticket moved into it, or a WIP limit set on it."""

    def __init__(self, stage: str) -> None:
        super().__init__(f"{stage!r} is not a stage a ticket can be moved into")


class PracticeNotFoundError(LookupError):
    """Raised when a caller names a practice, such as clean_engineering, that the board or ticket does not have. It
    names the practice and what was searched for it."""

    def __init__(self, practice: str, within: str) -> None:
        self.practice = practice
        self.within = within
        super().__init__(f"no practice named {practice!r} on {within}")


class FidelityNotFoundError(LookupError):
    """Raised when a caller names a fidelity, such as stories-story-map, that a ticket or practice does not have. It
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


    def __init__(self, repo: Repo, practices: list[PracticeGuidance]) -> None:
        self._repo = repo
        self._practices = list(practices)
        self._columns = self._build_columns()

    @classmethod
    @tool_subject
    def load(cls, project: Path | str) -> Board:
        """The board of project, with every practice chosen; a tool call is handed the project the call names. A chat
        in a ticket's worktree reads the board of the project's main checkout, where every ticket's session lives."""
        checkout = Repo(Repo(project).checkout_folder).primary_root()
        return cls(Repo(checkout), list(PracticeCatalogue.practices()))

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    def sessions(self) -> Sessions:
        """The sessions of the board's repository: each one a ticket, and which is open."""
        return Sessions(self._repo.root)

    @property
    def file(self) -> Path:
        """The file that holds what this repository's sessions share on the board."""
        return self.sessions.folder / _BOARD_FILE

    @property
    @data_field
    def project(self) -> str:
        return self._repo.root.name

    @cached_property
    def worktrees(self) -> dict[Branch, Worktree]:
        """Each branch's worktree, listed once per board read rather than once per ticket: the board is read after every
        call. A project that is no git clone has none."""
        if not self._repo.is_clone:
            return {}
        return {tree.branch: tree for tree in self._repo.worktrees if tree.branch is not None}

    @property
    @data_field
    def practices(self) -> list[PracticeGuidance]:
        """The practices every ticket works through, in the order the board shows them, each with its name and colour."""
        return list(self._practices)

    @property
    @data_field
    def columns(self) -> list[Column]:
        return list(self._columns)

    @property
    def tickets(self) -> list[Ticket]:
        from space.kanban.ticket import Ticket

        return [Ticket(session, self) for session in self.sessions.all()]

    @property
    def backlog_items(self) -> list[BacklogItem]:
        from space.kanban.backlog_item import BacklogItem

        folder = self.sessions.backlog_folder
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
    @data_field
    def active(self) -> Ticket | None:
        """The ticket of the session saved as open; none while main is, since main is not on the board."""
        return self.ticket(self.sessions.open_name)

    def column(self, name: str) -> Column:
        found = next((column for column in self._columns if column.name == name), None)
        if found is None:
            raise ColumnNotFoundError(name)
        return found

    def ticket(self, name: str) -> Ticket | None:
        """The ticket called name, open before closed, read from its own session folder: a tool names one ticket, so
        the board reads no other session to find it."""
        from space.kanban.ticket import Ticket

        session = self.sessions.named(name)
        return Ticket(session, self) if session is not None else None

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
    def folders(self, path: str = "") -> list[str]:
        """List the folders inside path, a folder in the repository (its top when empty), as paths from the project, for a person choosing a workpath or a practice root. Installed packages, caches, and hidden folders hold no one's work, so they are left out."""
        return sorted(entry.path for entry in self._repo.file_manager.list(path).folders)

    @mcp
    @agent_tool
    @noSessionLog
    def help(self, slug: str) -> Help:
        """Return the overview, guidance, and rules of the practice or fidelity slug names, such as stories or stories-story-map, with the stage a fidelity belongs to and its page on the forge."""
        for practice in self._practices:
            if practice.slug == slug:
                return Help(practice, None, None)
            fidelity = next((entry for entry in practice.fidelities if entry.slug == slug), None)
            if fidelity is not None:
                return Help(practice, fidelity, self._stage_requiring(fidelity))
        raise PracticeNotFoundError(slug, "the board")

    def _stage_requiring(self, fidelity: FidelityGuidance) -> Stage | None:
        return next((column for column in self._columns if isinstance(column, Stage) and fidelity in column.work_required), None)

    def practice(self, key: str) -> PracticeGuidance:
        """The board's practice whose folder name is key, such as clean_engineering."""
        found = next((entry for entry in self._practices if entry.key == key), None)
        if found is None:
            raise PracticeNotFoundError(key, "the board")
        return found

    def _build_columns(self) -> list[Column]:
        return [Backlog(self), *(Stage(stage, self) for stage in STAGES), Complete(self)]


@identity("name")
class Column:
    """*Column* is one place on the board: Backlog, a stage, or Complete."""

    def __init__(self, name: str, board: Board) -> None:
        self._name = name
        self._board = board

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    def cards(self) -> list[Card]:
        return [card for card in self._board.cards if card.column is self]


class Backlog(Column):
    """*Backlog* is the first column: the ideas a person has added to the backlog folder."""

    def __init__(self, board: Board) -> None:
        super().__init__(BACKLOG_COLUMN, board)

    @property
    @data_field
    def items(self) -> list[BacklogItem]:
        return list(self.cards)


class Complete(Column):
    """*Complete* is the last column: the tickets whose sessions are closed."""

    def __init__(self, board: Board) -> None:
        super().__init__(COMPLETE_COLUMN, board)

    @property
    @data_field
    def tickets(self) -> list[Ticket]:
        return list(self.cards)


@language_adapter(language="typescript")
@agent_toolset
class Stage(Column):
    """Show one stage of the board, the tickets at work in it, and how many it takes before it is over its limit."""

    # It is a column made for one stage of the approach, which says its scope and the actions run on a fidelity in it.
    # Every chosen practice's fidelity for the stage goes through its steps. The stage keeps its own WIP limit in the
    # board's file, `.sessions/_board.json`, beside the other stages' limits.

    def __init__(self, approach: ApproachStage, board: Board) -> None:
        super().__init__(approach.title, board)
        self._approach = approach

    @classmethod
    @tool_subject
    def load(cls, stage: str, *, project: Path | str) -> Stage:
        """The stage named stage, such as Discovery, on the board of project."""
        found = Board.load(project).column(stage)
        if not isinstance(found, Stage):
            raise NotAStageError(stage)
        return found

    @property
    def steps(self) -> list[str]:
        """What every fidelity goes through in this stage, in order: generate, validate, and review."""
        return self._approach.steps

    @property
    @data_field
    def scope(self) -> StageScope:
        """How much of the solution the stage's work covers, which the board draws as its shape."""
        return self._approach.scope

    @property
    @data_field
    def actions(self) -> list[str]:
        """Every action a person can run on a fidelity in this stage: its steps first, then the others."""
        return self._approach.actions

    @property
    @data_field
    def producing_actions(self) -> list[str]:
        """The actions that write a fidelity's files, which an action bar offers with formats."""
        return self._approach.producing_actions

    @property
    @data_field
    def work_required(self) -> list[FidelityGuidance]:
        """Every fidelity of every chosen practice whose stage is this stage, in practice order."""
        return [fidelity for practice in self._board.practices for fidelity in practice.fidelities if fidelity.stage == self._approach.name]

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
    @data_field
    def wip_limit(self) -> int:
        return self._saved_wip_limits.get(self.name, DEFAULT_WIP_LIMIT)

    @property
    @data_field
    def is_over_limit(self) -> bool:
        return len(self.cards) > self.wip_limit

    @property
    @data_field
    def in_progress(self) -> list[Ticket]:
        return [ticket for ticket in self.cards if not ticket.is_done]

    @property
    @data_field
    def done(self) -> list[Ticket]:
        return [ticket for ticket in self.cards if ticket.is_done]

    @mcp
    @agent_tool
    @noSessionLog
    def set_wip_limit(self, limit: int) -> Stage:
        """Set how many tickets this stage holds before its count shows as over its limit."""
        limits = {**self._saved_wip_limits, self.name: limit}
        self._board.file.write_text(json.dumps({"wip_limits": limits}), encoding="utf-8")
        return self

    @property
    def _saved_wip_limits(self) -> dict[str, int]:
        """Every stage's limit a person has set, by stage name: one file holds them all."""
        path = self._board.file
        return json.loads(path.read_text(encoding="utf-8")).get("wip_limits", {}) if path.is_file() else {}


class Card(ABC):
    """*Card* is anything on the board that a person moves: a ticket or a backlog item."""

    def __init__(self, board: Board) -> None:
        self._board = board

    @property
    def board(self) -> Board:
        return self._board

    @property
    @data_field
    @abstractmethod
    def title(self) -> str: ...

    @property
    @abstractmethod
    def column(self) -> Column: ...

    @property
    @data_field
    @abstractmethod
    def last_activity(self) -> str: ...

    @abstractmethod
    def move_next(self) -> Card: ...

    @abstractmethod
    def move_previous(self) -> Card: ...

    def _timestamp(self, moment: datetime) -> str:
        return SessionLog.timestamp(moment)


class Help:
    """The overview, guidance, and rules of a practice or one of its fidelities, with its stage and its page on the forge."""

    def __init__(self, practice: PracticeGuidance, fidelity: FidelityGuidance | None, stage: Stage | None) -> None:
        self._practice = practice
        self._fidelity = fidelity
        self._stage = stage

    @property
    def _subject(self) -> PracticeGuidance | FidelityGuidance:
        return self._fidelity or self._practice

    @property
    @data_field
    def practice(self) -> PracticeGuidance:
        """The practice this help is about, or whose fidelity it is about."""
        return self._practice

    @property
    @data_field
    def fidelity(self) -> FidelityGuidance | None:
        """The fidelity this help is about; none on a practice's help."""
        return self._fidelity

    @property
    @data_field(reference=True)
    def stage(self) -> Stage | None:
        """The stage the fidelity belongs to, such as Discovery; none on a practice's help."""
        return self._stage

    @property
    @data_field
    def overview(self) -> str:
        return (self._subject.overview or "").strip()

    @property
    @data_field
    def guidance(self) -> str:
        return (self._subject.guidance or "").strip()

    @property
    @data_field
    def rules(self) -> list[Rule]:
        return list(self._subject.rules)

    @property
    @data_field
    def href(self) -> str:
        """Its page on the forge: a fidelity's own page, or its practice's page for a fidelity the forge has none for."""
        page = f"{self._practice.key}-{self._fidelity.name}" if self._fidelity else ""
        if not page or page in FIDELITIES_WITHOUT_PAGE:
            return f"{FORGE}/context-tools/{self._practice.key}.html"
        return f"{FORGE}/fidelities/{page}.html"
