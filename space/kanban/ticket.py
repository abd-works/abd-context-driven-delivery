"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path
from enum import Enum
from typing import TYPE_CHECKING, Callable, TypeVar

from harness.agent_tools import agent_toolset
from harness.annotations.annotation import hosted_only
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.agent_tools.tool_call import ToolCall
from harness.chat.chat import Chat, Chats
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.action_catalogue import ACTION_CATALOGUE
from harness.installation.data_class import data_field, identity, language_adapter
from harness.markdown.format import Format
from harness.mcp.mcp_annotations import long_call, mcp
from space.kanban.board import (
    RequiredFidelity,
    BACKLOG_COLUMN,
    COMPLETE_COLUMN,
    Board,
    Card,
    Column,
    FidelityNotFoundError,
    Help,
    Stage,
)
from harness.graph.location import Location
from harness.graph.violation import FoundBy, FoundOn, Violation
from space.kanban.report import Report, ReportFile
from space.kanban.ticket_choices import TicketChoices
from space.kanban.ticket_checkout import LeaveChoices, Leaving, TicketCheckout
from space.kanban.ticket_tree import NotAChildError, ParentLoopError, TicketTree
from space.repo.repo import Branch
from space.session import Session
from space.kanban.progress_cache import ACCEPTED_COUNT, HAS_OUTPUT, PROGRESS_CACHES, VIOLATION_COUNT
from space.session.session_log import LogLine
from space.session.practices.guidance_selection import GuidanceSelection
from space.session.session_record import OwnedFields
from space.session.files.file_manager import FileEntry

if TYPE_CHECKING:
    from space.kanban.backlog_item import BacklogItem

GRAPH_RULE_VIOLATION = "graph-rule"
MOVED_INTO = "move"


class StageMark(Enum):
    """The mark a person gives a ticket in a stage: done, or in progress. Its value is the word its session's log and
    session.json keep."""

    DONE = "done"
    IN_PROGRESS = "in-progress"


# The session.json fields the board keeps for a ticket: its stage and its mark there, and the files whose work its
# latest close dropped (``record.extra("ticket")``).
_STAGE_FIELD = "stage"
_DROPPED_WORK_FIELD = "dropped_work"
# What a ticket worked out about itself and keeps until it next writes something.
Remembered = TypeVar("Remembered")
_STAGE_MARK_FIELD = "stage_mark"
_TICKET_FIELDS = "ticket"


def _generate() -> str:
    """The step that writes a fidelity's files, as the session log names it: the action catalogue's writing step."""
    return ACTION_CATALOGUE.writing_step.name


def _validate() -> str:
    """The step that checks a fidelity's files, as the session log names it: the action catalogue's checking step."""
    return ACTION_CATALOGUE.checking_step.name


def _needing_output() -> list[str]:
    """The actions that check or convert a fidelity's output, so they wait until there is some."""
    return [action.name for action in ACTION_CATALOGUE.needing_output]


def _ticket_stage_of(session: Session) -> str:
    """The stage a session's ticket stands in on the board of the project whose sessions hold it, such as `Discovery`;
    empty for one that is closed."""
    column = Board.load(session.sessions.root).placement.make_ticket(session).column
    return column.name if isinstance(column, Stage) else ""


# Before anyone chose stages for a session, its guidance selection shows its ticket's stage selected.
GuidanceSelection.start_on_ticket_stage_with(_ticket_stage_of)


class TicketPrompts:
    """*TicketPrompts* are what a ticket asks its chat to do for it, each naming the ticket's session, because a prompt
    runs in whichever chat it is sent to, whose open session can be another ticket's."""

    def __init__(self, ticket: str, session_file: str) -> None:
        self._ticket = ticket
        self._session_file = session_file

    def _in_session(self, prompt: str) -> str:
        return f"{prompt} session={self._session_file}"

    @property
    @data_field
    def split(self) -> str:
        """Split the ticket into child tickets, one for each story on its story map."""
        name = self._ticket
        return self._in_session(f"Split ticket {name} into child tickets, one per story on its story map: call ticket.create with parent {name} for each story.")

    @property
    @data_field
    def handoff(self) -> str:
        return self._in_session(f"Write a handoff for ticket {self._ticket} with /space-session-handoff-session")

    @property
    @data_field
    def set_up_roots(self) -> str:
        """Propose roots for the pieces the ticket works on, in every practice, and set them once the person confirms."""
        return self._in_session(f"Set up the roots of ticket {self._ticket}'s session with session.set_up_roots")

    @property
    @data_field
    def close_session(self) -> str:
        """Close the chat's session, which leaves the ticket where it is: moving it into Complete is what completes it."""
        return self._in_session("/space:session:close-session")

    @property
    @data_field
    def new_chat(self) -> str:
        """The prompt a ticket's new chat opens with. The Claude app gives a new chat no title, so it asks for the
        ticket's, then opens the ticket's session and reads its latest handoff."""
        name = self._ticket
        return (
            f'Title this session "{name}". You are the chat of the session board\'s ticket {name}; work on that '
            f"ticket. First call sessions.switch with name {name}, so every tool works on its session, then read the "
            "session's latest handoff. When the switch says the session's roots are unchecked, set them up with "
            "session.set_up_roots before generating anything, so they cover exactly the pieces the ticket works on."
        )


class StagePlace:
    """*StagePlace* is where a move puts a ticket that stays on a stage: the stage, and whether in its Done or its In
    progress. The board sends it on each ticket for Move next and Move previous, so the page can show the card there
    the moment either is pressed, and the move itself goes where it says."""

    def __init__(self, stage: Stage, is_done: bool) -> None:
        self._stage = stage
        self._is_done = is_done

    @property
    @data_field(reference=True)
    def stage(self) -> Stage:
        """The stage, sent by its name."""
        return self._stage

    @property
    @data_field
    def is_done(self) -> bool:
        return self._is_done


@hosted_only
class TicketCheckoutTools:
    """A ticket's published checkout tools: its branches, its chat, opening it in its own worktree, and what closing it can
    do. Each asks the ticket's *TicketCheckout*."""

    checkout: TicketCheckout
    session: Session
    moves: TicketMoves
    forget_reads: Callable[[], None]

    @mcp
    @agent_tool
    @noSessionLog
    def branch(self) -> Branch:
        """Return ticket's own branch, named as the ticket: whether the repository has it yet, so activating ticket offers to create only what is missing, and whether it is checked out, so leaving ticket can commit, push, and merge its work."""
        return self.checkout.branch

    @mcp
    @agent_tool
    @noSessionLog
    def work_branch(self) -> Branch:
        """Return the branch ticket's work is on, which leaving ticket commits and pushes: its own branch while it is checked out, in the repository or in its own worktree, else the default branch while the repository has it checked out, as for a session with no branch of its own. Any other branch checked out is not ticket's, and neither is the default branch while its own branch is checked out nowhere, such as after its worktree was deleted, so its own branch comes back not checked out and leaving commits nothing."""
        return self.checkout.work_branch

    @mcp
    @agent_tool
    def assign_chat(self, chat: str = "") -> Ticket:
        """Make chat, the id of a connected chat, ticket's chat, kept in its session.json, so every command the board sends for ticket goes there and no chat named after it is looked for; an empty chat gives ticket back to the chat named after it."""
        self.session.checkout.assign_chat(chat)
        self.forget_reads()
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def close_choices(self) -> LeaveChoices:
        """Return what closing ticket can do with its work, none chosen at first, so closing does only what the person ticks: a handoff always; a commit and a push of the branch its work is on while a checkout has it, which branch names; and, for its own branch, which own_branch names, a merge into main, a delete of the branch, and a delete of its worktree while it has one. unsaved_work names the files in its worktree with changes nobody committed, and warning says deleting the worktree or branch without a commit loses them."""
        return self.checkout.close_choices

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def activate(self) -> Ticket:
        """Open ticket in its own worktree, where its own chat works on it: the worktree it has, else a new one on its own branch, made when missing, after the session folders not yet committed are committed on main and pushed. A closed ticket reopens first, as moving it out of Complete does: its folder back among the open sessions, on the stage it was closed from. Sessions open only from main: the chat that asks keeps its own session, the repository's own folder stays on main, and nothing is left or moved."""
        opened = self.moves.reopened()
        opened.checkout.open()
        opened.forget_reads()
        return opened.in_answer()



