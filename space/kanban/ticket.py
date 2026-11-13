"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import quote, urlencode

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.chat.chat import Chat
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.graph.pattern_overlays import PatternOverlays
from harness.guidance.stages import GENERATE, RENDER, VALIDATE
from harness.installation.data_class import data_field, identity, language_adapter
from harness.markdown.format import Format
from harness.mcp.mcp_server import long_call, mcp
from space.kanban.board import (
    BACKLOG_COLUMN,
    COMPLETE_COLUMN,
    Board,
    Card,
    Column,
    FidelityNotFoundError,
    Help,
    Stage,
)
from space.kanban.format_choice import FormatChoice
from space.kanban.overlay_choice import OverlayChoice
from space.kanban.report import Report, ReportFile
from space.kanban.ticket_checkout import LeaveChoices, TicketCheckout
from space.repo.repo import Branch
from space.session import Session
from space.session.session import MAIN_SESSION_NAME
from space.session.progress_cache import HAS_OUTPUT, VIOLATION_COUNT
from space.session.session_log import LogEntry
from space.session.file_manager import FileEntry

if TYPE_CHECKING:
    from space.kanban.backlog_item import BacklogItem

GRAPH_RULE_VIOLATION = "graph-rule"
# The Claude app opens a new chat from this link, on the folder it names, with its prompt typed in for the person to send.
NEW_CHAT_LINK = "claude://code/new"
MOVED_INTO = "move"
MARKED_DONE = "done"
MARKED_IN_PROGRESS = "in-progress"
# The session.json fields that record a ticket's stage and its mark there.
_STAGE_FIELD = "stage"
_STAGE_MARK_FIELD = "stage_mark"
# The actions that check or convert a fidelity's output, so they wait until there is some.
ONCE_THERE_IS_OUTPUT = (VALIDATE, RENDER)


class MainStaysOpenError(ValueError):
    """Raised when a tool would close, archive, or shelve main, the default session, which stays on the board."""

    def __init__(self, action: str) -> None:
        super().__init__(f"main is the default session and stays open; it cannot {action}")


class ParentMovesWithChildrenError(ValueError):
    """Raised when a person moves a ticket that has children: a parent takes the stage of its child furthest back."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"{ticket} has child tickets; a parent moves only with its children")


class NotAChildError(ValueError):
    """Raised when a ticket with no parent is pulled out of one."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"{ticket} has no parent to be pulled out of")


class ParentLoopError(ValueError):
    """Raised when a ticket would become its own parent, or a child of one of its own children."""

    def __init__(self, ticket: str, parent: str) -> None:
        super().__init__(f"{parent} cannot be the parent of {ticket}: it is {ticket} or one of its children")


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


