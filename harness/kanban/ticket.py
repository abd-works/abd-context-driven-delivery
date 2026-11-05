"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

from datetime import datetime, timezone
from fnmatch import fnmatch
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
    PracticeNotFoundError,
    Stage,
)
from harness.kanban.report import Report, ReportFile
from harness.kanban.ticket_files import FileEntry, TicketFiles
from harness.mcp.mcp_server import mcp
from space.session import Session, name_of
from tools.file_manager.file_manager import FileText

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.board import Column

LOG_FILE = "session.log"
HANDOFF_FILES = "handoff-*.md"
REPORT_FOLDER = "validation-reports"
GRAPH_RULE_VIOLATION = "graph-rule"
MOVED_INTO = "move"
MARKED_DONE = "done"
MARKED_IN_PROGRESS = "in-progress"
LEAVE_COMMIT = "commit"
LEAVE_PUSH = "push"
LEAVE_MERGE = "merge"
OPEN_BRANCH = "branch"
OPEN_WORKTREE = "worktree"
SATISFY = "satisfy"
ALWAYS_ALLOWED = (GENERATE,)
ONCE_THERE_IS_OUTPUT = (VALIDATE, REVIEW)
# A session log line is `<timestamp> <verb> <subject...>`: the verb is its second word, and on a move or a mark the
# stage it names is its third.
VERB_WORD = 1
STAGE_WORD = 2


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
    def scope(self) -> str:
        return self._session.scope

    @property
    def parent(self) -> Ticket | None:
        """The ticket this one was split from; none when it was not split from one."""
        named = self._session.parent
        return self._board.ticket(named) if named else None

    @property
    @data_field(key="parent")
    def parent_name(self) -> str:
        return self._session.parent

    @property
    @data_field
    def practices(self) -> dict[str, bool]:
        """Which practices this ticket works on: every practice until a person turns it off."""
        active = {practice.name for practice in self._session.active_practices}
        return {practice.key: practice.key in active for practice in self._board.practices}

    @property
    def progress(self) -> list[FidelityProgress]:
        """One per fidelity the board requires, in stage order; read from the session log each time, with the latest
        report's judgment able to fail a validate the log shows passing."""
        lines = self._log_lines()
        reports = self._report_files()
        return [
            self._judged(FidelityProgress.from_log(fidelity, stage, lines), reports)
            for stage in self._stages
            for fidelity in stage.work_required
        ]

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
        upcoming = self.next_fidelity
        return upcoming.slug if upcoming else None

    @property
    @data_field
    def next_action(self) -> str:
        """What Run next does: generate, validate, or review on the next fidelity, or satisfy while it has violations."""
        upcoming = self.next_fidelity
        if upcoming is None:
            return ""
        return SATISFY if upcoming.has_violations else upcoming.remaining_actions[0]

    @property
    def last_activity(self) -> str:
        lines = self._log_lines()
        return lines[-1].split(" ", 1)[0] if lines else ""

    @property
    @data_field(key="handoff")
    def latest_handoff(self) -> str:
        """The newest handoff file, as a path from the project; handoff names sort by their timestamp."""
        handoffs = sorted(self._folder.glob(HANDOFF_FILES))
        return self._from_repository(handoffs[-1]) if handoffs else ""

    @property
    @data_field
    def reports(self) -> dict[str, str]:
        """The latest validation report of each fidelity that has one, as paths from the project; report names sort by their date.
        Validate saves a report before the agent judges it, so a report with no judgment and no saved graph yet does not
        hide an earlier one that has its result."""
        files = self._report_files()
        found = {progress.slug: progress.reports_among(files) for progress in self.progress}
        return {slug: self._from_repository(self._latest_with_result(reports)) for slug, reports in found.items() if reports}

    @property
    @data_field
    def violation_counts(self) -> dict[str, int]:
        """How many violations the latest report names, graph hits and judged findings, for each fidelity left with violations."""
        counts = {entry.slug: self.report(entry.slug).violation_count for entry in self.progress if entry.has_violations}
        return {slug: count for slug, count in counts.items() if count}

    @property
    @data_field(key="progress")
    def fidelity_states(self) -> dict[str, str]:
        """done, violations, in_progress, or not_started for each fidelity: what the board colours."""
        return {entry.slug: entry.state for entry in self.progress}

    @property
    @data_field(key="actions")
    def fidelity_actions(self) -> dict[str, ActionStates]:
        return {entry.slug: entry.action_states for entry in self.progress}

    @property
    @data_field
    def allowed_actions(self) -> dict[str, list[str]]:
        return {entry.slug: self._allowed_actions(entry) for entry in self.progress}

    @property
    @data_field
    def workpath(self) -> str:
        """The folder the session works in, as a path from the project; empty for the whole repository."""
        return self._from_repository(self._workpath)

    @property
    @data_field
    def worktree(self) -> str:
        """The folder of the ticket's own worktree, where its chat works; empty while it has none."""
        found = self._board.worktree_of(self.name)
        return str(found) if found else ""

    @property
    @data_field
    def practice_roots(self) -> dict[str, PracticeRoot]:
        """Where each practice writes, as a path from the project, and whether a person chose it or it is the default."""
        guidances = {entry.practice: entry.fidelity.practice_guidance for entry in self.progress}
        return {
            practice: PracticeRoot(self._from_repository(self._session.practice_root(guidance, practice).resolve()), self._session.has_chosen_practice_root(practice))
            for practice, guidance in guidances.items()
        }

    @property
    @data_field
    def session_file(self) -> str:
        """Its session.json as a path from the project. Every command the board sends names it, because a command runs
        in whichever chat it is sent to, and that chat's open session can be another."""
        return self._from_repository(self._session.session_file)

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
            return self.reopen()
        if self.is_done:
            return self._mark(MARKED_IN_PROGRESS, column)
        earlier = column.previous_stage
        if earlier is None:
            return self.return_to_backlog()
        return self._enter(earlier)._mark(MARKED_DONE, earlier)

    @mcp
    @agent_tool
    @noSessionLog
    def move_to(self, stage: str, done: bool = False) -> Ticket | BacklogItem:
        """Move ticket straight into stage's In progress, or its Done when done is true, whatever its work; dragging a card does this. Out of Complete it reopens first. Into the Backlog, from any column, it becomes a backlog item that keeps its whole folder."""
        if stage == BACKLOG_COLUMN:
            return self.return_to_backlog()
        target = next((column for column in self._stages if column.name == stage), None)
        if target is None:
            raise NotAStageError(stage)
        moved = self if isinstance(self.column, Stage) else Ticket(self._session.reopen(), self._board)
        entered = moved if moved.column is target else moved._enter(target)
        return entered._mark(MARKED_DONE if done else MARKED_IN_PROGRESS, target)

    def reopen(self) -> Ticket:
        """Back out of Complete into Implementation's Done: its session reopens."""
        reopened = Ticket(self._session.reopen(), self._board)
        final = self._stages[-1]
        return reopened._enter(final)._mark(MARKED_DONE, final)

    def return_to_backlog(self) -> BacklogItem:
        """Into the Backlog from any column: its session closes and its whole folder becomes a backlog item, so starting
        the item brings the ticket back with its work."""
        from harness.kanban.backlog_item import BacklogItem

        self._session.close()
        kept_in_backlog = Ticket(self._session.move_to_backlog(), self._board)
        item = BacklogItem.from_ticket(kept_in_backlog, self._board)
        item.write_if_missing(kept_in_backlog.title)
        return item

    @mcp
    @agent_tool
    @noSessionLog
    def close(self, leaving: list[str] | None = None) -> Ticket:
        """Close ticket: its session ends, its folder moves to closed/, and it shows in Complete. leaving names what to do with its work first: commit, push, merge."""
        self.leave(leaving or [])
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
    def activate(self, leaving: list[str] | None = None, opening: list[str] | None = None) -> Ticket:
        """Make ticket the current session. leaving names what to do with the active ticket's work first: commit, push, merge. opening names what to create for this ticket: branch, worktree."""
        active = self._board.active
        if active is not None and active.name != self.name:
            active.leave(leaving or [])
        self.open_workspace(opening or [])
        Session.switch(self.name, repo_path=self._board.repo.root)
        return self

    def leave(self, leaving: list[str]) -> None:
        """Do what leaving names with this ticket's work: commit, push, merge. Only on its own branch, checked out,
        because those steps act on whatever is checked out."""
        if not leaving or not self._is_on_its_branch:
            return
        repo = self._board.repo
        if LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving:
            repo.push_commit(f"{self.name}: leave session", sync_remote=LEAVE_PUSH in leaving)
        if LEAVE_MERGE in leaving:
            repo.close_branch(self.name)

    def open_workspace(self, opening: list[str]) -> None:
        """Create and open what opening names for this ticket: its branch, its worktree."""
        if OPEN_BRANCH in opening:
            self._board.repo.switch_branch(self.name)
        if OPEN_WORKTREE in opening:
            self._board.repo.switch_worktree(self.name)

    @mcp
    @agent_tool
    @noSessionLog
    def open_worktree(self) -> Ticket:
        """Open ticket's own worktree beside the repository, creating its branch when missing: the folder its chat works in, named as its worktree. The open session is left as it is."""
        self._board.repo.branch_named(self.name).open_in_worktree()
        return Ticket(self._session, Board.load(self._board.repo.root))

    @mcp
    @agent_tool
    @noSessionLog
    def workspace(self) -> Workspace:
        """Say whether ticket already has its branch and its worktree, so activating it offers only what is missing, and whether the active ticket being left is on a branch of its own, so its work can be committed, pushed, and merged."""
        active = self._board.active
        return Workspace(
            self._board.repo.has_branch(self.name),
            self._board.worktree_of(self.name) is not None,
            active is not None and active._is_on_its_branch,
        )

    @mcp
    @agent_tool
    @noSessionLog
    def finish_review(self, fidelities: list[str]) -> Ticket:
        """Record that a person has reviewed and approved fidelities, slugs such as stories-story_map, on ticket: one review line each in its session log. A review counts until the fidelity is validated again, and a fidelity whose actions are all done is done in its stage."""
        approved = [self._progress_of(slug).fidelity for slug in fidelities]
        for fidelity in approved:
            self.record(f"{REVIEW} {type(fidelity.practice_guidance).__name__} {fidelity.name}")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def choose_workpath(self, path: str) -> Ticket:
        """Make path, a folder in the repository, ticket's workpath: the folder its session works in and its graph loads from. An empty path is the whole repository."""
        self._session.choose_workpath(self._board.repo.root / path)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def choose_practice_root(self, practice: str, path: str) -> Ticket:
        """Write practice's files under path, a folder in the repository, for this ticket."""
        self._session.choose_practice_root(practice, self._board.repo.root / path)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def use_default_practice_root(self, practice: str) -> Ticket:
        """Write practice's files under its default practice root again: the ticket's workpath plus the practice's own folder."""
        self._session.use_default_practice_root(practice)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def enable_practice(self, practice: str, is_enabled: bool) -> Ticket:
        """Turn practice on or off for ticket, saved in its session.json."""
        if practice not in self.practices:
            raise PracticeNotFoundError(practice, f"ticket {self.name!r}")
        self._session.enable_practice(practice, is_enabled)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def files(self, fidelities: list[str]) -> dict[str, dict[str, list[FileEntry]]]:
        """List the files fidelities declare by format, each with its path from the project and whether it exists. A pattern lists the files this ticket worked on, not every match in the repository."""
        return {progress.slug: self._files.declared_by(progress.fidelity) for progress in self.progress if progress.slug in fidelities}

    @mcp
    @agent_tool
    @noSessionLog
    def session_files(self) -> list[FileEntry]:
        """List every file in ticket's session folder, each with its path from the project: its log, handoffs, kept notes, and validation reports."""
        return self._files.in_session_folder()

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str) -> FileText:
        """Return the text of path, a file in this repository; no text when the file is gone, such as one deleted since the board listed it."""
        return self._files.read(path)

    @mcp
    @agent_tool
    @noSessionLog
    def report(self, fidelity: str) -> Report:
        """Return the latest validation report of fidelity, a slug such as stories-story_map: its path and text, and the rules broken in it, each with its description and each violation with its line and the source around it. The rules are those broken on the nodes of the graph saved beside the report, then each rule the validating agent's judgment fails that the graph did not hit. has_saved_graph is false when the report has no saved graph, so its graph's rules are missing."""
        path = self.reports.get(fidelity, "")
        if not path:
            return Report()
        progress = self._progress_of(fidelity)
        return self._report_file(self._board.repo.root / path).report(progress, self._superseded(path, progress))

    @mcp
    @agent_tool
    @noSessionLog
    def violations(self) -> Report:
        """Return the rules broken on every fidelity of the ticket's stage left with violations, across its practices, each rule naming its fidelity, in the shape of ticket.report. path is the folder the reports sit in. A saved graph holds its whole practice's hits, so a rule two fidelities share is listed once. has_saved_graph is false when a report has no saved graph, so its rules are missing."""
        column = self.column
        reports = [self.report(entry.slug) for entry in self.progress if entry.has_violations and entry.stage is column]
        return Report.from_reports(self._from_repository(self._folder / REPORT_FOLDER), reports)

    @mcp
    @agent_tool
    @noSessionLog
    def generate_commands(self, fidelities: list[str], formats: list[str]) -> list[str]:
        """Return the commands that generate fidelities in formats. A format the same practice's earlier fidelity has no file in is rendered from that fidelity first."""
        renders = [self._render_command(self._progress_of(slug), formats) for slug in fidelities]
        named = " ".join(slug.replace("_", "-") for slug in fidelities)
        commands = [*filter(None, renders), f"/actions-generate {named} format={','.join(formats)}"]
        return [f"{command} session={self.session_file}" for command in commands]

    def keep_file(self, file: Path) -> Path:
        """Keep file, such as a started backlog item's idea, with this ticket's work in its session folder."""
        return self._session.keep_file(file)

    def record(self, entry: str) -> None:
        with (self._folder / LOG_FILE).open("a", encoding="utf-8") as log:
            log.write(f"{self._timestamp(datetime.now(timezone.utc))} {entry}\n")

    def _allowed_actions(self, progress: FidelityProgress) -> list[str]:
        """Generate always; Validate and Review as soon as any action on the fidelity is recorded, so a person can check
        the same output again as often as they like. Files already on disk are listed by `files`, which the board reads
        when a person opens the fidelity; reading them here would search the disk on every board read."""
        return [*ALWAYS_ALLOWED, *ONCE_THERE_IS_OUTPUT] if progress.done_actions else list(ALWAYS_ALLOWED)

    @property
    def _folder(self) -> Path:
        return self._session.session_path

    @property
    def _workpath(self) -> Path:
        """The folder the session works in; the repository when it names none. A saved graph names its files from here."""
        return Path(self._session.workpath or self._board.repo.root).resolve()

    @property
    def _stages(self) -> list[Stage]:
        return [column for column in self._board.columns if isinstance(column, Stage)]

    @property
    def _enabled_progress(self) -> list[FidelityProgress]:
        practices = self.practices
        return [entry for entry in self.progress if practices[entry.practice]]

    def _progress_of(self, slug: str) -> FidelityProgress:
        """The progress of the fidelity slug names, such as stories-story_map."""
        found = next((entry for entry in self.progress if entry.slug == slug), None)
        if found is None:
            raise FidelityNotFoundError(slug, f"ticket {self.name!r}")
        return found

    def _report_files(self) -> list[Path]:
        """Every validation report in the session folder, oldest first; report names sort by their date."""
        folder = self._folder / REPORT_FOLDER
        return sorted(folder.glob("*.md")) if folder.is_dir() else []

    def _judged(self, progress: FidelityProgress, reports: list[Path]) -> FidelityProgress:
        """A validate the log shows passing still failed when the judgment the validating agent added to its report fails a rule."""
        if VALIDATE not in progress.done_actions:
            return progress
        own = progress.reports_among(reports)
        if not own or not self._report_file(self._latest_with_result(own)).is_judged_failing:
            return progress
        return progress.with_violations()

    def _latest_with_result(self, reports: list[Path]) -> Path:
        with_result = [report for report in reports if self._report_file(report).has_result]
        return (with_result or reports)[-1]

    def _report_file(self, file: Path) -> ReportFile:
        return ReportFile(file, self._board.repo, self._workpath)

    @cached_property
    def _files(self) -> TicketFiles:
        return TicketFiles(self._session, self._board.repo, self.name)

    def _log_lines(self) -> list[str]:
        path = self._folder / LOG_FILE
        if not path.is_file():
            return []
        return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _moved_into(self) -> Stage | None:
        moves = [stage for verb, stage in map(_verb_and_stage, self._log_lines()) if verb == MOVED_INTO and stage]
        return next((stage for stage in self._stages if moves and stage.name == moves[-1]), None)

    def _latest_mark(self, stage: Stage) -> str | None:
        """The latest mark a person made in stage since entering it; none when they have made none."""
        latest = None
        for verb, named in map(_verb_and_stage, self._log_lines()):
            if named == stage.name and verb in (MOVED_INTO, MARKED_DONE, MARKED_IN_PROGRESS):
                latest = None if verb == MOVED_INTO else verb
        return latest

    def _mark(self, mark: str, stage: Stage) -> Ticket:
        self.record(f"{mark} {stage.name}")
        return self

    def _enter(self, stage: Stage) -> Ticket:
        self.record(f"{MOVED_INTO} {stage.name}")
        return self

    def _from_repository(self, path: Path | str) -> str:
        return self._board.repo.path_from_top(path)

    @property
    def _is_on_its_branch(self) -> bool:
        """Whether the repository has this ticket's branch checked out; a commit lands on whatever is checked out."""
        repo = self._board.repo
        return repo.has_branch(self.name) and repo.current_branch == self.name

    def _superseded(self, report: str, progress: FidelityProgress) -> list[FidelityGuidance]:
        """The earlier fidelities with a report newer than report, whose rules that newer report answers for."""
        reports = self.reports
        return [earlier for earlier in progress.earlier_fidelities if _report_stamp(reports.get(progress.slug_of(earlier), "")) > _report_stamp(report)]

    def _render_command(self, progress: FidelityProgress, formats: list[str]) -> str:
        """The command that renders the fidelity before progress's into formats it has no file in, when it has work to render."""
        earlier = next((entry for entry in self.progress if entry.practice == progress.practice and entry.stage.next_stage is progress.stage), None)
        if earlier is None:
            return ""
        made = {label for label, entries in self._files.declared_by(earlier.fidelity).items() if any(entry.exists for entry in entries)}
        wanted = [label for label in formats if label in earlier.fidelity.outputs and label not in made]
        if not made or not wanted:
            return ""
        return f"/actions-render {earlier.slug.replace('_', '-')} format={','.join(wanted)} source={sorted(made)[0]}"