def in_answer(moved: Ticket | BacklogItem) -> Ticket | BacklogItem:
    """What a move answers with: a ticket as `Ticket.in_answer` sends it, a backlog item as it is."""
    return moved.in_answer() if isinstance(moved, Ticket) else moved

@hosted_only
class TicketMoveTools:
    """A ticket's published moves through the columns: Move next, Move previous, a drag into a stage, and a drag above
    another card. Each asks the ticket's *TicketMoves*, or the card's own order in its column."""

    moves: TicketMoves

    @mcp
    @agent_tool
    @noSessionLog
    def move_next(self) -> Ticket:
        """Move ticket on: from In progress to its stage's Done, from Done to the next column, whatever its work. Out of Hardening, the last stage, it closes, but main, the default session, stays in Hardening's Done. A ticket with children moves only with them, so it is refused."""
        return self.moves.move_next().in_answer()

    @mcp
    @agent_tool
    @noSessionLog
    def move_previous(self) -> Ticket | BacklogItem:
        """Move ticket back: from Done to its stage's In progress, from In progress to the previous column's Done. Out of Complete it reopens in Hardening, the last stage; out of Discovery it goes to the Backlog with its work, but main stays in Discovery. A ticket with children moves only with them, so it is refused."""
        return in_answer(self.moves.move_previous())

    @mcp
    @agent_tool
    @noSessionLog
    def move_to(self, stage: str, done: bool = False) -> Ticket | BacklogItem:
        """Move ticket straight into stage's In progress, or its Done when done is true, whatever its work; dragging a card does this. Out of Complete it reopens first. Into the Backlog, from any column, it becomes a backlog item that keeps its whole folder, and its children go with it, each an item of its own. Into a stage, a ticket with children moves only with them, so it is refused."""
        return in_answer(self.moves.move_to(stage, done))

    @mcp
    @agent_tool
    @noSessionLog
    def move_before(self, other: Ticket) -> Ticket:
        """Move ticket just above other, as dragging it there does. Where other is in another column, or in its stage's other list, ticket goes there first: into other's stage, In progress or Done as other is, and beside a closed ticket it closes with its work left as it is. The column keeps that order, in .sessions/_board.json. Committed on main and pushed. A ticket with children moves only with them, so a move to another column is refused."""
        beside = self.moves.move_beside(other)
        Card.move_before(beside, other)
        return beside.in_answer()


@hosted_only
class TicketTreeTools:
    """A ticket's published changes to its tree: adding a child, pulling it out of its parent, and choosing its parent,
    each kept by its session's hierarchy. Where it sits in the tree, and which parents it may take, its *TicketTree*
    answers."""

    name: str
    session: Session
    board: Board
    parent: Ticket | None
    tree: TicketTree
    forget_reads: Callable[[], None]

    @mcp
    @agent_tool
    @noSessionLog
    def add_child(self, title: str) -> Ticket:
        """Open a child ticket of ticket titled title, a story In progress in Discovery, working where ticket works. A title that gives no name, one too long, or the name of a ticket already there is refused, as for any new ticket. Committed on main and pushed."""
        placement = self.board.placement
        return placement.ticket_of(self.session.hierarchy.open_child(placement.free_name_for(title), title, scope="story"))

    @mcp
    @agent_tool
    @noSessionLog
    def pull_out(self) -> Ticket:
        """Pull ticket out of its parent: it moves on the board as a card of its own, still keeping its parent, which keeps a row for it. Committed on main and pushed."""
        if self.parent is None:
            raise NotAChildError(self.name)
        self.session.hierarchy.mark_pulled_out()
        self.forget_reads()
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def reassign_parent(self, parent: Ticket | None = None) -> Ticket:
        """Make parent ticket's parent, as dragging ticket onto it does, or none, so ticket is a ticket of its own (Alt-dragging it out of its parent); either way it is no longer pulled out. Committed on main and pushed."""
        if parent is not None and not self.session.hierarchy.can_take_parent(parent.session):
            raise ParentLoopError(self.name, parent.name)
        self.session.hierarchy.set_parent(parent.session if parent is not None else None)
        self.forget_reads()
        return self


@hosted_only
class TicketEnding:
    """*TicketEnding* is how a ticket leaves the board's stages, its endings published as its tools: closed into Complete
    after doing what the person chose with its work, archived, deleted, or shelved in the Backlog as an item that keeps
    its whole folder. Main, the default session, never leaves; each ending's move is committed on main and pushed."""

    name: str
    session: Session
    board: Board
    checkout: TicketCheckout
    board_fields: OwnedFields

    def _refuse_main(self, action: str) -> None:
        self.session.refuse_if_main(action)

    def _end_session(self) -> None:
        """End the ticket's session for the chat the board is read for: when that chat has it open, main becomes open."""
        self.board.sessions.opened.close(self.session, self.board.chat)

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def close(self, leaving: list[str] | None = None) -> Ticket:
        """Close ticket: leaving names what to do with its work first, and the close does only that (handoff, commit, push, merge, delete_branch, delete_worktree; any other is refused with UnknownLeavingStepError, before anything changes), its work committed where it is and its branch merged before anything is removed or moved, so a merge git refuses, or a worktree a running program holds open, stops the close with ticket still open; then its session ends, its record folder moves to _complete/ with the work the merge brought beside it, that move is committed on main and pushed, and it shows in Complete; a worktree deleted without a commit goes as it is, and the closed ticket's dropped_work names the files whose uncommitted work went with it. The repository's own folder stays on main, and what is uncommitted there is never committed for a ticket that has its own worktree: a merge that would run over it is refused with EditsInTheWayOfMergeError before anything changes."""
        self._refuse_main("close")
        chosen = Leaving(leaving or [])
        checkout = self.checkout
        checkout.refuse_edits_merge_would_overwrite(chosen)
        checkout.write_handoff(chosen)
        # The work is saved and the branch merged while the ticket still has its worktree and its open session, so a
        # merge git refuses leaves both as they were. The branch also merges before the record moves: the session's work
        # folder on the branch lands beside the record in main's .sessions, and the move takes both among the closed
        # sessions. Moved first, git would find the work folder added inside a folder main renamed, and refuse the merge.
        checkout.save_work(chosen)
        checkout.keep_landing_release(chosen)
        self.board_fields.save(**{_DROPPED_WORK_FIELD: checkout.leave_branch(chosen)})
        self._end_session()
        closed = self.board.placement.ticket_of(self.session.folder.move_to_closed())
        checkout.return_to_default_branch()
        self.board.sessions.saves.now(f"sessions: close {self.name}")
        return closed.in_answer()

    @mcp
    @agent_tool
    @noSessionLog
    def archive(self) -> Ticket:
        """Archive ticket: its own worktree is removed, its work committed and pushed on its branch first, which stays; then its session ends, its folder moves to _archive/, that move is committed on main and pushed, and it leaves the board. Main never archives."""
        self._refuse_main("archive")
        self.checkout.free_worktree()
        self._end_session()
        archived = self.board.placement.ticket_of(self.session.folder.move_to_archive())
        self.board.sessions.saves.now(f"sessions: archive {self.name}")
        return archived.in_answer()

    @mcp
    @agent_tool
    @noSessionLog
    def delete(self) -> None:
        """Delete ticket: its own worktree is removed, its work committed and pushed on its branch first, which stays; then its session ends and its folder, log, and files are removed, that removal committed on main and pushed, and it leaves the board. A worktree or a session folder a running program holds open refuses the delete with ticket's record still whole. Main never deletes."""
        self._refuse_main("be deleted")
        self.checkout.free_worktree()
        self.session.folder.remove()
        self._end_session()
        self.board.placement.reread()

    def to_backlog(self) -> BacklogItem:
        """Into the Backlog from any column: its session closes and its whole folder becomes a backlog item, so starting
        the item brings the ticket back with its work. Its children go first, each an item of its own that still names
        it as its parent, so starting its item starts theirs."""
        self._refuse_main("go to the Backlog")
        for child in self.children:
            child.to_backlog()
        self._end_session()
        kept_in_backlog = self.board.placement.ticket_of(self.session.folder.move_to_backlog())
        return self.board.placement.backlog_item_of(kept_in_backlog)