@identity("name")
@language_adapter(language="typescript")
@agent_toolset
class Ticket(Card):
    """Show one work session as a unit of delivery and move it through the stages."""

    # It works with its session, which holds its folders, practices, and files, and the board it sits on, and holds
    # three parts made once: its work (its progress on each fidelity the board requires), its checkout (its branch and
    # worktree), and its stage marks (the moves and marks a person made). Callers reach those through it.
    # Never moves to another column by itself: a person moves it, and the move is written to its session log.
    # The board is read after every cdd call, so these tools stay out of the session log; a move writes its own line.
    # Its tools and data fields stay on it, so their published names do not change (.context/cdr/0004).

    def __init__(self, session: Session, board: Board) -> None:
        super().__init__(board)
        self._session = session
        self.work = TicketWork(self)
        self.checkout = TicketCheckout(self)
        self.marks = StageMarks(self)

    @classmethod
    @tool_subject
    def load(cls, ticket: str, *, project: Path | str) -> Ticket:
        """The ticket named ticket on the board of project, read from its own session alone."""
        return Board.load(project).ticket_called(ticket)

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def create(cls, title: str, scope: str = "feature", parent: str = "", path: str = "", *, project: Path | str) -> Ticket:
        """Open a new ticket titled title in Discovery, its record committed on main and pushed. scope is feature, story, or slice; parent names the ticket it was split from; path is the folder in the repository its session works on. Then run ticket.activate to open the ticket's own worktree, and do its work in a chat started there (start_session with cwd set to the ticket's worktree), not in this chat."""
        board = Board.load(project)
        opened = board.open_ticket(title, scope, parent, path)
        return opened

    @property
    @data_field
    def name(self) -> str:
        """Its session's name. A ticket is an agent toolset, whose own name is the toolset's, so without this a
        ticket's name would read "ticket"."""
        return self._session.name

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
        """Return the branch ticket's work is on, which leaving ticket commits and pushes: its own branch while it is checked out, in the repository or in its own worktree, else the default branch while the repository has it checked out, as for a session with no branch of its own. Any other branch checked out is not ticket's, so its own branch comes back not checked out and leaving commits nothing."""
        return self.checkout.work_branch

    @property
    @data_field
    def is_main(self) -> bool:
        """Whether this is main, the default session: every chat in the repository's own folder works on it, and it
        never closes, archives, or goes to the Backlog."""
        return self.name == MAIN_SESSION_NAME

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
        named = self._session.parent
        return self._board.ticket(named) if named else None

    @property
    def ancestors(self) -> list[Ticket]:
        """Its parent, its parent's parent, and so on."""
        parent = self.parent
        return [parent, *parent.ancestors] if parent is not None else []

    @property
    @data_field
    def children(self) -> list[Ticket]:
        """The tickets whose session names this one's as their parent: stacked inside its card, or, pulled out, cards of
        their own it keeps a row for. Sent whole, since a stacked child shows in no column."""
        return self._board.children_of(self)

    @property
    @data_field
    def is_pulled_out(self) -> bool:
        """Whether this child moves on the board as a card of its own, still keeping its parent."""
        return self._session.is_pulled_out

    @property
    @data_field
    def is_stacked(self) -> bool:
        """Whether it shows inside its parent's card rather than as a card of its own: an open child, not pulled out, of
        an open parent."""
        if self.is_pulled_out or self.is_closed:
            return False
        parent = self.parent
        return parent is not None and not parent.is_closed

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
        if self._session.is_closed:
            return self._board.column(COMPLETE_COLUMN)
        furthest_back = self._furthest_back_child_stage
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
        """Whether its session is the one saved as open, which the agent works in."""
        return self._board.sessions.open_name == self.name

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
        if self.is_main:
            return []
        parent = self.parent
        return [ticket.name for ticket in self._board.tickets if ticket is not parent and self._can_be_child_of(ticket)]

    def _can_be_child_of(self, parent: Ticket) -> bool:
        return self.name not in [parent.name, *(ancestor.name for ancestor in parent.ancestors)]

    @property
    @data_field
    def drop_targets(self) -> list[str]:
        """The columns besides the stages a person can drop it on. The Backlog takes any ticket, which keeps its whole
        folder there. Complete takes one from Implementation's Done, or an open ticket, through its Close dialog, because
        closing it asks what to do with its work."""
        if self.is_main:
            return []
        final = self._board.stages[-1]
        closes = self.is_open or (not self.is_closed and self.column is final and self.is_done)
        return [BACKLOG_COLUMN, *([COMPLETE_COLUMN] if closes else [])]

    @property
    @data_field
    def is_done(self) -> bool:
        """True in a stage when a person marked it done there, or when all its enabled work there is done."""
        column = self.column
        if not isinstance(column, Stage):
            return False
        children_here = [child for child in self.children if child.column is column]
        if children_here:
            return all(child.is_done for child in children_here)
        marked = self.marks.latest_in(column)
        if marked is not None:
            return marked == MARKED_DONE
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
    def new_chat_link(self) -> str:
        """The claude://code/new link that opens the ticket's chat in the Claude app on its worktree, with a prompt typed
        in for the person to send; empty while it has no worktree. The app starts no chat a person did not send, so the
        board and the chat bar open this link rather than ask an agent to start one."""
        if not self.worktree:
            return ""
        prompt = (
            f'Title this session "{self.name}". You are the chat of the session board\'s ticket {self.name}; work on that '
            f"ticket. First call sessions.switch with name {self.name}, so every tool works on its session, then read the "
            "session's latest handoff."
        )
        return f"{NEW_CHAT_LINK}?{urlencode({'folder': self.worktree, 'q': prompt}, quote_via=quote)}"

    @property
    @data_field
    def branch_name(self) -> str:
        """The branch the ticket's chat works on, which the chat bar's status row names: its own while it has a
        worktree, else the branch the repository has checked out."""
        if self.worktree:
            return self.checkout.branch.name
        repo = self._board.repo
        return repo.current_branch.name if repo.is_clone else ""

    @property
    @data_field
    def root_folder(self) -> str:
        """The folder the ticket's session works in, as a path from its repository's folder, which the status line below
        the chat names after the repository; empty when the session works in the whole repository. A folder outside the
        repository keeps its whole path."""
        work_root = self._session.work_root
        repository = Path(self._session.repo_path).resolve()
        if not work_root.is_relative_to(repository):
            return str(work_root)
        relative = work_root.relative_to(repository)
        return "" if relative == Path(".") else str(relative)

    @property
    @data_field(key="working_chat", reference=True)
    def chat(self) -> Chat | None:
        """The connected chat the ticket works in, which every command the board sends for it goes to, sent by its id as
        working_chat: the chat a person assigned to it, else the one named after the ticket, else the one working in its
        worktree. None while no such chat is connected."""
        return self.checkout.chat

    @mcp
    @agent_tool
    def assign_chat(self, chat: str = "") -> Ticket:
        """Make chat, the id of a connected chat, ticket's chat, kept in its session.json, so every command the board sends for ticket goes there and no chat named after it is looked for; an empty chat gives ticket back to the chat named after it."""
        self.checkout.assign_chat(chat)
        return self

    @property
    @data_field
    def stage_work(self) -> list[StageWork]:
        """Its work in each stage taken together, in stage order: what a stage head's action bar shows and acts on."""
        return [self.work.in_stage(stage) for stage in self._board.stages]

    @mcp
    @agent_tool
    @noSessionLog
    def format_choices(self, fidelities: list[str]) -> list[FormatChoice]:
        """Return the format chips of an action bar on ticket over fidelities, slugs such as stories-story-map: each group of formats they offer, the format each fidelity uses from it, how many offer it and have a file in it already, and whether the bar opens with it picked."""
        read = [(progress.fidelity, progress.files()) for progress in (self.work.progress_of(slug) for slug in fidelities)]
        return FormatChoice.offered_by(read)

    @mcp
    @agent_tool
    @noSessionLog
    def overlay_choices(self) -> list[OverlayChoice]:
        """Return the pattern overlays a person can choose for ticket's session: every registered pattern in name order, each with its icon, its first and last letter, and whether the session overlays it on its graph."""
        chosen = self._session.overlays
        return [OverlayChoice(pattern, pattern in chosen) for pattern in PatternOverlays().names]

    @mcp
    @agent_tool
    def choose_overlays(self, overlays: list[str]) -> list[OverlayChoice]:
        """Overlay the patterns overlays names, such as lern_domain_driven, on ticket's session's graph in place of those chosen before, refusing a name that is no pattern with NotAPatternError; return its overlay choices."""
        self._session.choose_overlays(overlays)
        return self.overlay_choices()

    @mcp
    @agent_tool
    @noSessionLog
    def close_choices(self) -> LeaveChoices:
        """Return what closing ticket can do with its work, none chosen at first, so closing does only what the person ticks: a handoff always; a commit and a push of the branch its work is on while a checkout has it, which branch names; and, for its own branch, which own_branch names, a merge into main, a delete of the branch, and a delete of its worktree while it has one."""
        return self.checkout.close_choices

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def activate(self) -> Ticket:
        """Open ticket in its own worktree, where its own chat works on it: the worktree it has, else a new one on its own branch, made when missing, after the session folders not yet committed are committed on main and pushed. Sessions open only from main: the chat that asks keeps its own session, the repository's own folder stays on main, and nothing is left or moved."""
        self.checkout.open()
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def move_next(self) -> Ticket:
        """Move ticket on: from In progress to its stage's Done, from Done to the next column, whatever its work. Out of Implementation it closes, but main, the default session, stays in Implementation's Done. A ticket with children moves only with them, so it is refused."""
        self._refuse_moving_a_parent()
        column = self.column
        if not isinstance(column, Stage):
            return self
        place = self.next_place
        if place is None:
            return self if self.is_main else self.close()
        return self.marks.mark(MARKED_DONE, column) if place.is_done else self.marks.enter(place.stage)

    @property
    @data_field
    def next_place(self) -> StagePlace | None:
        """Where Move next puts the ticket while it stays on a stage: its stage's Done, else the next stage's In progress.
        None when the move closes it, leaves it where it is, or is refused, which only the move itself can show."""
        column = self.column
        if self.children or not isinstance(column, Stage):
            return None
        if not self.is_done:
            return StagePlace(column, True)
        following = column.next_stage
        return StagePlace(following, False) if following is not None else None

    @mcp
    @agent_tool
    @noSessionLog
    def move_previous(self) -> Ticket | BacklogItem:
        """Move ticket back: from Done to its stage's In progress, from In progress to the previous column's Done. Out of Complete it reopens in Implementation; out of Discovery it goes to the Backlog with its work, but main stays in Discovery. A ticket with children moves only with them, so it is refused."""
        self._refuse_moving_a_parent()
        column = self.column
        if not isinstance(column, Stage):
            reopened, final = self._board.ticket_of(self._session.reopen()), self._board.stages[-1]
            reopened.marks.enter(final)
            return reopened.marks.mark(MARKED_DONE, final)
        place = self.previous_place
        if place is None:
            return self if self.is_main else self._return_to_backlog()
        return self.marks.place(place.stage, MARKED_DONE) if place.is_done else self.marks.mark(MARKED_IN_PROGRESS, column)

    @property
    @data_field
    def previous_place(self) -> StagePlace | None:
        """Where Move previous puts the ticket while it stays on a stage: its stage's In progress, else the previous
        stage's Done. None when the move reopens it, sends it to the Backlog, leaves it where it is, or is refused."""
        column = self.column
        if self.children or not isinstance(column, Stage):
            return None
        if self.is_done:
            return StagePlace(column, False)
        earlier = column.previous_stage
        return StagePlace(earlier, True) if earlier is not None else None

    @mcp
    @agent_tool
    @noSessionLog
    def move_to(self, stage: str, done: bool = False) -> Ticket | BacklogItem:
        """Move ticket straight into stage's In progress, or its Done when done is true, whatever its work; dragging a card does this. Out of Complete it reopens first. Into the Backlog, from any column, it becomes a backlog item that keeps its whole folder. A ticket with children moves only with them, so it is refused."""
        self._refuse_moving_a_parent()
        if stage == BACKLOG_COLUMN:
            return self._return_to_backlog()
        target = self._board.stage(stage)
        moved = self if isinstance(self.column, Stage) else self._board.ticket_of(self._session.reopen())
        return moved.marks.place(target, MARKED_DONE if done else MARKED_IN_PROGRESS)

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def close(self, leaving: list[str] | None = None) -> Ticket:
        """Close ticket: leaving names what to do with its work first (handoff, commit, push, merge, delete_branch, delete_worktree); then its session ends, its folder moves to _complete/, that move is committed on main and pushed, and it shows in Complete. The repository's own folder stays on main."""
        if self.is_main:
            raise MainStaysOpenError("close")
        chosen = leaving or []
        self.checkout.write_handoff(chosen)
        # A worktree something still holds open fails to delete; deleting it first stops the close with nothing changed.
        self.checkout.free_worktree(chosen)
        self.checkout.keep_landing_release(chosen)
        self._session.close()
        closed = self._board.ticket_of(self._session.move_to_closed())
        # The work is saved after the folder moves, so the move is committed with it.
        self.checkout.save_work(chosen)
        self.checkout.return_to_default_branch()
        # The ticket's record is kept on main, so its move among the closed sessions is committed and pushed there.
        self._board.sessions.saves.now(f"sessions: close {self.name}")
        return closed

    @mcp
    @agent_tool
    @noSessionLog
    def archive(self) -> Ticket:
        """Archive ticket: its session ends, its folder moves to _archive/, that move is committed on main and pushed, and it leaves the board. Main never archives."""
        if self.is_main:
            raise MainStaysOpenError("archive")
        self._session.close()
        archived = self._board.ticket_of(self._session.move_to_archive())
        self._board.sessions.saves.now(f"sessions: archive {self.name}")
        return archived

    @mcp
    @agent_tool
    @noSessionLog
    def violations(self) -> Report:
        """Return the rules broken on every fidelity of the ticket's stage left with violations, across its practices, each rule naming its fidelity, in the shape of fidelity_progress.report. path is the folder the reports sit in. A saved graph holds its whole practice's hits, so a rule two fidelities share is listed once. has_saved_graph is false when a report has no saved graph, so its rules are missing."""
        column = self.column
        reports = [entry.report() for entry in self.progress if entry.has_violations and entry.stage is column]
        return Report.from_reports(self._session.from_project(self._session.reports_folder), reports)

    @mcp
    @agent_tool
    @noSessionLog
    def edit_text(self, text: str) -> Ticket:
        """Write text as what ticket's work is about, in the idea file its session folder keeps, <name>.md, under its heading; the file is made when ticket has none. Committed on main and pushed."""
        self._session.keep_text(text)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def tag(self, word: str) -> Ticket:
        """Tag ticket's session with word, kept in its session.json beside its other tags. Committed on main and pushed."""
        self._session.add_tag(word)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def delete(self) -> None:
        """Delete ticket: its session ends and its folder, log, and files are removed, that removal committed on main and pushed, and it leaves the board. Main never deletes."""
        if self.is_main:
            raise MainStaysOpenError("be deleted")
        self._session.close()
        self._session.remove()
        self._board.reread()

    @mcp
    @agent_tool
    @noSessionLog
    def add_child(self, title: str) -> Ticket:
        """Open a child ticket of ticket titled title, a story In progress in Discovery, working where ticket works. Committed on main and pushed."""
        child = self._board.ticket_of(self._session.open_child(title, scope="story"))
        return child

    @mcp
    @agent_tool
    @noSessionLog
    def pull_out(self) -> Ticket:
        """Pull ticket out of its parent: it moves on the board as a card of its own, still keeping its parent, which keeps a row for it. Committed on main and pushed."""
        if self.parent is None:
            raise NotAChildError(self.name)
        self._session.mark_pulled_out()
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def reassign_parent(self, parent: Ticket | None = None) -> Ticket:
        """Make parent ticket's parent, as dragging ticket onto it does, or none, so ticket is a ticket of its own (Alt-dragging it out of its parent); either way it is no longer pulled out. Committed on main and pushed."""
        if parent is not None and not self._can_be_child_of(parent):
            raise ParentLoopError(self.name, parent.name)
        self._session.set_parent(parent.session if parent is not None else None)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def move_before(self, other: Ticket) -> Ticket:
        """Move ticket just above other in their column, as dragging it there does; the column keeps that order, in .sessions/_board.json. Committed on main and pushed."""
        super().move_before(other)
        return self

    @property
    def _furthest_back_child_stage(self) -> Stage | None:
        """The stage of its child furthest back on the board; none while no child of it is on a stage."""
        stages = self._board.stages
        staged = [column for column in (child.column for child in self.children) if isinstance(column, Stage)]
        return min(staged, key=stages.index) if staged else None

    def _refuse_moving_a_parent(self) -> None:
        if self.children:
            raise ParentMovesWithChildrenError(self.name)

    def _return_to_backlog(self) -> BacklogItem:
        """Into the Backlog from any column: its session closes and its whole folder becomes a backlog item, so starting
        the item brings the ticket back with its work. The move is committed on main and pushed."""
        if self.is_main:
            raise MainStaysOpenError("go to the Backlog")
        self._session.close()
        kept_in_backlog = self._board.ticket_of(self._session.move_to_backlog())
        item = self._board.backlog_item_of(kept_in_backlog)
        item.write_if_missing(kept_in_backlog.title)
        return item

    def in_overview(self) -> OverviewTicket:
        """This ticket as the board's overview sends it: whole, but with its children by name."""
        return OverviewTicket(self._session, self._board)


