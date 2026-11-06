"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import data_field, language_adapter
from harness.kanban.board import (
    BACKLOG_COLUMN,
    COMPLETE_COLUMN,
    GENERATE,
    REVIEW,
    VALIDATE,
    Board,
    Card,
    FidelityNotFoundError,
    Stage,
)
from harness.kanban.report import Report, ReportFile
from harness.mcp.mcp_server import mcp
from space.repo.repo import Repo
from space.session import Session, name_of
from space.session.session import LogEntry
from tools.file_manager.file_manager import FileEntry

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.board import Column

GRAPH_RULE_VIOLATION = "graph-rule"
MOVED_INTO = "move"
MARKED_DONE = "done"
MARKED_IN_PROGRESS = "in-progress"
SATISFY = "satisfy"
ALWAYS_ALLOWED = (GENERATE,)
ONCE_THERE_IS_OUTPUT = (VALIDATE, REVIEW)


class TicketNotFoundError(LookupError):
    """Raised when a tool names a ticket the board does not show."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"no ticket named {ticket!r} on the board")


class NotAStageError(ValueError):
    """Raised when a ticket is moved into a column that is not a stage, such as the Backlog or Complete."""

    def __init__(self, stage: str) -> None:
        super().__init__(f"{stage!r} is not a stage a ticket can be moved into")


@language_adapter(language="typescript", identity="name")
@agent_toolset
class Ticket(Card):
    """Show one work session as a unit of delivery and move it through the stages."""

    # It works with three objects: its session, which holds its folders, practices, and files; its progress, one per
    # fidelity the board requires; and the board it sits on. Callers reach those through it rather than through copies
    # of their fields.
    # Never moves to another column by itself: a person moves it, and the move is written to its session log.
    # The board is read after every cdd call, so these tools stay out of the session log; a move writes its own line.

    def __init__(self, session: Session, board: Board) -> None:
        super().__init__(board)
        self._session = session

    @classmethod
    @tool_subject
    def load(cls, ticket: str) -> Ticket:
        found = Board.current().ticket(ticket)
        if found is None:
            raise TicketNotFoundError(ticket)
        return found

    @classmethod
    @mcp
    @agent_tool
    @noSessionLog
    def create(cls, title: str, scope: str = "feature", parent: str = "", path: str = "") -> Ticket:
        """Open a new ticket titled title in Discovery. scope is feature, story, or slice; parent names the ticket it was split from; path is the folder in the repository its session works on."""
        board = Board.current()
        name = name_of(title)
        root = board.repo.root
        workpath = (root / path).resolve() if path else root
        Session.new(name, workpath, root, is_current=False, title=title, scope=scope, parent=parent)
        return board.ticket(name)

    @property
    @data_field
    def name(self) -> str:
        """Its session's name. A ticket is an agent toolset, whose own name is the toolset's, so without this a
        ticket's name would read "ticket"."""
        return self._session.name

    @property
    def title(self) -> str:
        return self._session.title or self._session.name

    @property
    @data_field
    def session(self) -> Session:
        """The work session this ticket shows: its folders, its practices and their files, and its log."""
        return self._session

    @property
    def progress(self) -> list[FidelityProgress]:
        """One per fidelity the board requires, in stage order; read from the session log each time, with the latest
        report's judgment able to fail a validate the log shows passing."""
        entries = self._session.log_entries
        return [FidelityProgress.from_log(fidelity, stage, entries, self) for stage in self._stages for fidelity in stage.work_required]

    @property
    @data_field(key="progress")
    def progress_by_fidelity(self) -> dict[str, FidelityProgress]:
        """Its progress by fidelity slug, such as stories-story_map, the way the board looks a fidelity up."""
        return {entry.fidelity_slug: entry for entry in self.progress}

    def progress_of(self, slug: str) -> FidelityProgress:
        """The progress of the fidelity slug names, such as stories-story_map."""
        found = next((entry for entry in self.progress if entry.fidelity_slug == slug), None)
        if found is None:
            raise FidelityNotFoundError(slug, f"ticket {self.name!r}")
        return found

    @property
    def column(self) -> Column:
        """Complete once closed; otherwise the stage of its latest move, or the earliest stage it has work in."""
        if self._session.is_closed:
            return self._board.column(COMPLETE_COLUMN)
        moved = self._moved_into()
        if moved is not None:
            return moved
        worked = [progress.stage for progress in self._enabled_progress if progress.done_actions]
        return worked[0] if worked else self._stages[0]

    @property
    @data_field(key="column")
    def column_name(self) -> str:
        return self.column.name

    @property
    @data_field
    def is_done(self) -> bool:
        """True in a stage when a person marked it done there, or when all its enabled work there is done."""
        column = self.column
        if not isinstance(column, Stage):
            return False
        marked = self._latest_mark(column)
        if marked is not None:
            return marked == MARKED_DONE
        return all(progress.is_done for progress in self._enabled_progress if progress.stage is column)

    @property
    def next_fidelity(self) -> FidelityProgress | None:
        """The first fidelity not done in its current stage or a stage before it, earliest stage first, since later work
        builds on it; none when it is done in its stage or Complete."""
        column = self.column
        if self.is_done or column not in self._stages:
            return None
        reached = self._stages[: self._stages.index(column) + 1]
        return next((progress for progress in self._enabled_progress if progress.stage in reached and not progress.is_done), None)

    @property
    @data_field(key="next")
    def next_slug(self) -> str | None:
        """The slug of its next fidelity, whose progress says what Run next does."""
        upcoming = self.next_fidelity
        return upcoming.fidelity_slug if upcoming else None

    @property
    def last_activity(self) -> str:
        entries = self._session.log_entries
        return entries[-1].time if entries else ""

    @property
    @data_field
    def worktree(self) -> str:
        """The folder of the ticket's own worktree, where its chat works; empty while it has none."""
        found = self._board.worktree_of(self.name)
        return str(found) if found else ""

    @mcp
    @agent_tool
    @noSessionLog
    def move_next(self) -> Ticket:
        """Move ticket on: from In progress to its stage's Done, from Done to the next column, whatever its work. Out of Implementation it closes."""
        column = self.column
        if not isinstance(column, Stage):
            return self
        if not self.is_done:
            return self._mark(MARKED_DONE, column)
        following = column.next_stage
        return self._enter(following) if following else self.close()

    @mcp
    @agent_tool
    @noSessionLog
    def move_previous(self) -> Ticket | BacklogItem:
        """Move ticket back: from Done to its stage's In progress, from In progress to the previous column's Done. Out of Complete it reopens in Implementation; out of Discovery it goes to the Backlog with its work."""
        column = self.column
        if not isinstance(column, Stage):
            return self._reopen()
        if self.is_done:
            return self._mark(MARKED_IN_PROGRESS, column)
        earlier = column.previous_stage
        if earlier is None:
            return self._return_to_backlog()
        return self._enter(earlier)._mark(MARKED_DONE, earlier)

    @mcp
    @agent_tool
    @noSessionLog
    def move_to(self, stage: str, done: bool = False) -> Ticket | BacklogItem:
        """Move ticket straight into stage's In progress, or its Done when done is true, whatever its work; dragging a card does this. Out of Complete it reopens first. Into the Backlog, from any column, it becomes a backlog item that keeps its whole folder."""
        if stage == BACKLOG_COLUMN:
            return self._return_to_backlog()
        target = next((column for column in self._stages if column.name == stage), None)
        if target is None:
            raise NotAStageError(stage)
        moved = self if isinstance(self.column, Stage) else Ticket(self._session.reopen(), self._board)
        entered = moved if moved.column is target else moved._enter(target)
        return entered._mark(MARKED_DONE if done else MARKED_IN_PROGRESS, target)

    @mcp
    @agent_tool
    @noSessionLog
    def close(self, leaving: list[str] | None = None) -> Ticket:
        """Close ticket: its session ends, its folder moves to _complete/, and it shows in Complete. leaving names what to do with its work first: commit, push, merge."""
        self._board.leave(self, leaving or [])
        self._session.close()
        return Ticket(self._session.move_to_closed(), self._board)

    @mcp
    @agent_tool
    @noSessionLog
    def archive(self) -> Ticket:
        """Archive ticket: its session ends, its folder moves to _archive/, and it leaves the board."""
        self._session.close()
        return Ticket(self._session.move_to_archive(), self._board)

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
    def generate_commands(self, fidelities: list[str], formats: list[str]) -> list[str]:
        """Return the commands that generate fidelities in formats. A format the same practice's earlier fidelity has no file in is rendered from that fidelity first."""
        renders = [self._render_command(self.progress_of(slug), formats) for slug in fidelities]
        named = " ".join(slug.replace("_", "-") for slug in fidelities)
        commands = [*filter(None, renders), f"/actions-generate {named} format={','.join(formats)}"]
        return [f"{command} session={self._session.session_file_from_project}" for command in commands]

    def _reopen(self) -> Ticket:
        """Back out of Complete into Implementation's Done: its session reopens."""
        reopened = Ticket(self._session.reopen(), self._board)
        final = self._stages[-1]
        return reopened._enter(final)._mark(MARKED_DONE, final)

    def _return_to_backlog(self) -> BacklogItem:
        """Into the Backlog from any column: its session closes and its whole folder becomes a backlog item, so starting
        the item brings the ticket back with its work."""
        from harness.kanban.backlog_item import BacklogItem

        self._session.close()
        kept_in_backlog = Ticket(self._session.move_to_backlog(), self._board)
        item = BacklogItem.from_ticket(kept_in_backlog, self._board)
        item.write_if_missing(kept_in_backlog.title)
        return item

    @property
    def _folder(self) -> Path:
        return self._session.session_path

    @property
    def _stages(self) -> list[Stage]:
        return [column for column in self._board.columns if isinstance(column, Stage)]

    @property
    def _enabled_progress(self) -> list[FidelityProgress]:
        return [entry for entry in self.progress if entry.is_enabled]

    def _moved_into(self) -> Stage | None:
        moves = [entry.stage for entry in self._session.log_entries if entry.verb == MOVED_INTO and entry.stage]
        return next((stage for stage in self._stages if moves and stage.name == moves[-1]), None)

    def _latest_mark(self, stage: Stage) -> str | None:
        """The latest mark a person made in stage since entering it; none when they have made none."""
        latest = None
        for entry in self._session.log_entries:
            if entry.stage == stage.name and entry.verb in (MOVED_INTO, MARKED_DONE, MARKED_IN_PROGRESS):
                latest = None if entry.verb == MOVED_INTO else entry.verb
        return latest

    def _mark(self, mark: str, stage: Stage) -> Ticket:
        self._session.record(f"{mark} {stage.name}")
        return self

    def _enter(self, stage: Stage) -> Ticket:
        self._session.record(f"{MOVED_INTO} {stage.name}")
        return self

    def _render_command(self, progress: FidelityProgress, formats: list[str]) -> str:
        """The command that renders the fidelity before progress's into formats it has no file in, when it has work to render."""
        earlier = next((entry for entry in self.progress if entry.practice == progress.practice and entry.stage.next_stage is progress.stage), None)
        if earlier is None:
            return ""
        made = {label for label, entries in earlier.files().items() if any(entry.exists for entry in entries)}
        wanted = [label for label in formats if label in earlier.fidelity.outputs and label not in made]
        if not made or not wanted:
            return ""
        return f"/actions-render {earlier.fidelity_slug.replace('_', '-')} format={','.join(wanted)} source={sorted(made)[0]}"