@hosted_only
class TicketTextTools:
    """A ticket's published edits to what its session says about its work: its text and its tags, each kept by its session.
    Main, the default session, is no one piece of work, so it takes neither."""

    session: Session
    forget_reads: Callable[[], None]
    _refuse_main: Callable[[str], None]

    @mcp
    @agent_tool
    @noSessionLog
    def edit_text(self, text: str) -> Ticket:
        """Write text as what ticket's work is about, in the idea file its session folder keeps, <name>.md, under its heading; the file is made when ticket has none. Committed on main and pushed. Main, the default session, is refused."""
        self._refuse_main("have its text edited")
        self.session.keep_text(text)
        self.forget_reads()
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def tag(self, word: str) -> Ticket:
        """Tag ticket's session with word, kept in its session.json beside its other tags. Committed on main and pushed. Main, the default session, is refused."""
        self._refuse_main("be tagged")
        self.session.add_tag(word)
        self.forget_reads()
        return self


@identity("name")
@language_adapter(language="typescript")
@agent_toolset
class Ticket(TicketCheckoutTools, TicketChoices, TicketMoveTools, TicketTreeTools, TicketEnding, TicketTextTools, Card):
    """Show one work session as a unit of delivery and move it through the stages."""

    # It works with its session, which holds its folders, practices, and files, and the board it sits on, and holds
    # parts made once: its work (its progress on each fidelity the board requires), its checkout (its branch and
    # worktree), its stage marks (the moves and marks a person made), its tree (where it sits among its parent and
    # children), and its moves (Move next, Move previous, a drag). Its tools are declared by job on the bases mixed in
    # ahead of Card, so the toolset still publishes them as ticket's: the checkout, move, and text tools ask a part or
    # its session; the choices (the files and chips it offers), the tree changes, and the ending (closing, archiving,
    # deleting, or shelving it in the Backlog) do their own work, with no part behind them to forward to.
    # Never moves to another column by itself: a person moves it, and the move is written to its session log.
    # The board is read after every cdd call, so these tools stay out of the session log; a move writes its own line.
    # Its tools and data fields keep their published names (.context/cdr/0004).

    def __init__(self, session: Session, board: Board) -> None:
        super().__init__(board)
        self._session = session
        self.work = TicketWork(self)
        self.checkout = TicketCheckout(self)
        self.marks = StageMarks(self)
        self.tree = TicketTree(self)
        self.moves = TicketMoves(self)
        # What it has worked out about itself so far, such as its column, its parent, and whether it is done: one answer
        # asks each many times, for every column, mark, and drop target. Forgotten whenever the ticket writes anything.
        self._remembered: dict[str, object] = {}

    def _remember(self, name: str, read: Callable[[], Remembered]) -> Remembered:
        """What read answers, worked out once until the ticket next writes something (``forget_reads``)."""
        if name not in self._remembered:
            self._remembered[name] = read()
        return self._remembered[name]

    def forget_reads(self) -> None:
        """Forget what the ticket worked out about itself, since it has just written a change to its session."""
        self._remembered = {}

    @classmethod
    @tool_subject
    def load(cls, ticket: str, *, project: Path | str, call: ToolCall | None = None) -> Ticket:
        """The ticket named ticket on the board of project, read for call from its own session alone."""
        return Board.load(project, call).placement.ticket_called(ticket)

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def create(cls, title: str, scope: str = "feature", parent: str = "", path: str = "", *, project: Path | str, call: ToolCall | None = None) -> Ticket:
        """Open a new ticket titled title in Discovery, its record committed on main and pushed. scope is feature, story, or slice; parent names the ticket it was split from; path is the folder in the repository its session works on. Then run ticket.activate to open the ticket's own worktree, and do its work in a chat started there (start_session with cwd set to the ticket's worktree), not in this chat."""
        board = Board.load(project, call)
        opened = board.placement.open_ticket(title, scope, path)
        if parent:
            opened.session.hierarchy.set_parent(board.sessions.named(parent))
        return opened

    @property
    @data_field
    def name(self) -> str:
        """Its session's name. A ticket is an agent toolset, whose own name is the toolset's, so without this a
        ticket's name would read "ticket"."""
        return self._session.name

    @property
    @data_field
    def is_main(self) -> bool:
        """Whether this is main, the default session: every chat in the repository's own folder works on it, and it
        never closes, archives, or goes to the Backlog."""
        return self._session.is_main

    @property
    def title(self) -> str:
        """Its session's title, or its name when it has none; a child pulled out of its parent is titled under the
        parent's, as Checkout flow.Enter card details."""
        own = self._session.title or self._session.name
        parent = self.parent if self.is_pulled_out else None
        return f"{parent.title}.{own}" if parent is not None else own

    @property
    def key(self) -> str:
        return self.name

    @property
    @data_field
    def text(self) -> str:
        """What its work is about: the text of the idea file its session folder keeps; empty while it has none."""
        return self._session.text

    @property
    @data_field
    def tags(self) -> list[str]:
        """The words a person tagged its session with."""
        return self._session.tags

    @property
    def parent(self) -> Ticket | None:
        """The ticket its session names as its parent; none when it names none, or one the board does not have."""
        return self._remember("parent", self._read_parent)

    def _read_parent(self) -> Ticket | None:
        named = self._session.parent
        return self._board.placement.ticket(named) if named else None

    @property
    @data_field
    def children(self) -> list[Ticket]:
        """The tickets whose session names this one's as their parent: stacked inside its card, or, pulled out, cards of
        their own it keeps a row for. Sent whole, since a stacked child shows in no column."""
        return self._board.reads.children_of(self)

    @property
    @data_field
    def is_pulled_out(self) -> bool:
        """Whether this child moves on the board as a card of its own, still keeping its parent."""
        return self._session.hierarchy.is_pulled_out

    @property
    @data_field
    def is_stacked(self) -> bool:
        """Whether it shows inside its parent's card rather than as a card of its own: an open child, not pulled out, of
        an open parent."""
        return self.tree.is_stacked

    @property
    @data_field
    def session(self) -> Session:
        """The work session this ticket shows: its folders, its practices and their files, and its log."""
        return self._session

    @property
    @data_field
    def progress(self) -> list[FidelityProgress]:
        """One per fidelity the board requires, in stage order, each naming its fidelity; read from the session log once
        per ticket read, with the latest report's judgment able to fail a validate the log shows passing."""
        return list(self.work.progress)

    @property
    @data_field(reference=True)
    def column(self) -> Column:
        """Complete once closed; otherwise the stage of the fidelity its latest generate or validate names, unless a
        person moved it since, which holds until the next generate or validate: the stage follows the work, forward or
        back. With neither, the first stage. Sent by its name, since the column sends the ticket."""
        return self._remember("column", self._read_column)

    def _read_column(self) -> Column:
        if self._session.is_closed:
            return self._board.column(COMPLETE_COLUMN)
        furthest_back = self.tree.furthest_back_child_stage
        if furthest_back is not None:
            return furthest_back
        return self.work.stage_worked_since_latest_move or self.marks.moved_into or self._board.stages[0]

    @property
    @data_field
    def is_closed(self) -> bool:
        """Whether its session is closed, so it shows in Complete."""
        return self._session.is_closed

    @property
    @data_field
    def is_active(self) -> bool:
        """Whether its session is the one the board's chat has open, which the agent works in."""
        return self._remember("is_active", lambda: self._board.sessions.opened.name_for(self._board.chat) == self.name)

    @property
    @data_field
    def is_open(self) -> bool:
        """Whether it is open for work: in its own worktree, or the active ticket. An open ticket closes through its Close
        dialog, whichever chat the board has chosen. Main is never open or closed this way."""
        return not self.is_main and not self.is_closed and (bool(self.worktree) or self.is_active)

    @property
    @data_field
    def parent_choices(self) -> list[str]:
        """The tickets a person can drop it on to make it their child: any on the board but its own parent, itself, and
        the tickets under it, which would make a loop."""
        return self.tree.parent_choices

    @property
    @data_field
    def drop_targets(self) -> list[str]:
        """The columns besides the stages a person can drop it on. The Backlog takes any ticket, which keeps its whole
        folder there. Complete takes any ticket not closed yet, from whatever stage it reached: an open one through its
        Close dialog, because closing it asks what to do with its work, and one not opened at once. A parent waits for
        its children, since it moves only with them."""
        if self.is_main:
            return []
        closes = not self.is_closed and not any(not child.is_closed for child in self.children)
        return [BACKLOG_COLUMN, *([COMPLETE_COLUMN] if closes else [])]

    @property
    @data_field
    def is_done(self) -> bool:
        """True in a stage when a person marked it done there, or when all its enabled work there is done."""
        return self._remember("is_done", self._read_is_done)

    def _read_is_done(self) -> bool:
        column = self.column
        if not isinstance(column, Stage):
            return False
        children_here = [child for child in self.children if child.column is column]
        if children_here:
            return all(child.is_done for child in children_here)
        marked = self.marks.latest_in(column)
        if marked is not None:
            return marked is StageMark.DONE
        return all(progress.is_done for progress in self.work.enabled if progress.stage is column)

    @property
    @data_field(key="next", reference=True)
    def next_fidelity(self) -> FidelityProgress | None:
        """The first fidelity not done in its current stage or a stage before it, earliest stage first, since later work
        builds on it; none when it is done in its stage or Complete. Sent by its ticket and fidelity, since progress sends
        it."""
        column = self.column
        stages = self._board.stages
        if self.is_done or column not in stages:
            return None
        reached = stages[: stages.index(column) + 1]
        return next((progress for progress in self.work.enabled if progress.stage in reached and not progress.is_done), None)

    @property
    @data_field
    def agent_context(self) -> str:
        """What the agent is told about this ticket in its system prompt while it is the active one: the ticket, its
        column, its next fidelity or that its stage waits for a person, and the steps every fidelity goes through."""
        upcoming = self.next_fidelity
        steps = self._board.stages[0].steps
        following = f"Its next guidance is {upcoming.fidelity.slug}. " if upcoming else "Its stage is done and waits for a person to move it. "
        return (
            f'CDD session board: you are working on ticket {self.name} ("{self.title}"), in {self.column.name}. '
            f"{following}Each fidelity goes through {', '.join(steps[:-1])}, then {steps[-1]}, and is done once its latest {steps[-1]} passes."
        )

    @property
    def last_activity(self) -> str:
        entries = self._session.log.entries
        return entries[-1].time if entries else ""

    @property
    @data_field
    def worktree(self) -> str:
        """The folder of the ticket's own worktree, where its chat works; empty while it has none."""
        return self.checkout.worktree

    @property
    @data_field
    def dropped_work(self) -> list[str]:
        """The files whose changes nobody committed that went with its worktree when it was last closed, since commit was
        not chosen, so the close's answer names what was lost; none when nothing was."""
        return list(self.board_fields.get(_DROPPED_WORK_FIELD) or [])

    @property
    def board_fields(self) -> OwnedFields:
        """The fields the board keeps for it in its session.json: its stage, its mark there, and its dropped work."""
        return self._session.record.extra(_TICKET_FIELDS)

    @property
    @data_field
    def new_chat_link(self) -> str:
        """The claude://code/new link that opens the ticket's chat in the Claude app on its worktree, with a prompt typed
        in for the person to send; empty while it has no worktree. The app starts no chat a person did not send, so the
        board and the chat bar open this link rather than ask an agent to start one."""
        if not self.worktree:
            return ""
        return Chats.load(self._board.call).new_chat(self.worktree, self.prompts.new_chat).link

    @property
    @data_field
    def prompts(self) -> TicketPrompts:
        """What the ticket asks its chat to do for it, worded here beside the tools they name: split it, write its
        handoff, set up its roots, close its session, and start as its new chat."""
        return TicketPrompts(self.name, self._session.session_file_from_project)

    @property
    @data_field
    def can_edit(self) -> bool:
        """Whether a person may edit its text and tags: any ticket's but main's, the default session, which is no one
        piece of work; edit_text and tag refuse main."""
        return not self.is_main

    @property
    @data_field
    def session_path(self) -> str:
        """The whole path of the folder the ticket's session works in: its workpath, else its repository's folder. The
        status line below the chat names it, and the chat bar opens the Graph app on it, so the graph a chat opens is its
        own session's."""
        return str(self._session.work_root)

    @property
    @data_field(key="working_chat", reference=True)
    def chat(self) -> Chat | None:
        """The connected chat the ticket works in, which every command the board sends for it goes to, sent by its id as
        working_chat: the chat a person assigned to it, else the one named after the ticket, else the one working in its
        worktree. None while no such chat is connected."""
        return self.checkout.chat

    @property
    @data_field
    def stage_work(self) -> list[StageWork]:
        """Its work in each stage taken together, in stage order: what a stage head's action bar shows and acts on."""
        return [self.work.in_stage(stage) for stage in self._board.stages]

    @property
    @data_field
    def next_place(self) -> StagePlace | None:
        """Where Move next puts the ticket while it stays on a stage: its stage's Done, else the next stage's In progress.
        None when the move closes it, leaves it where it is, or is refused, which only the move itself can show."""
        return self.moves.next_place

    @property
    @data_field
    def previous_place(self) -> StagePlace | None:
        """Where Move previous puts the ticket while it stays on a stage: its stage's In progress, else the previous
        stage's Done. None when the move reopens it, sends it to the Backlog, leaves it where it is, or is refused."""
        return self.moves.previous_place

    @mcp
    @agent_tool
    @noSessionLog
    def violations(self) -> Report:
        """Return the rules broken on every fidelity of the ticket's stage left with violations, across its practices, each rule naming its fidelity, in the shape of fidelity_progress.report. path is the folder the reports sit in. A saved graph holds its whole practice's hits, so a rule two fidelities share is listed once. has_saved_graph is false when a report has no saved graph, so its rules are missing."""
        return self.work.violations

    @mcp
    @agent_tool
    @noSessionLog
    def violations_of(self, path: str) -> Report:
        """Return the rules the latest reports of every fidelity of the ticket find broken in path, a file or a folder named from the project, each with only its violations in that file or in a file in that folder, in the shape of violations; no rule when none is broken there. The Files app's file menu shows it as Display violations."""
        return self.work.violations_of(path)

    def in_overview(self) -> OverviewTicket:
        """This ticket as the board's overview sends it: whole, but for its text, and with its children by name."""
        return OverviewTicket(self._session, self._board)

    def in_answer(self) -> OverviewTicket:
        """This ticket as a move, a close, an archive, or an activate answers with it: as the overview sends it, since a
        plan kept in the idea file runs to tens of thousands of characters and took the answer past MCP's size limit, so
        the agent that moved the ticket could not read what came of it. The board reads the board again after each of
        them, and `ticket.show` sends the text."""
        return self.in_overview()