class OverviewTicket(Ticket):
    """*OverviewTicket* is the active ticket as `board.overview` sends it to a reader such as the chat bar, whose MCP
    answer is cut off past its size limit: the ticket whole, with each child by its name alone. Sent whole, each child
    would carry its own progress, stage work, and children, so a ticket two levels of children deep would triple the
    answer; `board.show` keeps sending them whole for the board, where a stacked child shows in no column."""

    @property
    @data_field(reference=True)
    def children(self) -> list[Ticket]:
        """The tickets whose session names this one's as their parent, each by its name."""
        return self._board.children_of(self)


class TicketWork:
    """*TicketWork* is a ticket's progress on each fidelity the board requires whose practice its session holds, in
    stage order: read from its session's log once per ticket read, and read again after the ticket writes a line."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket
        # Its progress as last read from its session's log; none until asked for, and none again once a line is written.
        self._read: list[FidelityProgress] | None = None
        # The enabled part of that reading, with the reading it was picked from.
        self._enabled: tuple[list[FidelityProgress], list[FidelityProgress]] | None = None

    @cached_property
    def _required(self) -> list[tuple[Stage, FidelityGuidance]]:
        """Each fidelity a stage requires, as this ticket's session holds it, with its stage: one object per fidelity in
        a session, which finds its own files and reports there and is the one an action on it works with."""
        fidelities = [fidelity for practice in self._ticket.session.own_practices.values() for fidelity in practice.fidelities]
        return [(stage, fidelity) for stage in self._ticket.board.stages for fidelity in fidelities if stage.requires(fidelity)]

    @property
    def progress(self) -> list[FidelityProgress]:
        if self._read is None:
            entries = self._ticket.session.log.entries
            self._read = [FidelityProgress.from_log(fidelity, stage, entries, self._ticket) for stage, fidelity in self._required]
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
        entries = self._ticket.session.log.entries
        moves = [index for index, entry in enumerate(entries) if entry.verb == MOVED_INTO]
        since = entries[moves[-1] + 1:] if moves else entries
        for entry in reversed(since):
            if entry.verb not in (GENERATE, VALIDATE):
                continue
            stage = next((progress.stage for progress in self.enabled if entry.names(progress.fidelity)), None)
            if stage is not None:
                return stage
        return None

    def progress_of(self, slug: str) -> FidelityProgress:
        """The progress of the fidelity slug names, such as stories-story-map. Only that fidelity's progress is read,
        because a tool that names one fidelity needs no other's reports."""
        found = next(((stage, fidelity) for stage, fidelity in self._required if fidelity.slug == slug), None)
        if found is None:
            raise FidelityNotFoundError(slug, f"ticket {self._ticket.name!r}")
        stage, fidelity = found
        return FidelityProgress.from_log(fidelity, stage, self._ticket.session.log.entries, self._ticket)

    def in_stage(self, stage: Stage) -> StageWork:
        """Its work in stage: the progress of every fidelity stage requires whose practice its session works on."""
        return StageWork(self._ticket, stage, [progress for progress in self.enabled if progress.stage is stage])

    def command(self, action: str, fidelities: list[FidelityGuidance]) -> str:
        """The command that runs action on fidelities in the ticket's session, one command for them all so the chat
        works on them in one turn. It names the session, because the chat that runs it can have another session open,
        and no format, so the action works in the format each fidelity keeps in that session."""
        named = " ".join(fidelity.slug for fidelity in fidelities)
        return f"/actions-{action} {named} session={self._ticket.session.session_file_from_project}"

    def record(self, line: str) -> None:
        """Write line to the ticket's session log; its progress is read from the log again next time it is asked for."""
        self._ticket.session.log.record(line)
        self._read = None


