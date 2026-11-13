"""The session kanban: a board of columns, the stages work moves through, and the backlog."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.catalog_generator.catalog_examples import CatalogFidelity
from harness.chat.chat import Chat
from harness.diagnostics.app import App
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.installation.data_class import data_field, identity, language_adapter
from harness.installation.json_file import JsonFile
from harness.mcp.mcp_server import mcp
from harness.guidance.stages import STAGES, ApproachStage, StageScope
from space.repo.repo import Repo
from space.session.session_log import LogTimestamp
from space.session.session_saves import SaveFailure
from space.session.sessions import BoardPractices, Sessions

if TYPE_CHECKING:
    from harness.catalog_generator.catalog_practice import CatalogPractice
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


class FidelityNotFoundError(LookupError):
    """Raised when a caller names a fidelity, such as stories-story-map, that a ticket or practice does not have. It
    names the fidelity and the ticket or practice searched, so a caller can say which request was refused."""

    def __init__(self, fidelity: str, within: str) -> None:
        self.fidelity = fidelity
        self.within = within
        super().__init__(f"no fidelity named {fidelity!r} on {within}")


class TicketNotFoundError(LookupError):
    """Raised when a tool names a ticket the board does not show."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"no ticket named {ticket!r} on the board")


class BacklogItemNotFoundError(LookupError):
    """Raised when a tool names a backlog item the board does not show."""

    def __init__(self, backlog_item: str) -> None:
        super().__init__(f"no backlog item titled {backlog_item!r} on the board")


