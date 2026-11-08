"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.chat.chat import Chat
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.installation.data_class import data_field, identity, language_adapter
from harness.mcp.mcp_server import mcp
from harness.guidance.stages import STAGES, ApproachStage, StageScope
from space.kanban.format_choice import FormatGroup
from space.repo.repo import Repo
from space.session.session_log import LogTimestamp
from space.session.session import MAIN_SESSION_NAME
from space.session.sessions import Sessions

if TYPE_CHECKING:
    from space.kanban.backlog_item import BacklogItem
    from space.kanban.ticket import Ticket
    from space.repo.repo import Branch
    from space.repo.worktree import Worktree
    from space.session import Session

BACKLOG_COLUMN = "Backlog"
COMPLETE_COLUMN = "Complete"
# How many tickets a stage holds before its count shows as over its limit, until a person sets another.
DEFAULT_WIP_LIMIT = 3
# The file in `.sessions` that holds what the sessions share on the board, such as each stage's work-in-progress limit.
_BOARD_FILE = "_board.json"
# Where the catalog is published; the catalog generator names each page in it.
FORGE = "https://forge.abdworks.net/abd-context-driven-delivery"


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


    # The kinds of card a board places: ticket.py and backlog_item.py build on this module, so the kanban package hands
    # their classes to the board when it is imported (``places_cards``), and this module imports neither back.
    _ticket_kind: ClassVar[type[Ticket]]
    _backlog_item_kind: ClassVar[type[BacklogItem]]

    def __init__(self, repo: Repo, practices: list[PracticeGuidance]) -> None:
        self._repo = repo
        # The sessions of the board's repository, as this process holds them: each one a ticket, and which is open.
        self._sessions = Sessions.of_project(repo.root)
        self._practices = list(practices)
        self._columns = self._build_columns()
        self._reads = BoardReads(self)

    @classmethod
    def places_cards(cls, ticket_kind: type[Ticket], backlog_item_kind: type[BacklogItem]) -> None:
        """Make every board place its sessions as tickets of ticket_kind and its ideas as items of backlog_item_kind."""
        cls._ticket_kind = ticket_kind
        cls._backlog_item_kind = backlog_item_kind

    @classmethod
    @tool_subject
    def load(cls, project: Path | str) -> Board:
        """The board of project, with every practice chosen; a tool call is handed the project the call names. A chat
        in a ticket's worktree reads the board of the project's main checkout, where every ticket's session lives."""
        return cls(Sessions.of_project(project).repo.main_clone, list(PracticeCatalogue.practices()))

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    def sessions(self) -> Sessions:
        return self._sessions

    @property
    def file(self) -> Path:
        """The file that holds what this repository's sessions share on the board."""
        return self.sessions.folder / _BOARD_FILE

    def wip_limit(self, stage: Stage) -> int:
        """How many tickets stage holds before its count shows as over its limit: the one a person set, else the default."""
        return self._shared.get("wip_limits", {}).get(stage.name, DEFAULT_WIP_LIMIT)

    def set_wip_limit(self, stage: Stage, limit: int) -> None:
        """Keep stage's limit in the board's file beside the other stages' limits and whatever else the sessions share there."""
        shared = self._shared
        shared["wip_limits"] = {**shared.get("wip_limits", {}), stage.name: limit}
        self.file.write_text(json.dumps(shared), encoding="utf-8")

    @cached_property
    def _shared(self) -> dict:
        """Everything the board's file holds, read once per board read; the board is its one reader and writer."""
        path = self.file
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    @property
    @data_field
    def project(self) -> str:
        return self._repo.root.name

    @property
    def worktrees(self) -> dict[Branch, Worktree]:
        """Each branch's worktree, listed once per board read rather than once per ticket: the board is read after every
        call. A project that is no clone has none."""
        return self._reads.worktrees

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
    @data_field
    def format_groups(self) -> list[FormatGroup]:
        """The groups a person picks formats by, each with its formats, so the page sorts a fidelity's files by group."""
        return FormatGroup.every()

    @property
    def chats(self) -> list[Chat]:
        """The chats connected now, listed once per board read, so each ticket finds the one working on it."""
        return self._reads.chats

    @property
    def tickets(self) -> list[Ticket]:
        """Every session's ticket, made once per board read: each column, and each ticket's own reads, ask for them."""
        return self._reads.tickets

    @property
    def backlog_items(self) -> list[BacklogItem]:
        return self._reads.backlog_items

    def ticket_of(self, session: Session) -> Ticket:
        """The ticket of session, which was just opened, moved between folders, closed, or reopened: the board forgets
        the cards it has read, so its next read sees the change."""
        self.reread()
        return self._ticket_kind(session, self)

    def backlog_item_of(self, ticket: Ticket) -> BacklogItem:
        """The item ticket becomes in the Backlog once its session's folder has moved there: the board forgets the cards
        it has read, so its next read sees the item."""
        self.reread()
        return self._backlog_item_kind.from_ticket(ticket)

    def reread(self) -> None:
        """Forget the tickets, backlog items, worktrees, and chats read so far, so the next read sees a change made since."""
        self._reads = BoardReads(self)

    @property
    def cards(self) -> list[Card]:
        return [*self.tickets, *self.backlog_items]

    @property
    @data_field(reference=True)
    def open_tickets(self) -> list[Ticket]:
        """The tickets a person can switch to, in the board's column order: each in a stage, so neither a backlog item
        nor a closed ticket. Sent by their names, since their columns send them."""
        return [card for column in self._columns if isinstance(column, Stage) for card in column.cards]

    @property
    @data_field(reference=True)
    def active(self) -> Ticket | None:
        """The ticket of the session saved as open; none while main is, since main is not on the board. Sent by its
        name, since its column sends the ticket."""
        return self.ticket(self.sessions.open_name)

    def column(self, name: str) -> Column:
        found = next((column for column in self._columns if column.name == name), None)
        if found is None:
            raise ColumnNotFoundError(name)
        return found

    def ticket(self, name: str) -> Ticket | None:
        """The ticket called name, open before closed, read from its own session folder: a tool names one ticket, so
        the board reads no other session to find it. The main session works on the whole repository and is no ticket."""
        session = self.sessions.named(name) if name != MAIN_SESSION_NAME else None
        return self._ticket_kind(session, self) if session is not None else None

    def backlog_item(self, title: str) -> BacklogItem | None:
        return next((item for item in self.backlog_items if item.title == title), None)

    def open_ticket(self, title: str, scope: str, parent: str, path: str) -> Ticket:
        """A new ticket titled title in Discovery, its session working on path, a folder in the repository (its top when
        empty)."""
        root = self._repo.root
        workpath = (root / path).resolve() if path else root
        return self.ticket_of(self.sessions.create(title, workpath, title=title, scope=scope, parent=parent))

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
        return sorted(entry.path for entry in self.sessions.file_manager.list(path).folders)

    @mcp
    @agent_tool
    @noSessionLog
    def help(self, practice: str) -> Help:
        """Return the overview, guidance, and shared rules of the board's practice named practice, such as stories or clean_engineering, with its page on the forge. A fidelity's help comes from its progress on a ticket: fidelity-progress.help."""
        return Help(self.practice(practice), None, None)

    def works_through(self, practice: PracticeGuidance) -> bool:
        """Whether practice, the board's own or a ticket's session's instance of it, is one the board's tickets work
        through."""
        return any(type(chosen) is type(practice) for chosen in self._practices)

    def practice(self, key: str) -> PracticeGuidance:
        """The board's practice whose folder name is key, such as clean_engineering."""
        found = next((entry for entry in self._practices if entry.key == key), None)
        if found is None:
            raise PracticeNotFoundError(key, "the board")
        return found

    def _build_columns(self) -> list[Column]:
        return [Backlog(self), *(Stage(stage, self) for stage in STAGES), Complete(self)]