class StageMarks:
    """*StageMarks* are the moves and marks a person made on one ticket's stages: the stage it was last moved into, and
    in that stage whether it was last marked done or in progress. They are the ticket's record, kept in its session.json
    (``stage``, ``stage_mark``), so the stage never depends on which log lines a branch has. Each move or mark is also a
    log line, the history agentic improvement reads; a ticket moved before the record existed is read from its log."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket

    @property
    def moved_into(self) -> Stage | None:
        """The stage of the ticket's latest move; none before a person has moved it."""
        name = self._recorded_stage
        if name is None:
            moved = self._ticket.session.log.latest(MOVED_INTO)
            name = moved.stage if moved is not None else ""
        return next((stage for stage in self._ticket.board.stages if stage.name == name), None)

    def latest_in(self, stage: Stage) -> str | None:
        """The latest mark a person made in stage since entering it; none when they have made none."""
        if self._recorded_stage is not None:
            mark = str(self._ticket.session.fields.get(_STAGE_MARK_FIELD, "") or "")
            return mark if self._recorded_stage == stage.name and mark else None
        latest = self._ticket.session.log.latest(MOVED_INTO, MARKED_DONE, MARKED_IN_PROGRESS, stage=stage.name)
        return latest.verb if latest is not None and latest.verb != MOVED_INTO else None

    @property
    def _recorded_stage(self) -> str | None:
        """The stage session.json records; none for a ticket whose moves are only in its log."""
        recorded = self._ticket.session.fields.get(_STAGE_FIELD)
        return str(recorded) if recorded else None

    def enter(self, stage: Stage) -> Ticket:
        """Move the ticket into stage's In progress."""
        return self.mark(MOVED_INTO, stage)

    def mark(self, mark: str, stage: Stage) -> Ticket:
        """Mark the ticket done or in progress in stage, or move it into stage, keeping the result in session.json, which
        is committed on main and pushed."""
        self._write(mark, stage)
        return self._ticket

    def place(self, stage: Stage, mark: str) -> Ticket:
        """Put the ticket in stage, entering it first unless it is there, then mark it there: one commit on main, pushed,
        for both."""
        if self._ticket.column is not stage:
            self._write(MOVED_INTO, stage)
        return self.mark(mark, stage)

    def _write(self, mark: str, stage: Stage) -> None:
        self._ticket.session.save_fields(**{_STAGE_FIELD: stage.name, _STAGE_MARK_FIELD: "" if mark == MOVED_INTO else mark})
        self._ticket.work.record(f"{mark} {stage.name}")