class CardNotInColumnError(ValueError):
    """Raised when a card is to be placed before another, and either is not a card of its own in the column."""

    def __init__(self, card: str, column: str) -> None:
        super().__init__(f"{card!r} is not a card of its own in {column}")


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

    def __init__(self, repo: Repo, practices: BoardPractices) -> None:
        self._repo = repo
        # The sessions of the board's repository, as this process holds them: each one a ticket, and which is open.
        self._sessions = Sessions.of_project(repo.root)
        # The catalog's view of each practice the board works through, which names its pages and its fidelities' skills,
        # held for the checkout by its sessions, since a board is made for every call. Its stages and tickets ask it.
        self.catalogued_practices = practices
        self._stages = [Stage(stage, self) for stage in STAGES]
        self._columns: list[Column] = [Backlog(self), *self._stages, Complete(self)]
        self._reads = BoardReads(self)

    @classmethod
    def places_cards(cls, ticket_kind: type[Ticket], backlog_item_kind: type[BacklogItem]) -> None:
        """Make every board place its sessions as tickets of ticket_kind and its ideas as items of backlog_item_kind."""
        cls._ticket_kind = ticket_kind
        cls._backlog_item_kind = backlog_item_kind

    @classmethod
    @tool_subject
    def load(cls, project: Path | str) -> Board:
        """The board of project, with every practice chosen; a tool call is handed the project the call names, the folder
        the calling chat works in. Every checkout's board lists the repository's own ``.sessions``."""
        sessions = Sessions.of_project(project)
        return cls(sessions.repo, sessions.board_practices)

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
        JsonFile(self.file).write(shared)

    def order_in(self, column: Column) -> list[str]:
        """The keys of column's cards in the order a person last placed them; none before they have placed any."""
        return list(self._shared.get("order", {}).get(column.name, []))

    def keep_order(self, column: Column, keys: list[str]) -> None:
        """Keep column's cards in the order keys gives them, in the board's file beside whatever else it holds."""
        shared = self._shared
        shared["order"] = {**shared.get("order", {}), column.name: list(keys)}
        JsonFile(self.file).write(shared)

    @property
    @data_field
    def sends_fixes_directly(self) -> bool:
        """Whether a report's Fix sends straight to the ticket's chat as a message, rather than putting it in the chat's
        prompt for a person to edit before sending: set once for the repository, in the board's file, and off until a
        person turns it on."""
        return bool(self._shared.get("sends_fixes_directly", False))

    @property
    @data_field
    def unsaved(self) -> SaveFailure | None:
        """The latest save of the tickets' records on main that git refused, such as a push origin would not take,
        naming each change not yet saved; none while every save went through. The changes are on disk, so the board
        works on them, and save_again commits and pushes them."""
        return self.sessions.saves.failure

    @cached_property
    def _shared(self) -> dict:
        """Everything the board's file holds, read once per board read; the board is its one reader and writer."""
        return JsonFile(self.file).read()

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
    def branches(self) -> list[Branch]:
        """Every local branch, listed once per board read rather than once per ticket, so each ticket finds its own."""
        return self._reads.branches

    @property
    @data_field
    def practices(self) -> list[PracticeGuidance]:
        """The practices every ticket works through, in the order the board shows them, each with its name and colour."""
        return [catalogued.practice for catalogued in self.catalogued_practices.catalogued]

    @property
    @data_field
    def columns(self) -> list[Column]:
        return list(self._columns)

    @property
    def stages(self) -> list[Stage]:
        """The columns work moves through, Discovery to Implementation, in order."""
        return list(self._stages)

    def stage(self, name: str) -> Stage:
        """The stage called name, such as Discovery; refuses any other column with ``NotAStageError``."""
        found = next((stage for stage in self._stages if stage.name == name), None)
        if found is None:
            raise NotAStageError(name)
        return found

    @property
    @data_field
    def fidelities(self) -> list[BoardFidelity]:
        """Every fidelity of the board's practices with its practice, its label, and its skill's slash command, as the
        catalog names them, so a tile shows them without taking the fidelity's slug apart. The board sends each
        fidelity once, here."""
        return [BoardFidelity(catalogued, shown) for catalogued in self.catalogued_practices.catalogued for shown in catalogued.shown_fidelities]

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
        return self.make_ticket(session)

    def make_ticket(self, session: Session) -> Ticket:
        """The ticket this board places for session, as it reads it now."""
        return self._ticket_kind(session, self)

    def make_backlog_item(self, path: Path) -> BacklogItem:
        """The backlog item this board places for the idea kept in path, a file in the Backlog folder."""
        return self._backlog_item_kind(path, self)

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
        return [card for stage in self._stages for card in stage.cards]

    @property
    @data_field
    def active(self) -> Ticket | None:
        """The ticket of the session saved as open, main's own ticket while main is. Sent whole, so
        a reader such as the chat bar draws the active session from it without finding the ticket again by its name."""
        return self.ticket(self.sessions.open_name)

    def column(self, name: str) -> Column:
        found = next((column for column in self._columns if column.name == name), None)
        if found is None:
            raise ColumnNotFoundError(name)
        return found

    def ticket(self, name: str) -> Ticket | None:
        """The ticket called name, open before closed, read from its own session folder: a tool names one ticket, so
        the board reads no other session to find it. Main, the default session, is a ticket like any other."""
        session = self.sessions.named(name)
        return self.make_ticket(session) if session is not None else None

    def ticket_called(self, name: str) -> Ticket:
        """The ticket called name, as ``ticket`` reads it; raises ``TicketNotFoundError`` when the board has none."""
        found = self.ticket(name)
        if found is None:
            raise TicketNotFoundError(name)
        return found

    def children_of(self, ticket: Ticket) -> list[Ticket]:
        """The tickets whose session names ticket's as its parent, found once per board read."""
        return self._reads.children.get(ticket.name, [])

    def backlog_item(self, title: str) -> BacklogItem | None:
        return next((item for item in self.backlog_items if item.title == title), None)

    def backlog_item_called(self, title: str) -> BacklogItem:
        """The backlog item titled title; raises ``BacklogItemNotFoundError`` when the board has none."""
        found = self.backlog_item(title)
        if found is None:
            raise BacklogItemNotFoundError(title)
        return found

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
        """Return the session board: Backlog, Discovery, Specification, Implementation, and Complete, with every ticket's progress through Generate and Validate, and the active ticket."""
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def save_again(self) -> Board:
        """Commit and push again the tickets' changes whose save on main git refused, as the board's Save again does; the save runs on the saving thread, and the board shows whether it went through."""
        self.sessions.saves.retry()
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def set_sends_fixes_directly(self, sends: bool) -> Board:
        """Set whether a report's Fix sends straight to the ticket's chat as a message, or puts it in the chat's prompt to edit before sending; kept for the repository in the board's file."""
        shared = self._shared
        shared["sends_fixes_directly"] = sends
        JsonFile(self.file).write(shared)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def overview(self) -> BoardOverview:
        """Return the board as a reader that draws the active session sees it, such as the chat bar: the active ticket whole, every column with its tickets by name, the stages' actions and required fidelities by slug, and the practices' colours. It stays small however many tickets the board holds, because only the active ticket sends its progress."""
        return BoardOverview(self)

    @mcp
    @agent_tool
    @noSessionLog
    def folders(self, path: str = "") -> list[str]:
        """List the folders inside path, a folder in the repository (its top when empty), as paths from the project, for a person choosing a workpath or a practice root. Installed packages, caches, and hidden folders hold no one's work, so they are left out, apart from .context, which holds a module's models and maps and can be a practice root."""
        return sorted(entry.path for entry in self.sessions.file_manager.list(path).folders)

    @mcp
    @agent_tool
    @noSessionLog
    def help(self, practice: str) -> Help:
        """Return the overview, guidance, and shared rules of the board's practice named practice, such as stories or clean_engineering, with its page on the forge. A fidelity's help comes from its progress on a ticket: fidelity-progress.help."""
        found = self.catalogued_practices.keyed(practice)
        return Help(found.practice, None, None, found)


