"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.chat.chat import Chat
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.stages import GENERATE, RENDER, REVIEW, VALIDATE
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
from space.kanban.report import Report, ReportFile
from space.kanban.ticket_checkout import LEAVE_DELETE_BRANCH, LeaveChoices, OpenChoices, TicketCheckout
from space.repo.repo import Branch
from space.session import Session
from space.session.session_log import LogEntry
from space.session.file_manager import FileEntry

if TYPE_CHECKING:
    from space.kanban.backlog_item import BacklogItem

GRAPH_RULE_VIOLATION = "graph-rule"
MOVED_INTO = "move"
MARKED_DONE = "done"
MARKED_IN_PROGRESS = "in-progress"
# The actions that check or convert a fidelity's output, so they wait until there is some.
ONCE_THERE_IS_OUTPUT = (VALIDATE, REVIEW, RENDER)


class TicketNotFoundError(LookupError):
    """Raised when a tool names a ticket the board does not show."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"no ticket named {ticket!r} on the board")


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
        found = Board.load(project).ticket(ticket)
        if found is None:
            raise TicketNotFoundError(ticket)
        return found

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def create(cls, title: str, scope: str = "feature", parent: str = "", path: str = "", *, project: Path | str) -> Ticket:
        """Open a new ticket titled title in Discovery. scope is feature, story, or slice; parent names the ticket it was split from; path is the folder in the repository its session works on."""
        return Board.load(project).open_ticket(title, scope, parent, path)

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
    def title(self) -> str:
        return self._session.title or self._session.name

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
        """Complete once closed; otherwise the stage of its latest move, or the earliest stage it has work in. Sent by
        its name, since the column sends the ticket."""
        if self._session.is_closed:
            return self._board.column(COMPLETE_COLUMN)
        worked = [progress.stage for progress in self.work.enabled if progress.done_actions]
        return self.marks.moved_into or (worked[0] if worked else self._board.stages[0])

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
    def drop_targets(self) -> list[str]:
        """The columns besides the stages a person can drop it on. The Backlog takes any ticket, which keeps its whole
        folder there. Complete takes one from Implementation's Done, or the active ticket through its Close dialog,
        because closing it asks what to do with its work."""
        final = self._board.stages[-1]
        closes = not self.is_closed and (self.is_active or (self.column is final and self.is_done))
        return [BACKLOG_COLUMN, *([COMPLETE_COLUMN] if closes else [])]

    @property
    @data_field
    def is_done(self) -> bool:
        """True in a stage when a person marked it done there, or when all its enabled work there is done."""
        column = self.column
        if not isinstance(column, Stage):
            return False
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
            f"{following}Each fidelity goes through {', '.join(steps[:-1])}, then {steps[-1]}, which a person records on the board."
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
    @data_field(key="working_chat", reference=True)
    def chat(self) -> Chat | None:
        """The connected chat working on the ticket, which every command the board sends for it goes to, sent by its id as
        working_chat: the one working in its worktree or a folder inside it, else one whose mod names no folder and that
        is titled by the ticket's name, as the board titles the chat it opens for it. None while no chat works on it."""
        return self.checkout.chat

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
    def close_choices(self) -> LeaveChoices:
        """Return what closing ticket can do with its work, each chosen at first: a handoff always, and a commit and a push of the branch its work is on while that branch is checked out, which branch names. Closing never merges."""
        return self.checkout.close_choices

    @mcp
    @agent_tool
    @noSessionLog
    def leave_choices(self) -> LeaveChoices:
        """Return what leaving ticket for another can do with its work now, in the order leave does it: a handoff always; a commit and a push of the branch its work is on while that branch is checked out, which branch names; and a merge of that branch while it is the ticket's own, not the default branch. Each is chosen at first but the merge, which waits for the person."""
        return self.checkout.leave_choices

    @mcp
    @agent_tool
    @noSessionLog
    def open_choices(self) -> OpenChoices:
        """Return what opening ticket can create for it now, each chosen at first: its own branch while the repository has none, and its own worktree while it has none."""
        return self.checkout.open_choices

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def activate(self, leaving: list[str] | None = None, opening: list[str] | None = None) -> Ticket:
        """Make ticket the current session. leaving names what to do with the active ticket's work first: handoff, commit, push, merge, delete_branch, delete_worktree; deleting its branch closes it, so it moves to Complete. opening names how to open ticket: branch switches this checkout to its branch, worktree opens its own worktree."""
        active = self._board.active
        if active is not None and active.name != self.name:
            active._leave_for_another(leaving or [])
        self.checkout.open(opening or [])
        self._board.sessions.switch(self.name)
        return self

    def _leave_for_another(self, leaving: list[str]) -> None:
        """A session whose branch is deleted has nowhere left for its work, so it closes; any other is only left."""
        if LEAVE_DELETE_BRANCH in leaving:
            self.close(leaving)
            return
        self.checkout.leave(leaving)

    @long_call
    @mcp
    @agent_tool
    @noSessionLog
    def open_worktree(self) -> Ticket:
        """Open ticket's own worktree beside the repository, creating its branch when missing: the folder its chat works in, named as its worktree. The open session is left as it is."""
        self.checkout.open_worktree()
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def move_next(self) -> Ticket:
        """Move ticket on: from In progress to its stage's Done, from Done to the next column, whatever its work. Out of Implementation it closes."""
        column = self.column
        if not isinstance(column, Stage):
            return self
        if not self.is_done:
            return self.marks.mark(MARKED_DONE, column)
        following = column.next_stage
        return self.marks.enter(following) if following else self.close()

    @mcp
    @agent_tool
    @noSessionLog
    def move_previous(self) -> Ticket | BacklogItem:
        """Move ticket back: from Done to its stage's In progress, from In progress to the previous column's Done. Out of Complete it reopens in Implementation; out of Discovery it goes to the Backlog with its work."""
        column = self.column
        if not isinstance(column, Stage):
            reopened, final = self._board.ticket_of(self._session.reopen()), self._board.stages[-1]
            reopened.marks.enter(final)
            return reopened.marks.mark(MARKED_DONE, final)
        if self.is_done:
            return self.marks.mark(MARKED_IN_PROGRESS, column)
        earlier = column.previous_stage
        return self.marks.place(earlier, MARKED_DONE) if earlier else self._return_to_backlog()

    @mcp
    @agent_tool
    @noSessionLog
    def move_to(self, stage: str, done: bool = False) -> Ticket | BacklogItem:
        """Move ticket straight into stage's In progress, or its Done when done is true, whatever its work; dragging a card does this. Out of Complete it reopens first. Into the Backlog, from any column, it becomes a backlog item that keeps its whole folder."""
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
        """Close ticket: its session ends, its folder moves to _complete/, and it shows in Complete. leaving names what to do with its work first: handoff, commit, push, merge."""
        chosen = leaving or []
        self.checkout.write_handoff(chosen)
        self._session.close()
        closed = self._board.ticket_of(self._session.move_to_closed())
        # The work is saved after the folder moves, so the move is committed with it.
        self.checkout.save_work(chosen)
        self.checkout.return_to_default_branch(chosen)
        return closed

    @mcp
    @agent_tool
    @noSessionLog
    def archive(self) -> Ticket:
        """Archive ticket: its session ends, its folder moves to _archive/, and it leaves the board."""
        self._session.close()
        return self._board.ticket_of(self._session.move_to_archive())

    @mcp
    @agent_tool
    @noSessionLog
    def violations(self) -> Report:
        """Return the rules broken on every fidelity of the ticket's stage left with violations, across its practices, each rule naming its fidelity, in the shape of fidelity_progress.report. path is the folder the reports sit in. A saved graph holds its whole practice's hits, so a rule two fidelities share is listed once. has_saved_graph is false when a report has no saved graph, so its rules are missing."""
        column = self.column
        reports = [entry.report() for entry in self.progress if entry.has_violations and entry.stage is column]
        return Report.from_reports(self._session.from_project(self._session.reports_folder), reports)

    def _return_to_backlog(self) -> BacklogItem:
        """Into the Backlog from any column: its session closes and its whole folder becomes a backlog item, so starting
        the item brings the ticket back with its work."""
        self._session.close()
        kept_in_backlog = self._board.ticket_of(self._session.move_to_backlog())
        item = self._board.backlog_item_of(kept_in_backlog)
        item.write_if_missing(kept_in_backlog.title)
        return item