@identity("ticket", "fidelity")
@language_adapter(language="typescript")
@agent_toolset
class FidelityProgress:
    """*FidelityProgress* is how far one fidelity has got through its stage's actions on one ticket."""

    # Validate is done when its latest line names no graph-rule violations and the latest report's judgment fails no
    # rule; a fidelity whose latest validate passes is done.

    def __init__(self, fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool, ticket: Ticket, lines_logged: int = 0) -> None:
        self._fidelity = fidelity
        self._stage = stage
        self._done_actions = list(done_actions)
        self._has_violations = has_violations
        self._ticket = ticket
        # How many log lines name this fidelity: Generate and Validate each write one, so a change in it means the
        # fidelity's files may have changed since they were last looked for.
        self._lines_logged = lines_logged

    @classmethod
    def from_log(cls, fidelity: FidelityGuidance, stage: Stage, entries: list[LogEntry], ticket: Ticket) -> FidelityProgress:
        """Read the actions done on this fidelity from its session's log entries, finding it by name, never by position;
        the latest report's judgment can still fail a validate the log shows passing."""
        naming = [(index, entry.verb) for index, entry in enumerate(entries) if entry.names(fidelity)]
        validations = [index for index, verb in naming if verb == VALIDATE]
        latest_validation = validations[-1] if validations else None
        has_violations = latest_validation is not None and GRAPH_RULE_VIOLATION in entries[latest_validation].words
        validated = latest_validation is not None and not has_violations
        # Only the generate tool writes a generate line: an action started inside another, such as the generate a
        # Sketch prompt expands, logs nothing (GuidanceAction.log_running), so every generate line counts.
        done_verbs = {verb for _index, verb in naming if verb == GENERATE}
        done_verbs |= {VALIDATE} if validated else set()
        read = cls(fidelity, stage, [action for action in stage.steps if action in done_verbs], has_violations, ticket, len(naming))
        return read.with_violations() if read._is_judged_failing else read

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

    @property
    @data_field(reference=True)
    def fidelity(self) -> FidelityGuidance:
        """The fidelity this progress is on, as its ticket's session holds it; sent by its slug, such as
        stories-story-map, because its guidance text is read through its help, never with every ticket."""
        return self._fidelity

    @property
    @data_field(reference=True)
    def stage(self) -> Stage:
        """The stage that requires the fidelity, sent by its name, since the stage sends its tickets."""
        return self._stage

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
        return self._fidelity.session_output.is_enabled

    @property
    def _practice(self) -> PracticeGuidance:
        return self._fidelity.practice_guidance

    @property
    def done_actions(self) -> list[str]:
        return list(self._done_actions)

    @property
    def remaining_actions(self) -> list[str]:
        """Its stage's actions not yet done: a fidelity generated and validated without violations is done."""
        return [action for action in self._stage.steps if action not in self._done_actions]

    @property
    @data_field
    def next_action(self) -> str:
        """What Run next does on this fidelity: the first of its stage's actions not done, which is validate again
        while it has violations, or nothing once it is done."""
        remaining = self.remaining_actions
        return remaining[0] if remaining else ""

    @property
    @data_field
    def commands(self) -> dict[str, str]:
        """The command a chat runs for each action its stage offers on this fidelity, such as
        ``/actions-generate ux-mockup session=.sessions/checkout-flow/session.json``."""
        return {action: self.command(action) for action in self._stage.actions}

    def command(self, action: str) -> str:
        """The command that runs action on this fidelity in its ticket's session. It names the session, because the
        chat that runs it can have another session open, and no format, so the action works in the format the fidelity
        keeps in that session."""
        return self._ticket.work.command(action, [self._fidelity])

    @property
    @data_field
    def allowed_actions(self) -> list[str]:
        """Every action of its stage, in the stage's order; Validate and Render only once there is output to
        check or convert: an action on the fidelity is recorded, or a file it declares is already there, such as one a
        person wrote. A person can check the same output again as often as they like."""
        has_output = bool(self._done_actions) or self._has_files
        return [action for action in self._stage.actions if has_output or action not in ONCE_THERE_IS_OUTPUT]

    @cached_property
    def _has_files(self) -> bool:
        """Read once per reading of the progress, since the board and its stage's work both ask. A file named by its
        whole path, such as one a person wrote, is looked for on every read; a pattern's search walks folders, so it runs
        again only after Generate or Validate logs a line on the fidelity or its session declares other paths for it."""
        output = self._fidelity.session_output
        if output is None:
            return False
        if output.has_named_output():
            return True
        key = json.dumps([self._fidelity.output_paths(), self._lines_logged], sort_keys=True)
        return self._ticket.session.progress_cache.answer(self._fidelity.slug, HAS_OUTPUT, key, output.has_found_output)

    @property
    @data_field
    def has_violations(self) -> bool:
        """Whether its latest validate left violations, so it is validated again once they are fixed."""
        return self._has_violations

    @property
    def is_done(self) -> bool:
        return not self.remaining_actions

    @property
    @data_field
    def state(self) -> str:
        """done, violations, in_progress, or not_started: what the board pane colours."""
        if self.is_done:
            return "done"
        if self._has_violations:
            return "violations"
        return "in_progress" if self._done_actions else "not_started"

    @property
    @data_field(key="actions")
    def action_states(self) -> ActionStates:
        """Each action as to_do, in_progress, or done. A validate that left violations is in progress until they are fixed."""
        states = {action: "done" if action in self._done_actions else "to_do" for action in self._stage.steps}
        if self._has_violations:
            states[VALIDATE] = "in_progress"
        return ActionStates(states)

    @property
    @data_field
    def report_file(self) -> str:
        """Its latest validation report, as a path from the project; empty when it has none."""
        latest = self.latest_report
        return self._ticket.session.from_project(latest.file) if latest else ""

    @cached_property
    def latest_report(self) -> ReportFile | None:
        """Its latest validation report in its ticket's session that has its result, else its latest; none when it has
        none. Found once per reading of the progress."""
        return ReportFile.from_fidelity(self._fidelity)

    @property
    @data_field
    def violation_count(self) -> int:
        """How many violations its latest report names, graph hits and judged findings; none while it has no violations."""
        return self._violation_count

    @cached_property
    def _violation_count(self) -> int:
        """Counted once per reading of the progress, since the board and its stage's work both ask, and counted again
        only once Validate writes a report in the session or the latest report or its saved graph changes."""
        latest = self.latest_report
        if not self._has_violations or latest is None:
            return 0
        return self._ticket.session.progress_cache.answer(self._fidelity.slug, VIOLATION_COUNT, latest.version, lambda: latest.report().violation_count)

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
        return Help(self._practice, self._fidelity, self._stage, self._ticket.board.catalogued_practices.of(type(self._practice)))

    @mcp
    @agent_tool
    @noSessionLog
    def files(self) -> dict[str, list[FileEntry]]:
        """List the files this fidelity declares by format in its ticket's session, each with its path from the project and whether it exists, formats in the order files are shown (``Format.file_order``: markdown, code, diagrams). A pattern lists the files the ticket worked on, not every match in the repository."""
        files = self._fidelity.files()
        return dict(sorted(files.items(), key=lambda formats: Format(formats[0]).file_order))

    def with_violations(self) -> FidelityProgress:
        """This progress with its latest validate failed, so validate is to do again."""
        kept = [action for action in self._done_actions if action == GENERATE]
        return FidelityProgress(self._fidelity, self._stage, kept, True, self._ticket, self._lines_logged)

    @property
    def _is_judged_failing(self) -> bool:
        """A validate the log shows passing still failed when the judgment the validating agent added to its report fails a rule."""
        if VALIDATE not in self._done_actions:
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
            return cls({action: "to_do" for action in (GENERATE, VALIDATE)})
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
        return self._states[GENERATE]

    @property
    @data_field
    def validate(self) -> str:
        return self._states[VALIDATE]


class StageWork:
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
    def progress(self) -> list[FidelityProgress]:
        """The progress of each fidelity it holds."""
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
    @data_field
    def commands(self) -> dict[str, str]:
        """The command a chat runs for each action its stage offers, naming every one of its fidelities."""
        fidelities = [progress.fidelity for progress in self._progress]
        return {action: self._ticket.work.command(action, fidelities) for action in self._stage.actions}

    @property
    @data_field
    def allowed_actions(self) -> list[str]:
        """The actions every one of its fidelities allows, so one command can act on them all."""
        if not self._progress:
            return []
        first, *others = self._progress
        return [action for action in first.allowed_actions if all(action in other.allowed_actions for other in others)]