class BoardReads:
    """What one read of a board finds: its tickets, its backlog items, its worktrees, and the chats connected, each read
    once when first asked for. The board replaces it whole when it reads again."""

    def __init__(self, board: Board) -> None:
        self._board = board

    @cached_property
    def tickets(self) -> list[Ticket]:
        board = self._board
        return [board.make_ticket(session) for session in board.sessions.all()]

    @cached_property
    def children(self) -> dict[str, list[Ticket]]:
        """Every ticket that has a parent, under its parent's name."""
        held: dict[str, list[Ticket]] = {}
        for ticket in self.tickets:
            if ticket.session.parent:
                held.setdefault(ticket.session.parent, []).append(ticket)
        return held

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
        return [board.make_backlog_item(path) for path in found]

    @cached_property
    def chats(self) -> list[Chat]:
        return Chat.list()

    @cached_property
    def branches(self) -> list[Branch]:
        return self._board.repo.branches

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
        """The cards of its own in this column, in the order a person placed them; any not placed yet follow, in the
        order the board reads them. A child stacked inside its parent's card is not a card of its own."""
        own = [card for card in self._board.cards if card.column is self and not card.is_stacked]
        placed = self._board.order_in(self)
        return sorted(own, key=lambda card: placed.index(card.key) if card.key in placed else len(placed))

    def place_before(self, card: Card, other: Card) -> Column:
        """Put card just above other in this column, and keep that order."""
        keys = [shown.key for shown in self.cards]
        for named in (card, other):
            if named.key not in keys:
                raise CardNotInColumnError(named.key, self.name)
        if card.key == other.key:
            return self
        keys.remove(card.key)
        keys.insert(keys.index(other.key), card.key)
        self._board.keep_order(self, keys)
        return self


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
        return Board.load(project).stage(stage)

    @property
    def steps(self) -> list[str]:
        """What every fidelity goes through in this stage, in order: generate, then validate."""
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
    @data_field(reference=True)
    def work_required(self) -> list[FidelityGuidance]:
        """Every fidelity of every chosen practice whose stage is this stage, in practice order; each sent by its slug,
        since its guidance text is read through its help."""
        return [fidelity for practice in self._board.practices for fidelity in practice.fidelities if self.requires(fidelity)]

    def requires(self, fidelity: FidelityGuidance) -> bool:
        """Whether fidelity's work is done in this stage, whichever session holds it: it is a fidelity of a practice the
        board works through, and its approach stage is this stage's."""
        return fidelity.approach_stage is self._approach and self._board.catalogued_practices.works_through(type(fidelity.practice_guidance))

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

    @property
    @abstractmethod
    def key(self) -> str:
        """What names the card among the others in its column, by which the board keeps its place there."""

    @property
    def is_stacked(self) -> bool:
        """Whether it shows inside another card rather than as a card of its own: only a ticket's child does."""
        return False

    def move_before(self, other: Card) -> Card:
        """A person's move of this card just above other in their column: the column keeps that order, committed on
        main and pushed."""
        column = self.column.place_before(self, other)
        self._board.sessions.saves.later(f"sessions: move {self.key} before {other.key} in {column.name}")
        return self

    @abstractmethod
    def move_next(self) -> Card: ...

    @abstractmethod
    def move_previous(self) -> Card: ...

    def _timestamp(self, moment: datetime) -> str:
        return str(LogTimestamp(moment))


class Help:
    """Help on a practice or one of its fidelities: the guidance itself, which sends its own overview, guidance, and
    rules, with the fidelity's stage and its page on the forge."""

    def __init__(self, practice: PracticeGuidance, fidelity: FidelityGuidance | None, stage: Stage | None, catalogued: CatalogPractice) -> None:
        self._practice = practice
        self._fidelity = fidelity
        self._stage = stage
        # The catalog's view of the practice, which names every page on the forge: the one the board holds.
        self._catalogued = catalogued

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
        catalogued = self._catalogued
        return f"{FORGE}/{catalogued.fidelity_href(self._fidelity) if self._has_page else catalogued.href}"

    @property
    def _has_page(self) -> bool:
        """Whether the catalog shows the fidelity. The catalog's view is of the board's instance of the practice, and a
        ticket's fidelity is its session's instance, so it is found by its name in the practice, which is the same in
        both, as ``PracticeGuidance.fidelity_called`` finds a fidelity a person names."""
        fidelity = self._fidelity
        catalogued = self._catalogued
        return fidelity is not None and catalogued.practice.fidelity_called(fidelity.name) in catalogued.fidelities