class BoardReads:
    """What one read of a board finds: its tickets, its backlog items, its worktrees, and the chats connected, each read
    once when first asked for. The board replaces it whole when it reads again."""

    def __init__(self, board: Board) -> None:
        self._board = board

    @cached_property
    def tickets(self) -> list[Ticket]:
        board = self._board
        return [board._ticket_kind(session, board) for session in board.sessions.all()]

    @cached_property
    def backlog_items(self) -> list[BacklogItem]:
        board = self._board
        folder = board.sessions.backlog_folder
        if not folder.is_dir():
            return []
        # An item is a file in the Backlog, or a folder holding a file of its own name: a ticket moved back keeps its
        # whole folder, history and all. A folder beside a file of its name is that file's ticket, not a second item.
        files = list(folder.glob("*.md"))
        kept = [entry / f"{entry.name}.md" for entry in folder.iterdir() if entry.is_dir() and not (folder / f"{entry.name}.md").exists()]
        found = sorted([*files, *(path for path in kept if path.is_file())], key=lambda path: path.stem)
        return [board._backlog_item_kind(path, board) for path in found]

    @cached_property
    def chats(self) -> list[Chat]:
        return Chat.list()

    @cached_property
    def worktrees(self) -> dict[Branch, Worktree]:
        repo = self._board.repo
        if not repo.is_clone:
            return {}
        return {tree.branch: tree for tree in repo.worktrees if tree.branch is not None}