class TicketWork:
    """*TicketWork* is a ticket's progress on each fidelity the board requires whose practice its session holds, in
    stage order: read from its session's log once per ticket read, and read again after the ticket writes a line."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket
        # Its progress as last read from its session's log; none until asked for, and none again once a line is written.
        self._read: list[FidelityProgress] | None = None

    @cached_property
    def _required(self) -> list[tuple[Stage, FidelityGuidance]]:
        """Each fidelity a stage requires, as this ticket's session holds it, with its stage: one object per fidelity in
        a session, which finds its own files and reports there and is the one an action on it works with."""
        fidelities = [fidelity for practice in self._ticket.session.practices.values() for fidelity in practice.fidelities]
        return [(stage, fidelity) for stage in self._ticket.board.stages for fidelity in fidelities if stage.requires(fidelity)]

    @property
    def progress(self) -> list[FidelityProgress]:
        if self._read is None:
            entries = self._ticket.session.log.entries
            self._read = [FidelityProgress.from_log(fidelity, stage, entries, self._ticket) for stage, fidelity in self._required]
        return self._read

    @property
    def enabled(self) -> list[FidelityProgress]:
        """The progress of the fidelities whose practice the ticket's session works on."""
        return [entry for entry in self.progress if entry.is_enabled]

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
    """*StageMarks* are the moves and marks a person made on one ticket's stages, as its session's log answers them: the
    stage it was last moved into, and in a stage whether it was last marked done or in progress since entering it. A
    move or mark is a line written through the ticket's work, whose progress is read again after it."""

    def __init__(self, ticket: Ticket) -> None:
        self._ticket = ticket

    @property
    def moved_into(self) -> Stage | None:
        """The stage of the ticket's latest move; none before a person has moved it."""
        moved = self._ticket.session.log.latest(MOVED_INTO)
        return next((stage for stage in self._ticket.board.stages if moved is not None and stage.name == moved.stage), None)

    def latest_in(self, stage: Stage) -> str | None:
        """The latest mark a person made in stage since entering it; none when they have made none."""
        latest = self._ticket.session.log.latest(MOVED_INTO, MARKED_DONE, MARKED_IN_PROGRESS, stage=stage.name)
        return latest.verb if latest is not None and latest.verb != MOVED_INTO else None

    def enter(self, stage: Stage) -> Ticket:
        """Move the ticket into stage's In progress."""
        return self.mark(MOVED_INTO, stage)

    def mark(self, mark: str, stage: Stage) -> Ticket:
        """Mark the ticket done or in progress in stage."""
        self._ticket.work.record(f"{mark} {stage.name}")
        return self._ticket

    def place(self, stage: Stage, mark: str) -> Ticket:
        """Put the ticket in stage, entering it first unless it is there, then mark it there."""
        if self._ticket.column is not stage:
            self.enter(stage)
        return self.mark(mark, stage)