class BoardFidelity:
    """A fidelity as a board tile names it: its label and the slash command of the skill the installer publishes for it,
    both answered by the catalog's view of its practice, so the page shows them and works out neither."""

    def __init__(self, catalogued: CatalogPractice, shown: CatalogFidelity) -> None:
        self._catalogued = catalogued
        self._shown = shown

    @property
    @data_field(reference=True)
    def fidelity(self) -> FidelityGuidance:
        """The fidelity, sent by its slug, which its tile and its progress name it by."""
        return self._shown.fidelity

    @property
    @data_field(reference=True)
    def practice(self) -> PracticeGuidance:
        """The practice it belongs to, sent by its key, so a reader holding the fidelity finds its practice."""
        return self._catalogued.practice

    @property
    @data_field
    def label(self) -> str:
        """Its name on a tile, such as story-map, or information-architecture for UX's ia."""
        return self._shown.label

    @property
    @data_field
    def skill(self) -> str:
        """The slash command of its skill, such as /practices-stories-stories-story-map."""
        return f"/{self._catalogued.skill_of(self._shown.fidelity)}"

    @property
    @data_field
    def editor(self) -> App | None:
        """The app the small editor widget on this fidelity's row of every ticket opens: its practice's editor on the
        practice's first fidelity (the Stories story map), none on every other fidelity."""
        practice = self._catalogued.practice
        return practice.editor if self._shown.fidelity is next(iter(practice.fidelities), None) else None


class BoardOverview:
    """*BoardOverview* is the board as a reader that draws the active session sees it, such as the chat bar, which reads
    it every turn through MCP, whose answers are cut off past their size limit. Only the active ticket is sent whole;
    every other ticket is named in its column, so the overview grows by a name for each ticket."""

    def __init__(self, board: Board) -> None:
        self._board = board

    @property
    @data_field
    def project(self) -> str:
        return self._board.project

    @property
    @data_field
    def practices(self) -> list[BoardPractice]:
        """The board's practices, each with the colour and short name its fidelities are drawn in."""
        return [BoardPractice(practice) for practice in self._board.practices]

    @property
    @data_field
    def fidelities(self) -> list[BoardFidelity]:
        return self._board.fidelities

    @property
    @data_field
    def columns(self) -> list[ColumnOverview]:
        return [ColumnOverview(column) for column in self._board.columns]

    @property
    @data_field
    def active(self) -> Ticket | None:
        """The ticket of the session saved as open, sent whole; none while main is."""
        return self._board.active


class BoardPractice:
    """A practice as the board draws it: its colour and short name, sent with the practice's key, without its
    guidance text, which its help reads."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self._practice = practice

    @property
    @data_field(reference=True)
    def practice(self) -> PracticeGuidance:
        return self._practice

    @property
    @data_field
    def short_name(self) -> str:
        return self._practice.short_name

    @property
    @data_field
    def colour(self) -> str:
        return self._practice.colour

    @property
    @data_field
    def editor(self) -> App | None:
        """The app that edits the practice's files, which a file of the practice opens in from the chat bar's file viewer:
        the Story UI editor for Stories; none for a practice no app edits."""
        return self._practice.editor


class ColumnOverview:
    """A column as the overview sends it: its name and kind; a stage's scope, actions, and required fidelities by slug;
    and the open tickets in it by name. Backlog and Complete hold no open ticket and run no action."""

    def __init__(self, column: Column) -> None:
        self._column = column
        self._stage = column if isinstance(column, Stage) else None

    @property
    @data_field
    def name(self) -> str:
        return self._column.name

    @property
    @data_field
    def kind(self) -> str:
        return self._column.kind

    @property
    @data_field
    def scope(self) -> StageScope | None:
        return self._stage.scope if self._stage is not None else None

    @property
    @data_field
    def actions(self) -> list[str]:
        return self._stage.actions if self._stage is not None else []

    @property
    @data_field(reference=True)
    def work_required(self) -> list[FidelityGuidance]:
        return self._stage.work_required if self._stage is not None else []

    @property
    @data_field(reference=True)
    def tickets(self) -> list[Ticket]:
        """The open tickets in the column, by name: a stage's cards; none in Backlog or Complete."""
        return list(self._stage.cards) if self._stage is not None else []