@identity("name")
class Column:
    """*Column* is one place on the board: Backlog, a stage, or Complete."""

    def __init__(self, name: str, kind: str, board: Board) -> None:
        self._name = name
        self._kind = kind
        self._board = board

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def kind(self) -> str:
        """backlog, stage, or complete, so a reader of the board knows which fields the column sends."""
        return self._kind

    @property
    def cards(self) -> list[Card]:
        return [card for card in self._board.cards if card.column is self]


class Backlog(Column):
    """*Backlog* is the first column: the ideas a person has added to the backlog folder."""

    def __init__(self, board: Board) -> None:
        super().__init__(BACKLOG_COLUMN, "backlog", board)

    @property
    @data_field
    def items(self) -> list[BacklogItem]:
        return list(self.cards)


class Complete(Column):
    """*Complete* is the last column: the tickets whose sessions are closed."""

    def __init__(self, board: Board) -> None:
        super().__init__(COMPLETE_COLUMN, "complete", board)

    @property
    @data_field
    def tickets(self) -> list[Ticket]:
        return list(self.cards)


@language_adapter(language="typescript")
@agent_toolset
class Stage(Column):
    """Show one stage of the board, the tickets at work in it, and how many it takes before it is over its limit."""

    # It is a column made for one stage of the approach, which says its scope and the actions run on a fidelity in it.
    # Every chosen practice's fidelity for the stage goes through its steps. Its WIP limit is kept by the board, in
    # the board's file, `.sessions/_board.json`, beside the other stages' limits.

    def __init__(self, approach: ApproachStage, board: Board) -> None:
        super().__init__(approach.title, "stage", board)
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
    def actions_with_formats(self) -> list[str]:
        """The actions whose command takes the formats an action bar's chips pick, generate and render."""
        return self._approach.actions_with_formats

    @property
    @data_field
    def work_required(self) -> list[FidelityGuidance]:
        """Every fidelity of every chosen practice whose stage is this stage, in practice order."""
        return [fidelity for practice in self._board.practices for fidelity in practice.fidelities if self.requires(fidelity)]

    def requires(self, fidelity: FidelityGuidance) -> bool:
        """Whether fidelity's work is done in this stage, whichever session holds it: it is a fidelity of a practice the
        board works through, and its approach stage is this stage's."""
        return fidelity.approach_stage is self._approach and self._board.works_through(fidelity.practice_guidance)

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
        return self._board.wip_limit(self)

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
        self._board.set_wip_limit(self, limit)
        return self


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
        return str(LogTimestamp(moment))


class Help:
    """Help on a practice or one of its fidelities: the guidance itself, which sends its own overview, guidance, and
    rules, with the fidelity's stage and its page on the forge."""

    def __init__(self, practice: PracticeGuidance, fidelity: FidelityGuidance | None, stage: Stage | None) -> None:
        self._practice = practice
        self._fidelity = fidelity
        self._stage = stage

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
    def href(self) -> str:
        """Its page on the forge, as the catalog generator names it: a fidelity's own page, or its practice's page for
        a fidelity the catalog has no page for."""
        from harness.catalog_generator.catalog_generator import CatalogPractice

        catalogued = CatalogPractice(self._practice)
        has_page = self._fidelity is not None and self._fidelity in catalogued.fidelities
        return f"{FORGE}/{catalogued.fidelity_href(self._fidelity) if has_page else catalogued.href}"