class OverviewTicket(Ticket):
    """*OverviewTicket* is the active ticket as `board.overview` sends it to a reader such as the chat bar, whose MCP
    answer is cut off past its size limit: the ticket whole but for its text, with each child by its name alone. Sent whole, each child
    would carry its own progress, stage work, and children, so a ticket two levels of children deep would triple the
    answer; `board.show` keeps sending them whole for the board, where a stacked child shows in no column."""

    @property
    @data_field
    def text(self) -> str:
        """Empty: the reader draws no ticket text, and a plan kept in the idea file runs to tens of thousands of
        characters, which took the answer past its size limit. `board.show` and `ticket.show` send it."""
        return ""

    @property
    @data_field(reference=True)
    def children(self) -> list[Ticket]:
        """The tickets whose session names this one's as their parent, each by its name."""
        return self._board.reads.children_of(self)


class TicketMoves:
    """*TicketMoves* are the moves a person makes with one ticket: Move next and Move previous, where each puts a ticket
    that stays on a stage, and a drag straight into a stage or the Backlog. A parent moves only with its children, so
    each move refuses one; each move is a mark in the ticket's *StageMarks*."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket

    def move_next(self) -> Ticket:
        """From In progress to its stage's Done, from Done to the next column; out of Hardening, the last stage, it closes, but
        main stays in Hardening's Done."""
        ticket = self._ticket
        ticket.tree.refuse_moving_a_parent()
        column = ticket.column
        if not isinstance(column, Stage):
            return ticket
        place = self.next_place
        if place is None:
            return ticket if ticket.is_main else ticket.close([])
        return ticket.marks.mark(StageMark.DONE, column) if place.is_done else ticket.marks.enter(place.stage)

    @property
    def next_place(self) -> StagePlace | None:
        """Where Move next puts the ticket while it stays on a stage; none when the move closes it, leaves it where it
        is, or is refused."""
        ticket = self._ticket
        column = ticket.column
        if ticket.children or not isinstance(column, Stage):
            return None
        if not ticket.is_done:
            return StagePlace(column, True)
        following = column.next_stage
        return StagePlace(following, False) if following is not None else None

    def move_previous(self) -> Ticket | BacklogItem:
        """From Done to its stage's In progress, from In progress to the previous column's Done; out of Complete it
        reopens in Hardening, the last stage; out of Discovery it goes to the Backlog with its work, but main stays in Discovery."""
        ticket = self._ticket
        ticket.tree.refuse_moving_a_parent()
        column = ticket.column
        if not isinstance(column, Stage):
            reopened, final = self.reopened(), ticket.board.stages[-1]
            reopened.marks.enter(final)
            return reopened.marks.mark(StageMark.DONE, final)
        place = self.previous_place
        if place is None:
            return ticket if ticket.is_main else ticket.to_backlog()
        return ticket.marks.place(place.stage, StageMark.DONE) if place.is_done else ticket.marks.mark(StageMark.IN_PROGRESS, column)

    @property
    def previous_place(self) -> StagePlace | None:
        """Where Move previous puts the ticket while it stays on a stage; none when the move reopens it, sends it to the
        Backlog, leaves it where it is, or is refused."""
        ticket = self._ticket
        column = ticket.column
        if ticket.children or not isinstance(column, Stage):
            return None
        if ticket.is_done:
            return StagePlace(column, False)
        earlier = column.previous_stage
        return StagePlace(earlier, True) if earlier is not None else None

    def reopened(self) -> Ticket:
        """The ticket on a stage: itself while it is on one; out of Complete, reopened, its folder back among the open
        sessions and the ticket read there, on the stage it was closed from until a move places it."""
        ticket = self._ticket
        if not ticket.is_closed:
            return ticket
        return ticket.board.placement.ticket_of(ticket.session.folder.reopen())

    def move_to(self, stage: str, done: bool) -> Ticket | BacklogItem:
        """Straight into stage's In progress, or its Done when done; out of Complete it reopens first; into the Backlog
        it becomes a backlog item that keeps its whole folder."""
        ticket = self._ticket
        if stage == BACKLOG_COLUMN:
            return ticket.to_backlog()
        ticket.tree.refuse_moving_a_parent()
        target = ticket.board.stage(stage)
        return self.reopened().marks.place(target, StageMark.DONE if done else StageMark.IN_PROGRESS)

    def move_beside(self, other: Ticket) -> Ticket:
        """Into the column and list other is in, so the ticket can be placed next to it: itself where it is there
        already; closed, its work left as it is, beside a closed ticket; else in other's stage, In progress or Done as
        other is."""
        ticket = self._ticket
        if other.is_closed:
            return ticket if ticket.is_closed else ticket.close([])
        if not ticket.is_closed and ticket.column is other.column and ticket.is_done == other.is_done:
            return ticket
        ticket.tree.refuse_moving_a_parent()
        return self.reopened().marks.place(other.column, StageMark.DONE if other.is_done else StageMark.IN_PROGRESS)