class FidelityProgress:
    """*FidelityProgress* is how far one fidelity has got through its stage's actions on one ticket."""

    # Validate is done when its latest line names no graph-rule violations and, as the ticket judges it, the latest
    # report's judgment fails no rule. Review is done once a person reviews after the latest validate, passed or not.

    def __init__(self, fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool) -> None:
        self._fidelity = fidelity
        self._stage = stage
        self._done_actions = list(done_actions)
        self._has_violations = has_violations

    @classmethod
    def from_log(cls, fidelity: FidelityGuidance, stage: Stage, lines: list[str]) -> FidelityProgress:
        """Read the actions done on this fidelity from session log lines, finding it by name, never by position."""
        naming = cls._actions_naming(fidelity, lines)
        validations = [index for index, verb in naming if verb == VALIDATE]
        latest_validation = validations[-1] if validations else None
        has_violations = latest_validation is not None and GRAPH_RULE_VIOLATION in lines[latest_validation]
        validated = latest_validation is not None and not has_violations
        reviewed = any(verb == REVIEW and (latest_validation is None or index > latest_validation) for index, verb in naming)
        done_verbs = {verb for _, verb in naming if verb == GENERATE}
        done_verbs |= {VALIDATE} if validated else set()
        done_verbs |= {REVIEW} if reviewed else set()
        return cls(fidelity, stage, [action for action in stage.actions if action in done_verbs], has_violations)

    @staticmethod
    def _actions_naming(fidelity: FidelityGuidance, lines: list[str]) -> list[tuple[int, str]]:
        """Each log line that names fidelity and its practice, as its position and its verb. Action lines name the
        practice by its folder (`clean_engineering`) and validate lines by its class (`CleanEngineering`)."""
        practice = fidelity.practice_guidance
        spellings = {practice.key, type(practice).__name__}
        words_of = [_words_without_commas(line) for line in lines]
        return [(index, words[VERB_WORD]) for index, words in enumerate(words_of)
                if len(words) > VERB_WORD and fidelity.name in words[VERB_WORD + 1:] and spellings & set(words[VERB_WORD + 1:])]

    @property
    def fidelity(self) -> FidelityGuidance:
        return self._fidelity

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    def practice(self) -> str:
        return self._fidelity.practice_guidance.key

    @property
    def done_actions(self) -> list[str]:
        return list(self._done_actions)

    @property
    def remaining_actions(self) -> list[str]:
        return [action for action in self._stage.actions if action not in self._done_actions]

    @property
    def has_violations(self) -> bool:
        return self._has_violations

    @property
    def is_done(self) -> bool:
        return not self.remaining_actions

    @property
    def slug(self) -> str:
        return self.slug_of(self._fidelity)

    def with_violations(self) -> FidelityProgress:
        """This progress with its latest validate failed, so validate is to do again; a person's review stands."""
        return FidelityProgress(self._fidelity, self._stage, [action for action in self._done_actions if action in (GENERATE, REVIEW)], True)

    def slug_of(self, fidelity: FidelityGuidance) -> str:
        return f"{self.practice}-{fidelity.name}"

    def reports_among(self, reports: list[Path]) -> list[Path]:
        """This fidelity's dated validation reports among reports, in the order given."""
        pattern = f"{self.slug.replace('_', '-')}-*.md"
        return [report for report in reports if fnmatch(report.name, pattern)]

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
    def state(self) -> str:
        """done, violations, in_progress, or not_started: what the board pane colours."""
        if self.is_done:
            return "done"
        if self._has_violations:
            return "violations"
        return "in_progress" if self._done_actions else "not_started"

    @property
    def action_states(self) -> ActionStates:
        """Each action as to_do, in_progress, or done. A validate that left violations is in progress until they are fixed."""
        states = {action: "done" if action in self._done_actions else "to_do" for action in self._stage.actions}
        if self._has_violations:
            states[VALIDATE] = "in_progress"
        return ActionStates(states)


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