@language_adapter(language="typescript", identity=("ticket", "slug"))
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
        done_verbs = {verb for _, verb in naming if verb == GENERATE}
        done_verbs |= {VALIDATE} if validated else set()
        done_verbs |= {REVIEW} if reviewed else set()
        read = cls(fidelity, stage, [action for action in stage.actions if action in done_verbs], has_violations, ticket)
        return read.with_violations() if read._is_judged_failing else read

    @classmethod
    @tool_subject
    def load(cls, ticket: str, fidelity: str) -> FidelityProgress:
        """The progress of fidelity, a slug such as stories-story_map, on the ticket named ticket."""
        return Ticket.load(ticket).progress_of(fidelity)

    @property
    @data_field
    def ticket(self) -> str:
        """The name of the ticket this progress is on, which with its slug names it."""
        return self._ticket.name

    @property
    @data_field(key="slug")
    def fidelity_slug(self) -> str:
        """Its practice and fidelity, such as stories-story_map. Named apart from `slug`, which names the toolset its tools are published under."""
        return self.slug_of(self._fidelity)

    @property
    def fidelity(self) -> FidelityGuidance:
        return self._fidelity

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    @data_field
    def practice(self) -> str:
        return self._fidelity.practice_guidance.key

    @property
    @data_field
    def is_enabled(self) -> bool:
        """Whether the ticket's session works on this fidelity's practice."""
        return self._ticket.session.practices[self.practice].enabled

    @property
    def done_actions(self) -> list[str]:
        return list(self._done_actions)

    @property
    def remaining_actions(self) -> list[str]:
        return [action for action in self._stage.actions if action not in self._done_actions]

    @property
    @data_field
    def next_action(self) -> str:
        """What Run next does on this fidelity: satisfy while it has violations, else the first of its stage's actions
        not done, or nothing once it is done."""
        if self._has_violations:
            return SATISFY
        remaining = self.remaining_actions
        return remaining[0] if remaining else ""

    @property
    @data_field
    def allowed_actions(self) -> list[str]:
        """Generate always; Validate and Review as soon as any action on the fidelity is recorded, so a person can check
        the same output again as often as they like."""
        return [*ALWAYS_ALLOWED, *ONCE_THERE_IS_OUTPUT] if self._done_actions else list(ALWAYS_ALLOWED)

    @property
    def has_violations(self) -> bool:
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
        states = {action: "done" if action in self._done_actions else "to_do" for action in self._stage.actions}
        if self._has_violations:
            states[VALIDATE] = "in_progress"
        return ActionStates(states)

    @property
    @data_field
    def report_file(self) -> str:
        """Its latest validation report, as a path from the project; empty when it has none. Validate saves a report
        before the agent judges it, so a report with no judgment and no saved graph yet does not hide an earlier one
        that has its result."""
        latest = self._latest_report_of(self._fidelity)
        return self._ticket.session.from_project(latest) if latest else ""

    @property
    @data_field
    def violation_count(self) -> int:
        """How many violations its latest report names, graph hits and judged findings; none while it has no violations."""
        return self.report().violation_count if self._has_violations else 0

    @mcp
    @agent_tool
    @noSessionLog
    def finish_review(self) -> FidelityProgress:
        """Record that a person has reviewed and approved this fidelity: a review line in its ticket's session log. A review counts until the fidelity is validated again, and a fidelity whose actions are all done is done in its stage."""
        self._ticket.session.record(f"{REVIEW} {type(self._fidelity.practice_guidance).__name__} {self._fidelity.name}")
        return self._ticket.progress_of(self.fidelity_slug)

    @mcp
    @agent_tool
    @noSessionLog
    def report(self) -> Report:
        """Return this fidelity's latest validation report: its path and text, and the rules broken in it, each with its description and each violation with its line and the source around it. The rules are those broken on the nodes of the graph saved beside the report, then each rule the validating agent's judgment fails that the graph did not hit. has_saved_graph is false when the report has no saved graph, so its graph's rules are missing."""
        latest = self._latest_report_of(self._fidelity)
        if latest is None:
            return Report()
        return self._report_file(latest).report(self, self._superseded(latest))

    @mcp
    @agent_tool
    @noSessionLog
    def files(self) -> dict[str, list[FileEntry]]:
        """List the files this fidelity declares by format in its ticket's session, each with its path from the project and whether it exists. A pattern lists the files the ticket worked on, not every match in the repository."""
        return self._ticket.session.practices[self.practice].fidelities[self._fidelity.name].files()

    def with_violations(self) -> FidelityProgress:
        """This progress with its latest validate failed, so validate is to do again; a person's review stands."""
        kept = [action for action in self._done_actions if action in (GENERATE, REVIEW)]
        return FidelityProgress(self._fidelity, self._stage, kept, True, self._ticket)

    def slug_of(self, fidelity: FidelityGuidance) -> str:
        return f"{self.practice}-{fidelity.name}"

    @property
    def earlier_fidelities(self) -> list[FidelityGuidance]:
        """The fidelities of this practice that come before this one."""
        names = [fidelity.name for fidelity in self._practice_fidelities]
        return self._practice_fidelities[:names.index(self._fidelity.name)] if self._fidelity.name in names else []

    def rule_slugs_without(self, superseded: list[FidelityGuidance]) -> set[str]:
        """The practice's shared rules, this fidelity's own, and every earlier fidelity's but the superseded ones."""
        dropped = {fidelity.name for fidelity in superseded}
        earlier = [rule for fidelity in self.earlier_fidelities if fidelity.name not in dropped for rule in fidelity.rules]
        return {rule.slug for rule in [*self._fidelity.practice_guidance.rules, *earlier, *self._fidelity.rules]}

    @property
    def rule_descriptions(self) -> dict[str, str]:
        """Each rule's text by slug. A saved graph holds the whole practice's hits, so every fidelity's rules count; this fidelity's own win."""
        practice = self._fidelity.practice_guidance
        rules = [*practice.rules, *(rule for fidelity in self._practice_fidelities for rule in fidelity.rules), *self._fidelity.rules]
        return {rule.slug: rule.body.strip() for rule in rules}

    @property
    def _practice_fidelities(self) -> list[FidelityGuidance]:
        return list(self._fidelity.practice_guidance.fidelities)

    @property
    def _is_judged_failing(self) -> bool:
        """A validate the log shows passing still failed when the judgment the validating agent added to its report fails a rule."""
        if VALIDATE not in self._done_actions:
            return False
        latest = self._latest_report_of(self._fidelity)
        return latest is not None and self._report_file(latest).is_judged_failing

    def _latest_report_of(self, fidelity: FidelityGuidance) -> Path | None:
        """The latest report of fidelity in its ticket's session that has its result, else its latest; none when it has none."""
        own = self._ticket.session.practices[self.practice].fidelities[fidelity.name].reports()
        with_result = [report for report in own if self._report_file(report).has_result]
        return (with_result or own or [None])[-1]

    def _superseded(self, report: Path) -> list[FidelityGuidance]:
        """The earlier fidelities with a report newer than report, whose rules that newer report answers for."""
        stamp = self._report_file(report).stamp
        return [earlier for earlier in self.earlier_fidelities if self._stamp_of(self._latest_report_of(earlier)) > stamp]

    def _stamp_of(self, report: Path | None) -> str:
        return self._report_file(report).stamp if report else ""

    def _report_file(self, file: Path) -> ReportFile:
        session = self._ticket.session
        repo = Repo(session.repo_from_session())
        return ReportFile(file, repo, Path(session.workpath or repo.root).resolve())


class ActionStates:
    """Where each of a stage's actions stands on one fidelity: to_do, in_progress, or done."""

    def __init__(self, states: dict[str, str]) -> None:
        self._states = dict(states)

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