class TicketWork:
    """*TicketWork* is a ticket's progress on each fidelity the board requires whose practice its session holds, in
    stage order: read from its session's log once per ticket read, and read again after the ticket writes a line."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket
        # Its progress as last read from its session's log; none until asked for, and none again once a line is written.
        self._read: list[FidelityProgress] | None = None
        # The enabled part of that reading, with the reading it was picked from.
        self._enabled: tuple[list[FidelityProgress], list[FidelityProgress]] | None = None
        # Its session's log entries as last read; none until asked for, and none again once a line is written.
        self._entries: list[LogLine] | None = None

    @property
    def entries(self) -> list[LogLine]:
        """Its session's log entries, read once with its progress, so its stage and its progress read the same lines."""
        if self._entries is None:
            self._entries = self._ticket.session.log.entries
        return self._entries

    @cached_property
    def _required(self) -> list[RequiredFidelity]:
        """Each fidelity a stage requires, as this ticket's session holds it, with its stage: one object per fidelity in
        a session, which finds its own files and reports there and is the one an action on it works with."""
        fidelities = [fidelity for practice in self._ticket.session.own_practices.values() for fidelity in practice.fidelities]
        return [RequiredFidelity(stage, fidelity) for stage in self._ticket.board.stages for fidelity in fidelities if stage.requires(fidelity)]

    @property
    def progress(self) -> list[FidelityProgress]:
        if self._read is None:
            self._read = [FidelityProgress.from_log(required, self._ticket) for required in self._required]
        return self._read

    @property
    def enabled(self) -> list[FidelityProgress]:
        """The progress of the fidelities whose practice the ticket's session works on, picked once for each reading
        of the progress: a board read asks it for every stage and every mark."""
        progress = self.progress
        if self._enabled is None or self._enabled[0] is not progress:
            self._enabled = (progress, [entry for entry in progress if entry.is_enabled])
        return self._enabled[1]

    @property
    def stage_worked_since_latest_move(self) -> Stage | None:
        """The stage of the fidelity the latest generate or validate line names, when that line came after the ticket's
        latest move; none when no such work followed it."""
        entries = self.entries
        moves = [index for index, entry in enumerate(entries) if entry.verb == MOVED_INTO]
        since = entries[moves[-1] + 1:] if moves else entries
        for entry in reversed(since):
            if entry.verb not in (_generate(), _validate()):
                continue
            stage = next((progress.stage for progress in self.enabled if entry.names(progress.fidelity)), None)
            if stage is not None:
                return stage
        return None

    @property
    def violations(self) -> Report:
        """The rules broken on every fidelity of the ticket's stage left with violations, taken together in one report."""
        column = self._ticket.column
        reports = [entry.report() for entry in self.progress if entry.has_violations and entry.stage is column]
        session = self._ticket.session
        return Report.from_reports(session.paths.from_project(session.reports_folder), reports)

    def violations_of(self, path: str) -> Report:
        """The rules the latest reports of every fidelity with violations find broken in path, a file or a folder named
        from the project, with only their violations there."""
        reports = [entry.report() for entry in self.progress if entry.has_violations]
        session = self._ticket.session
        return Report.from_reports(session.paths.from_project(session.reports_folder), reports).within(path)

    def progress_of(self, slug: str) -> FidelityProgress:
        """The progress of the fidelity slug names, such as stories-story-map. Only that fidelity's progress is read,
        because a tool that names one fidelity needs no other's reports."""
        found = next((required for required in self._required if required.fidelity.slug == slug), None)
        if found is None:
            raise FidelityNotFoundError(slug, f"ticket {self._ticket.name!r}")
        return FidelityProgress.from_log(found, self._ticket)

    def in_stage(self, stage: Stage) -> StageWork:
        """Its work in stage: the progress of every fidelity stage requires whose practice its session works on."""
        return StageWork(self._ticket, stage, [progress for progress in self.enabled if progress.stage is stage])

    def record(self, line: LogLine) -> None:
        """Write line to the ticket's session log; its progress is read from the log again next time it is asked for."""
        self._ticket.session.log.record(line)
        self._read = None
        self._entries = None
        self._ticket.forget_reads()