class PracticeRoot:
    """Where one practice writes, as a path from the project, and whether a person chose it or it is the default."""

    def __init__(self, root: str, is_chosen: bool) -> None:
        self._root = root
        self._is_chosen = is_chosen

    @property
    @data_field
    def root(self) -> str:
        return self._root

    @property
    @data_field
    def is_chosen(self) -> bool:
        return self._is_chosen


class Workspace:
    """Whether a ticket has its branch and its worktree, and whether the active ticket being left is on a branch of its own."""

    def __init__(self, has_branch: bool, has_worktree: bool, leaving_has_branch: bool) -> None:
        self._has_branch = has_branch
        self._has_worktree = has_worktree
        self._leaving_has_branch = leaving_has_branch

    @property
    @data_field
    def has_branch(self) -> bool:
        return self._has_branch

    @property
    @data_field
    def has_worktree(self) -> bool:
        return self._has_worktree

    @property
    @data_field
    def leaving_has_branch(self) -> bool:
        return self._leaving_has_branch


def _report_stamp(report: str) -> str:
    """The date a report's name ends with; names stamp it in a form that sorts by time. Nothing for no report."""
    return Path(report).stem.rsplit("-", 1)[-1] if report else ""


def _words_without_commas(line: str) -> list[str]:
    """A log line's words, without the commas that join the paths an action names."""
    return [word.rstrip(",") for word in line.split()]


def _verb_and_stage(line: str) -> tuple[str, str]:
    """A log line's verb and the word after it, which names the stage on a move or a mark."""
    words = line.split()
    verb = words[VERB_WORD] if len(words) > VERB_WORD else ""
    return verb, words[STAGE_WORD] if len(words) > STAGE_WORD else ""