@identity("ticket", "fidelity")
@language_adapter(language="typescript")
@agent_toolset
class FidelityProgress:
    """*FidelityProgress* is how far one fidelity has got through its stage's actions on one ticket."""

    # Validate is done when its latest line names no graph-rule violations and the latest report's judgment fails no
    # rule. Review is done once a person reviews after the latest validate, passed or not.

    def __init__(self, fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool, ticket: Ticket) -> None:
        self._fidelity = fidelity
        self._stage = stage
        self._done_actions = list(done_actions)
        self._has_violations = has_violations
        self._ticket = ticket

    @classmethod
    def from_log(cls, fidelity: FidelityGuidance, stage: Stage, entries: list[LogEntry], ticket: Ticket) -> FidelityProgress:
        """Read the actions done on this fidelity from its session's log entries, finding it by name, never by position;
        the latest report's judgment can still fail a validate the log shows passing."""
        naming = [(index, entry.verb) for index, entry in enumerate(entries) if entry.names(fidelity)]
        validations = [index for index, verb in naming if verb == VALIDATE]
        latest_validation = validations[-1] if validations else None
        has_violations = latest_validation is not None and GRAPH_RULE_VIOLATION in entries[latest_validation].words
        validated = latest_validation is not None and not has_violations
        reviewed = any(verb == REVIEW and (latest_validation is None or index > latest_validation) for index, verb in naming)
        # Only the generate tool writes a generate line: an action started inside another, such as the generate a
        # Sketch prompt expands, logs nothing (GuidanceAction.log_running), so every generate line counts.
        done_verbs = {verb for _index, verb in naming if verb == GENERATE}
        done_verbs |= {VALIDATE} if validated else set()
        done_verbs |= {REVIEW} if reviewed else set()
        read = cls(fidelity, stage, [action for action in stage.steps if action in done_verbs], has_violations, ticket)
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
        return [action for action in self._stage.steps if action not in self._done_actions]

    @property
    @data_field
    def next_action(self) -> str:
        """What Run next does on this fidelity: review while it has violations, since a person reads them and tells the
        agent to fix them, else the first of its stage's actions not done, or nothing once it is done."""
        if self._has_violations:
            return REVIEW
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
        """Every action of its stage, in the stage's order; Validate, Review, and Render only once there is output to
        check or convert: an action on the fidelity is recorded, or a file it declares is already there, such as one a
        person wrote. A person can check the same output again as often as they like."""
        has_output = bool(self._done_actions) or self._has_files
        return [action for action in self._stage.actions if has_output or action not in ONCE_THERE_IS_OUTPUT]

    @cached_property
    def _has_files(self) -> bool:
        """Read once per reading of the progress: the board and its stage's work both ask."""
        return self._fidelity.has_declared_output()

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
        """Counted once per reading of the progress: the board and its stage's work both ask."""
        return self.report().violation_count if self._has_violations else 0

    @mcp
    @agent_tool
    @noSessionLog
    def finish_review(self) -> FidelityProgress:
        """Record that a person has reviewed and approved this fidelity: a review line in its ticket's session log. A review counts until the fidelity is validated again, and a fidelity whose actions are all done is done in its stage."""
        self._ticket.work.record(f"{REVIEW} {self._practice.key} {self._fidelity.name}")
        return next(progress for progress in self._ticket.progress if progress.fidelity is self._fidelity)

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
        """This progress with its latest validate failed, so validate is to do again; a person's review stands."""
        kept = [action for action in self._done_actions if action in (GENERATE, REVIEW)]
        return FidelityProgress(self._fidelity, self._stage, kept, True, self._ticket)

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
        return cls({action: cls._together([states._states[action] for states in every]) for action in (GENERATE, VALIDATE, REVIEW)})

    @staticmethod
    def _together(states: list[str]) -> str:
        if states and all(state == "done" for state in states):
            return "done"
        return "in_progress" if any(state != "to_do" for state in states) else "to_do"

    @property
    @data_field
    def generate(self) -> str:
        return self._states[GENERATE]

    @property
    @data_field
    def validate(self) -> str:
        return self._states[VALIDATE]

    @property
    @data_field
    def review(self) -> str:
        return self._states[REVIEW]


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