class StageMarks:
    """*StageMarks* are the moves and marks a person made on one ticket's stages: the stage it was last moved into, and
    in that stage whether it was last marked done or in progress. They are the board's own fields in the ticket's
    session.json (``stage``, ``stage_mark``, through ``record.extra("ticket")``), so the stage never depends on which
    log lines a branch has. Each move or mark is also a log line, the history agentic improvement reads; a ticket moved
    before the record existed is read from its log."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket

    @property
    def _fields(self) -> OwnedFields:
        return self._ticket.board_fields

    @property
    def moved_into(self) -> Stage | None:
        """The stage of the ticket's latest move; none before a person has moved it."""
        name = self._recorded_stage
        if name is None:
            moved = self._ticket.session.log.latest(MOVED_INTO)
            name = moved.stage if moved is not None else ""
        return next((stage for stage in self._ticket.board.stages if stage.name == name), None)

    def latest_in(self, stage: Stage) -> StageMark | None:
        """The latest mark a person made in stage since entering it; none when they have made none."""
        if self._recorded_stage is not None:
            mark = str(self._fields.get(_STAGE_MARK_FIELD) or "")
            return StageMark(mark) if self._recorded_stage == stage.name and mark else None
        latest = self._ticket.session.log.latest(MOVED_INTO, *(mark.value for mark in StageMark), stage=stage.name)
        return StageMark(latest.verb) if latest is not None and latest.verb != MOVED_INTO else None

    @property
    def _recorded_stage(self) -> str | None:
        """The stage session.json records; none for a ticket whose moves are only in its log."""
        recorded = self._fields.get(_STAGE_FIELD)
        return str(recorded) if recorded else None

    def enter(self, stage: Stage) -> Ticket:
        """Move the ticket into stage's In progress."""
        self._write(None, stage)
        return self._ticket

    def mark(self, mark: StageMark, stage: Stage) -> Ticket:
        """Mark the ticket done or in progress in stage, keeping the result in session.json, which is committed on main
        and pushed."""
        self._write(mark, stage)
        return self._ticket

    def place(self, stage: Stage, mark: StageMark) -> Ticket:
        """Put the ticket in stage, entering it first unless it is there, then mark it there: one commit on main, pushed,
        for both."""
        if self._ticket.column is not stage:
            self._write(None, stage)
        return self.mark(mark, stage)

    def _write(self, mark: StageMark | None, stage: Stage) -> None:
        """Keep the ticket in stage with mark, none when it was only moved there, and log the move or the mark."""
        self._fields.save(**{_STAGE_FIELD: stage.name, _STAGE_MARK_FIELD: mark.value if mark is not None else ""})
        self._ticket.work.record(LogLine(mark.value if mark is not None else MOVED_INTO, subject=stage.name))


class NoReportToAcceptInError(LookupError):
    """A person accepted, or took back the acceptance of, a violation of a fidelity that has no validation report. It
    names the fidelity and the violation asked for."""

    def __init__(self, fidelity: str, rule: str, location: str) -> None:
        self.fidelity = fidelity
        self.rule = rule
        self.location = location
        super().__init__(f"{fidelity} has no validation report, so it lists no violation of {rule} at {location}; validate it first")


class LoggedWork:
    """What a ticket's session log says was done on one fidelity: the actions done, whether its latest validate left
    violations, and how many lines name the fidelity. Generate and Validate each write one, so a change in that count
    means the fidelity's files may have changed since they were last looked for."""

    def __init__(self, done_actions: list[str], has_violations: bool, lines_logged: int = 0) -> None:
        self.done_actions = list(done_actions)
        self.has_violations = has_violations
        self.lines_logged = lines_logged

    def failed_again(self) -> LoggedWork:
        """This work with its latest validate failed, so validate is to do again."""
        return LoggedWork([action for action in self.done_actions if action == _generate()], True, self.lines_logged)

    def validated(self, steps: list[str]) -> LoggedWork:
        """This work with its latest validate passed, its done actions in the order of steps, its stage's."""
        return LoggedWork([action for action in steps if action in (*self.done_actions, _validate())], False, self.lines_logged)


class Work(ABC):
    """*Work* is a ticket's work on some fidelities of one stage: one fidelity's progress (*FidelityProgress*) or a
    stage's work taken together (*StageWork*). Each answers the command a chat runs for every action of its stage on its
    fidelities, which the ticket's session's guidance selection writes (``GuidanceSelection.command``): the one place a
    command and its ``format=`` are written."""

    _ticket: Ticket

    @property
    @abstractmethod
    def stage(self) -> Stage: ...

    @property
    @abstractmethod
    def fidelities(self) -> list[FidelityGuidance]:
        """The fidelities its commands name."""

    @property
    @data_field
    def commands(self) -> dict[str, str]:
        """The command a chat runs for each action its stage offers on its fidelities, such as
        ``/actions-generate ux-mockup session=.sessions/checkout-flow/session.json format=html``."""
        return self._ticket.session.guidance.commands_on(self.fidelities)

    def command(self, action: str) -> str:
        """The command that runs action on its fidelities in its ticket's session, with the formats chosen there for an
        action that takes them."""
        return self.commands[action]


@identity("ticket", "fidelity")
@language_adapter(language="typescript")
@agent_toolset
class FidelityProgress(Work):
    """*FidelityProgress* is how far one fidelity has got through its stage's actions on one ticket."""

    # Validate is done when its latest line names no graph-rule violations and the latest report's judgment fails no
    # rule, or when a person accepted every violation its latest report names; a fidelity whose latest validate passes
    # is done.

    def __init__(self, required: RequiredFidelity, logged: LoggedWork, ticket: Ticket) -> None:
        self._required = required
        self._logged = logged
        self._ticket = ticket

    @classmethod
    def from_log(cls, required: RequiredFidelity, ticket: Ticket) -> FidelityProgress:
        """Read the actions done on this fidelity from its ticket's session log entries, finding it by name, never by
        position; the latest report's judgment can still fail a validate the log shows passing."""
        entries = ticket.work.entries
        naming = [(index, entry.verb) for index, entry in enumerate(entries) if entry.names(required.fidelity)]
        validations = [index for index, verb in naming if verb == _validate()]
        latest_validation = validations[-1] if validations else None
        has_violations = latest_validation is not None and GRAPH_RULE_VIOLATION in entries[latest_validation].words
        validated = latest_validation is not None and not has_violations
        # Only the generate tool writes a generate line: an action started inside another, such as the generate a
        # Sketch prompt expands, logs nothing (GuidanceAction.log_running), so every generate line counts.
        done_verbs = {verb for _index, verb in naming if verb == _generate()}
        done_verbs |= {_validate()} if validated else set()
        logged = LoggedWork([action for action in required.stage.steps if action in done_verbs], has_violations, len(naming))
        read = cls(required, logged, ticket)
        judged = read._with_violations() if read._is_judged_failing else read
        return judged._with_accepted_left_out()

    @classmethod
    @tool_subject
    def load(cls, ticket: str, fidelity: str, *, project: Path | str) -> FidelityProgress:
        """The progress of fidelity, a slug such as stories-story-map, on the ticket named ticket on the board of
        project."""
        return Ticket.load(ticket, project=project).work.progress_of(fidelity)

    @property
    @data_field(reference=True)
    def ticket(self) -> Ticket:
        """The ticket this progress is on, sent by its name, which with its fidelity names the progress."""
        return self._ticket

    def holds(self, file: Path) -> bool:
        """Whether file is one of this fidelity's in its ticket's session, changed by the session or not; none while its
        practice works in no session."""
        output = self._required.fidelity.session_output
        return output is not None and output.written.holds(file)

    @property
    @data_field(reference=True)
    def fidelity(self) -> FidelityGuidance:
        """The fidelity this progress is on, as its ticket's session holds it; sent by its slug, such as
        stories-story-map, because its guidance text is read through its help, never with every ticket."""
        return self._required.fidelity

    @property
    @data_field(reference=True)
    def stage(self) -> Stage:
        """The stage that requires the fidelity, sent by its name, since the stage sends its tickets."""
        return self._required.stage

    @property
    @data_field(reference=True)
    def practice(self) -> PracticeGuidance:
        """Its practice, sent by its key, such as clean_engineering, by which the board's practices and its ticket's
        session name the practice."""
        return self._practice

    @property
    @data_field
    def is_enabled(self) -> bool:
        """Whether the ticket's session works on this fidelity's practice, as the fidelity, which works in that session,
        answers it."""
        return self._required.fidelity.session_output.is_enabled

    @property
    def _practice(self) -> PracticeGuidance:
        return self._required.fidelity.practice_guidance

    @property
    def _remaining_actions(self) -> list[str]:
        """Its stage's actions not yet done: a fidelity generated and validated without violations is done."""
        return [action for action in self._required.stage.steps if action not in self._logged.done_actions]

    @property
    @data_field
    def next_action(self) -> str:
        """What Run next does on this fidelity: the first of its stage's actions not done, which is validate again
        while it has violations, or nothing once it is done."""
        remaining = self._remaining_actions
        return remaining[0] if remaining else ""

    @property
    def fidelities(self) -> list[FidelityGuidance]:
        """Its one fidelity, which its commands name."""
        return [self._required.fidelity]

    @property
    @data_field
    def allowed_actions(self) -> list[str]:
        """Every action of its stage, in the stage's order; Validate and Render only once there is output to
        check or convert: an action on the fidelity is recorded, or a file it declares is already there, such as one a
        person wrote. A person can check the same output again as often as they like."""
        has_output = bool(self._logged.done_actions) or self._has_files
        return [action for action in self._required.stage.actions if has_output or action not in _needing_output()]

    @cached_property
    def _has_files(self) -> bool:
        """Read once per reading of the progress, since the board and its stage's work both ask. A file named by its
        whole path, such as one a person wrote, is looked for on every read; a pattern's search walks folders, so it runs
        again only after Generate or Validate logs a line on the fidelity or its session declares other paths for it."""
        output = self._required.fidelity.session_output
        if output is None:
            return False
        if output.written.has_named_output():
            return True
        key = json.dumps([self._required.fidelity.session_output.written.output_paths(), self._logged.lines_logged], sort_keys=True)
        return PROGRESS_CACHES.of(self._ticket.session).of(self._required.fidelity.slug).answer(HAS_OUTPUT, key, output.written.has_found_output)

    @property
    @data_field
    def has_violations(self) -> bool:
        """Whether its latest validate left violations, so it is validated again once they are fixed."""
        return self._logged.has_violations

    @property
    def is_done(self) -> bool:
        return not self._remaining_actions

    @property
    @data_field
    def state(self) -> str:
        """done, violations, in_progress, or not_started: what the board pane colours."""
        if self.is_done:
            return "done"
        if self._logged.has_violations:
            return "violations"
        return "in_progress" if self._logged.done_actions else "not_started"

    @property
    @data_field(key="actions")
    def action_states(self) -> ActionStates:
        """Each action as to_do, in_progress, or done. A validate that left violations is in progress until they are fixed."""
        states = {action: "done" if action in self._logged.done_actions else "to_do" for action in self._required.stage.steps}
        if self._logged.has_violations:
            states[_validate()] = "in_progress"
        return ActionStates(states)

    @property
    @data_field
    def report_file(self) -> str:
        """Its latest validation report, as a path from the project; empty when it has none."""
        latest = self.latest_report
        return self._ticket.session.paths.from_project(latest.file) if latest else ""

    @cached_property
    def latest_report(self) -> ReportFile | None:
        """Its latest validation report in its ticket's session that has its result, else its latest; none when it has
        none. Found once per reading of the progress."""
        return ReportFile.from_fidelity(self._required.fidelity)

    @property
    @data_field
    def violation_count(self) -> int:
        """How many violations its latest report names, graph hits and judged findings; none while it has no violations."""
        return self._violation_count

    @cached_property
    def _violation_count(self) -> int:
        """Counted once per reading of the progress, since the board and its stage's work both ask, and counted again
        only once Validate writes a report in the session, the latest report or its saved graph changes, or a person
        accepts a violation or takes an acceptance back."""
        return self._counted(VIOLATION_COUNT, lambda: self._latest_read.violation_count)

    @cached_property
    def _accepted_count(self) -> int:
        """How many violations its latest report leaves out because a person accepted them, kept as its count is."""
        return self._counted(ACCEPTED_COUNT, lambda: self._latest_read.accepted_count)

    def _counted(self, question: str, count: Callable[[], int]) -> int:
        """What count answers about its latest report, kept in its session's progress cache until the report can read
        otherwise; none while it has no violations."""
        latest = self.latest_report
        if not self._logged.has_violations or latest is None:
            return 0
        return PROGRESS_CACHES.of(self._ticket.session).of(self._required.fidelity.slug).answer(question, latest.version, count)

    @cached_property
    def _latest_read(self) -> Report:
        """Its latest report read once per reading of the progress, for each count taken from it."""
        return self.latest_report.report()

    @mcp
    @agent_tool
    @noSessionLog
    def accept_violation(self, rule: str, message: str, location: str, line: int = 0, node_id: str = "") -> Report:
        """Accept one violation of this fidelity's latest validation report as it is, and return the report without it. Name the violation as the report shows it: its rule, message, location, line (0 when it has none), and node_id (empty when it is on no node). It is kept in the project's .context/violations-accepted.json, by its rule, the id of its node, and its message, so no later validate, report, or count names it; a finding on no node is kept by its rule, its file, and the content of its line. It shows again when its message, its node's id, or that content changes. Refused when the report lists no such violation."""
        self._latest_report_or_refuse(rule, location).accept(self._shown_as(rule, message, Location(location, line or None), node_id))
        return self._report_read_again()

    @mcp
    @agent_tool
    @noSessionLog
    def reopen_violation(self, rule: str, message: str, location: str, line: int = 0, node_id: str = "") -> Report:
        """Take back the acceptance of one violation this fidelity's latest validation report lists under accepted, and return the report with it open again. Name the violation as the report shows it: its rule, message, location, line (0 when it has none), and node_id (empty when it is on no node). Refused when the report lists no such violation."""
        self._latest_report_or_refuse(rule, location).reopen(self._shown_as(rule, message, Location(location, line or None), node_id))
        return self._report_read_again()

    def _latest_report_or_refuse(self, rule: str, location: str) -> ReportFile:
        """Its latest report; *NoReportToAcceptInError*, naming the violation asked for, while it has none."""
        latest = self.latest_report
        if latest is None:
            raise NoReportToAcceptInError(self._required.fidelity.slug, rule, location)
        return latest

    def _shown_as(self, rule: str, message: str, location: Location, node_id: str) -> Violation:
        """The violation a page names by what its report showed of it."""
        return Violation(FoundBy(rule, "", FoundOn(node_id)), message, location)

    def _report_read_again(self) -> Report:
        """Its latest report read after an acceptance changed, with what its ticket worked out before forgotten."""
        self._ticket.forget_reads()
        return FidelityProgress(self._required, self._logged, self._ticket).report()

    @mcp
    @agent_tool
    @noSessionLog
    def report(self) -> Report:
        """Return this fidelity's latest validation report: its path and text, and the rules broken in it, each with its description and each violation with its line and the source around it. The rules are those broken on the nodes of the graph saved beside the report, then each rule the validating agent's judgment fails that the graph did not hit. has_saved_graph is false when the report has no saved graph, so its graph's rules are missing."""
        latest = self.latest_report
        return latest.report() if latest is not None else Report()

    @mcp
    @agent_tool
    @noSessionLog
    def help(self) -> Help:
        """Return the overview, guidance, and rules of this fidelity, with its stage and its page on the forge."""
        return Help(self._practice, self._ticket.board.catalogued_practices.of(type(self._practice)), self._required)

    @mcp
    @agent_tool
    @noSessionLog
    def files(self) -> dict[str, list[FileEntry]]:
        """List the files a person reviews for this fidelity by format in its ticket's session, each with its path from the project, whether it exists, and the published link of a design canvas, formats in the order files are shown (``Format.file_order``: markdown, code, diagrams). They are the files it declares, or those of the fidelities its practice document says it reviews files of (UX front-end code: its IA and mockup). A pattern lists the files the ticket worked on, not every match in the repository."""
        files = self._required.fidelity.session_output.written.files_to_review()
        return dict(sorted(files.items(), key=lambda formats: Format(formats[0]).file_order))

    def _with_violations(self) -> FidelityProgress:
        """This progress with its latest validate failed, so validate is to do again."""
        return FidelityProgress(self._required, self._logged.failed_again(), self._ticket)

    def _with_accepted_left_out(self) -> FidelityProgress:
        """This progress with its latest validate passed when a person accepted every violation its latest report
        names, so an accepted violation holds no fidelity back; itself while any is still open."""
        if not self._logged.has_violations or self._violation_count or not self._accepted_count:
            return self
        return FidelityProgress(self._required, self._logged.validated(self._required.stage.steps), self._ticket)

    @property
    def _is_judged_failing(self) -> bool:
        """A validate the log shows passing still failed when the judgment the validating agent added to its report fails a rule."""
        if _validate() not in self._logged.done_actions:
            return False
        latest = self.latest_report
        return latest is not None and latest.is_judged_failing


class ActionStates:
    """Where each of a stage's actions stands on one fidelity: to_do, in_progress, or done."""

    def __init__(self, states: dict[str, str]) -> None:
        self._states = dict(states)

    @classmethod
    def taken_together(cls, every: list[ActionStates]) -> ActionStates:
        """Where each action stands across several fidelities: done only once it is done on all of them, in progress
        once it is under way on any, else to do."""
        if not every:
            return cls({action: "to_do" for action in (_generate(), _validate())})
        taken = every[0]
        for states in every[1:]:
            taken = taken._with(states)
        return taken

    def _with(self, other: ActionStates) -> ActionStates:
        """These states taken together with other's: an action is done only when done on both, else in progress once
        under way on either, else to do."""
        return ActionStates({action: self._state_with(action, other._states[action]) for action in self._states})

    def _state_with(self, action: str, other: str) -> str:
        mine = self._states[action]
        if mine == "done" and other == "done":
            return "done"
        return "in_progress" if mine != "to_do" or other != "to_do" else "to_do"

    @property
    @data_field
    def generate(self) -> str:
        return self._states[_generate()]

    @property
    @data_field
    def validate(self) -> str:
        return self._states[_validate()]


class StageWork(Work):
    """*StageWork* is a ticket's work in one stage taken together: the progress of each fidelity the stage requires
    whose practice the ticket's session works on. A stage head's action bar shows how far it has got and acts on all of
    it at once."""

    def __init__(self, ticket: Ticket, stage: Stage, progress: list[FidelityProgress]) -> None:
        self._ticket = ticket
        self._stage = stage
        self._progress = list(progress)

    @property
    @data_field(reference=True)
    def stage(self) -> Stage:
        return self._stage

    @property
    @data_field(reference=True)
    def progress(self) -> list[FidelityProgress]:
        """The progress of each fidelity it holds, each a fidelity of the stage whose practice the session works on, in
        the order the stage requires them; sent by reference, since the ticket sends each in full."""
        return list(self._progress)

    @property
    @data_field(key="actions")
    def action_states(self) -> ActionStates:
        """Each action done only once it is done on every fidelity, in progress once it is under way on any."""
        return ActionStates.taken_together([progress.action_states for progress in self._progress])

    @property
    @data_field
    def has_violations(self) -> bool:
        """Whether any of its fidelities' latest validate left violations."""
        return any(progress.has_violations for progress in self._progress)

    @property
    @data_field
    def violation_count(self) -> int:
        """How many violations its fidelities' latest reports name together."""
        return sum(progress.violation_count for progress in self._progress)

    @property
    def fidelities(self) -> list[FidelityGuidance]:
        """Each of its fidelities, which one command names together."""
        return [progress.fidelity for progress in self._progress]

    @property
    @data_field
    def allowed_actions(self) -> list[str]:
        """The actions every one of its fidelities allows, so one command can act on them all."""
        if not self._progress:
            return []
        first, *others = self._progress
        return [action for action in first.allowed_actions if all(action in other.allowed_actions for other in others)]
