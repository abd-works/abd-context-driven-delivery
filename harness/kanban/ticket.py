"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from fnmatch import fnmatch
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import language_adapter
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
from harness.kanban.data import (
    FileEntryData,
    FileTextData,
    PracticeRootData,
    ReportData,
    ReportRuleData,
    SourceLineData,
    TicketData,
    ViolationData,
    WorkspaceData,
)
from harness.mcp.mcp_server import mcp
from space.session import Session, name_of

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
SOURCE_LINES_BEFORE = 2
SOURCE_LINES_AFTER = 4
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


class FileOutsideRepositoryError(ValueError):
    """Raised when a tool asks a ticket for a file outside its repository. It names the path and the ticket."""

    def __init__(self, path: str, ticket: str) -> None:
        self.path = path
        self.ticket = ticket
        super().__init__(f"{path!r} is not a file in this repository")


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
    def name(self) -> str:
        """Its session's name. A ticket is an agent toolset, whose own name is the toolset's, so without this a
        ticket's name would read "ticket"."""
        return self._session.name

    @property
    def title(self) -> str:
        return self._session.title or self._session.name

    @property
    def scope(self) -> str:
        return self._session.scope

    @property
    def parent(self) -> Ticket | None:
        """The ticket this one was split from; none when it was not split from one."""
        named = self._session.parent
        return self._board.ticket(named) if named else None

    @property
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
    def latest_handoff(self) -> str:
        """The newest handoff file, as a path from the project; handoff names sort by their timestamp."""
        handoffs = sorted(self._folder.glob(HANDOFF_FILES))
        return self._from_repository(handoffs[-1]) if handoffs else ""

    @property
    def reports(self) -> dict[str, str]:
        """The latest validation report of each fidelity that has one, as paths from the project; report names sort by their date.
        Validate saves a report before the agent judges it, so a report with no judgment and no saved graph yet does not
        hide an earlier one that has its result."""
        files = self._report_files()
        found = {progress.slug: progress.reports_among(files) for progress in self.progress}
        return {slug: self._from_repository(self._latest_with_result(reports)) for slug, reports in found.items() if reports}

    @property
    def violation_counts(self) -> dict[str, int]:
        """How many violations the latest report names, graph hits and judged findings, for each fidelity left with violations."""
        counts = {entry.slug: sum(rule["count"] for rule in self.report(entry.slug)["rules"]) for entry in self.progress if entry.has_violations}
        return {slug: count for slug, count in counts.items() if count}

    @property
    def workpath(self) -> str:
        """The folder the session works in, as a path from the project; empty for the whole repository."""
        return self._from_repository(self._workpath)

    @property
    def worktree(self) -> str:
        """The folder of the ticket's own worktree, where its chat works; empty while it has none."""
        found = self._board.worktree_of(self.name)
        return str(found) if found else ""

    @property
    def practice_roots(self) -> dict[str, PracticeRootData]:
        """Where each practice writes, as a path from the project, and whether a person chose it or it is the default."""
        guidances = {entry.practice: entry.fidelity.practice_guidance for entry in self.progress}
        return {
            practice: {"root": self._from_repository(self._session.practice_root(guidance, practice).resolve()), "is_chosen": self._session.has_chosen_practice_root(practice)}
            for practice, guidance in guidances.items()
        }

    @property
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
    def workspace(self) -> WorkspaceData:
        """Say whether ticket already has its branch and its worktree, so activating it offers only what is missing, and whether the active ticket being left is on a branch of its own, so its work can be committed, pushed, and merged."""
        repo = self._board.repo
        active = self._board.active
        return {
            "has_branch": repo.has_branch(self.name),
            "has_worktree": self._board.worktree_of(self.name) is not None,
            "leaving_has_branch": active is not None and active._is_on_its_branch,
        }

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
    def files(self, fidelities: list[str]) -> dict[str, dict[str, list[FileEntryData]]]:
        """List the files fidelities declare by format, each with its path from the project and whether it exists. A pattern lists the files this ticket worked on, not every match in the repository."""
        return {progress.slug: self._files_of(progress.fidelity) for progress in self.progress if progress.slug in fidelities}

    @mcp
    @agent_tool
    @noSessionLog
    def session_files(self) -> list[FileEntryData]:
        """List every file in ticket's session folder, each with its path from the project: its log, handoffs, kept notes, and validation reports."""
        files = sorted(path for path in self._folder.rglob("*") if path.is_file())
        return [{"path": self._from_repository(path), "exists": True} for path in files]

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str) -> FileTextData:
        """Return the text of path, a file in this repository; no text when the file is gone, such as one deleted since the board listed it."""
        target = self._inside_repository(path)
        if target is None:
            raise FileOutsideRepositoryError(path, self.name)
        text = target.read_text(encoding="utf-8", errors="replace") if target.is_file() else ""
        return {"path": path, "text": text}

    @mcp
    @agent_tool
    @noSessionLog
    def report(self, fidelity: str) -> ReportData:
        """Return the latest validation report of fidelity, a slug such as stories-story_map: its path and text, and the rules broken in it, each with its description and each violation with its line and the source around it. The rules are those broken on the nodes of the graph saved beside the report, then each rule the validating agent's judgment fails that the graph did not hit. has_saved_graph is false when the report has no saved graph, so its graph's rules are missing."""
        path = self.reports.get(fidelity, "")
        if not path:
            return {"path": "", "text": "", "rules": [], "has_saved_graph": False}
        progress = self._progress_of(fidelity)
        graph = self._graph_of(path)
        text = (self._board.repo.root / path).read_text(encoding="utf-8", errors="replace")
        graph_rules = self._rules_broken_in(path, progress) if graph.is_file() else []
        hit = {rule["name"] for rule in graph_rules}
        judged = [rule for rule in self._judged_rules(text, progress) if rule["name"] not in hit]
        return {"path": path, "text": text, "rules": graph_rules + judged, "has_saved_graph": graph.is_file()}

    @mcp
    @agent_tool
    @noSessionLog
    def violations(self) -> ReportData:
        """Return the rules broken on every fidelity of the ticket's stage left with violations, across its practices, each rule naming its fidelity, in the shape of ticket.report. path is the folder the reports sit in. A saved graph holds its whole practice's hits, so a rule two fidelities share is listed once. has_saved_graph is false when a report has no saved graph, so its rules are missing."""
        column = self.column
        reports = [self.report(entry.slug) for entry in self.progress if entry.has_violations and entry.stage is column]
        rules = {self._rule_identity(rule): rule for report in reversed(reports) for rule in report["rules"]}
        return {
            "path": self._from_repository(self._folder / REPORT_FOLDER),
            "text": "",
            "rules": list(reversed(rules.values())),
            "has_saved_graph": all(report["has_saved_graph"] for report in reports),
        }

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

    def to_json(self) -> TicketData:
        progress = self.progress
        upcoming = self.next_fidelity
        return {
            **super().to_json(),
            "name": self.name,
            "scope": self.scope,
            "parent": self._session.parent,
            "column": self.column.name,
            "is_done": self.is_done,
            "next": upcoming.slug if upcoming else None,
            "next_action": self.next_action,
            "handoff": self.latest_handoff,
            "reports": self.reports,
            "violation_counts": self.violation_counts,
            "practices": self.practices,
            "workpath": self.workpath,
            "worktree": self.worktree,
            "practice_roots": self.practice_roots,
            "session_file": self.session_file,
            "progress": {entry.slug: entry.state for entry in progress},
            "actions": {entry.slug: entry.action_states for entry in progress},
            "allowed_actions": {entry.slug: self._allowed_actions(entry) for entry in progress},
        }

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
        if not own or not Judgment.from_report(self._latest_with_result(own).read_text(encoding="utf-8", errors="replace")):
            return progress
        return progress.with_violations()

    def _latest_with_result(self, reports: list[Path]) -> Path:
        with_result = [report for report in reports if report.with_suffix(".json").is_file() or JUDGMENT_SECTION.search(report.read_text(encoding="utf-8"))]
        return (with_result or reports)[-1]

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
        """path as written from the repository's top, empty for the top itself, or as it is when it lies outside the
        repository."""
        given = Path(path)
        root = self._board.repo.root
        if not given.is_relative_to(root):
            return given.as_posix()
        relative = given.relative_to(root).as_posix()
        return "" if relative == "." else relative

    @property
    def _is_on_its_branch(self) -> bool:
        """Whether the repository has this ticket's branch checked out; a commit lands on whatever is checked out."""
        repo = self._board.repo
        return repo.has_branch(self.name) and repo.current_branch == self.name

    def _graph_of(self, report: str) -> Path:
        """The graph a validation saved beside its report."""
        return (self._board.repo.root / report).with_suffix(".json")

    def _hits_by_rule(self, report: str, progress: FidelityProgress) -> dict[str, list[dict]]:
        """The hits on the rules report answers for: a saved graph holds its whole practice's hits. A rule no fidelity describes belongs to none, so every report keeps it."""
        from validate.graph_json_reader import violations_by_rule, violations_from_graph_json_files

        answered = self._rules_answered_by(report, progress)
        described = progress.rule_descriptions
        scanned = self._scanned_rules(report, progress.practice)
        hits = violations_by_rule(violations_from_graph_json_files([self._graph_of(report)], [progress.practice]))
        return {name: rule_hits for name, rule_hits in hits.items() if name in scanned and (name in answered or name not in described)}

    def _scanned_rules(self, report: str, practice: str) -> set[str]:
        """The rules a scanner checks now; a saved graph keeps the hits of a scanner deleted since it was saved."""
        from harness.graph.practice_rules_registry import checks_for_practice
        from harness.graph.schema_rules import active_overlay_patterns

        overlays = json.loads(self._graph_of(report).read_text(encoding="utf-8")).get("overlays", [])
        return set(checks_for_practice(practice, active_overlay_patterns(tuple(overlays))))

    def _rules_answered_by(self, report: str, progress: FidelityProgress) -> set[str]:
        """The shared rules, the fidelity's own, and each earlier fidelity's that has no report newer than report."""
        reports = self.reports
        superseded = [earlier for earlier in progress.earlier_fidelities if _report_stamp(reports.get(progress.slug_of(earlier), "")) > _report_stamp(report)]
        return progress.rule_slugs_without(superseded)

    def _rules_broken_in(self, report: str, progress: FidelityProgress) -> list[ReportRuleData]:
        return [
            self._report_rule(progress, name, [self._violation_of(hit) for hit in hits])
            for name, hits in self._hits_by_rule(report, progress).items()
        ]

    def _judged_rules(self, text: str, progress: FidelityProgress) -> list[ReportRuleData]:
        """Each rule the judgment in a report fails, once however many judged files fail it, with its findings at the
        judged files' lines."""
        findings: dict[str, list[ViolationData]] = {}
        for judgment in Judgment.from_report(text):
            findings.setdefault(judgment.rule, []).extend(self._judged_violation(judgment.file, finding) for finding in judgment.findings)
        return [self._report_rule(progress, rule, violations) for rule, violations in findings.items()]

    def _report_rule(self, progress: FidelityProgress, name: str, violations: list[ViolationData]) -> ReportRuleData:
        """One broken rule of a report, in the one shape the board reads for graph hits and judged findings alike."""
        return {"fidelity": progress.slug, "name": name, "description": progress.rule_descriptions.get(name, ""), "count": len(violations), "violations": violations}

    def _judged_violation(self, judged_file: str, finding: ViolationData) -> ViolationData:
        """A finding names the judged file by its name alone, or no file; one that names another file keeps that file's path."""
        named = finding["location"]
        location = judged_file if not named or Path(named).name == Path(judged_file).name else named
        return {**finding, "location": location, "source": self._source_around(location, finding["line"])}

    def _rule_identity(self, rule: ReportRuleData) -> tuple:
        practice = rule["fidelity"].split("-")[0]
        return (practice, rule["name"], *((violation["location"], violation["line"], violation["message"]) for violation in rule["violations"]))

    def _violation_of(self, hit: dict) -> ViolationData:
        location = self._from_repository(self._workpath / hit["location"])
        line = hit["line_number"]
        return {"location": location, "line": line, "message": hit["violation_message"], "source": self._source_around(location, line)}

    def _source_around(self, location: str, line: int | None) -> list[SourceLineData]:
        """The numbered lines around line; none when the violation names no line or the file is not in this repository."""
        target = self._inside_repository(location)
        if target is None or line is None or not target.is_file():
            return []
        # Split on newlines alone: a graph counts lines that way, and splitlines() also breaks on form feeds.
        lines = target.read_text(encoding="utf-8", errors="replace").split("\n")
        first = max(line - SOURCE_LINES_BEFORE, 1)
        return [{"number": number, "text": text.rstrip("\r")} for number, text in enumerate(lines[first - 1:line + SOURCE_LINES_AFTER], first)]

    def _inside_repository(self, path: str) -> Path | None:
        """path within the repository; none when it lies outside it."""
        root = self._board.repo.root
        target = (root / path).resolve()
        return target if root in target.parents else None

    def _files_of(self, fidelity: FidelityGuidance) -> dict[str, list[FileEntryData]]:
        outputs = self._session.fidelity_outputs(fidelity.practice_guidance, fidelity)
        return {label: [entry for path in paths for entry in self._file_entries(path)] for label, paths in outputs.items()}

    def _render_command(self, progress: FidelityProgress, formats: list[str]) -> str:
        """The command that renders the fidelity before progress's into formats it has no file in, when it has work to render."""
        earlier = next((entry for entry in self.progress if entry.practice == progress.practice and entry.stage.next_stage is progress.stage), None)
        if earlier is None:
            return ""
        made = {label for label, entries in self._files_of(earlier.fidelity).items() if any(entry["exists"] for entry in entries)}
        wanted = [label for label in formats if label in earlier.fidelity.outputs and label not in made]
        if not made or not wanted:
            return ""
        return f"/actions-render {earlier.slug.replace('_', '-')} format={','.join(wanted)} source={sorted(made)[0]}"

    def _file_entries(self, declared: str) -> list[FileEntryData]:
        """A declared path, or each file of this ticket's that a pattern finds; a pattern that finds none stays as
        written, not yet there."""
        relative = self._from_repository(declared)
        pattern = _named_parts_as_wildcards(relative)
        if "*" not in pattern:
            return [{"path": relative, "exists": (self._board.repo.root / relative).exists()}]
        found = self._worked_on(_files_matching_from(self._board.repo.root, pattern))
        return [{"path": self._from_repository(path), "exists": True} for path in found] or [{"path": relative, "exists": False}]

    def _worked_on(self, found: list[Path]) -> list[Path]:
        """The files of a pattern that are this ticket's. A folder of its own holds only its work; on the whole repository, only what its branch changed is."""
        if not found or self._workpath != self._board.repo.root:
            return found
        return [path for path in found if path.resolve() in self._changed_on_branch]

    @cached_property
    def _changed_on_branch(self) -> set[Path]:
        root = self._board.repo.root
        return {(root / path).resolve() for path in self._board.repo.files_changed_on(self.name)}


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
    def action_states(self) -> dict[str, str]:
        """Each action as to_do, in_progress, or done. A validate that left violations is in progress until they are fixed."""
        states = {action: "done" if action in self._done_actions else "to_do" for action in self._stage.actions}
        if self._has_violations:
            states[VALIDATE] = "in_progress"
        return states


def _report_stamp(report: str) -> str:
    """The date a report's name ends with; names stamp it in a form that sorts by time. Nothing for no report."""
    return Path(report).stem.rsplit("-", 1)[-1] if report else ""


# The judgment the validating agent adds to a report, in the shape validate.md gives it.
JUDGMENT_HEADING = re.compile(r"^## Judgment — `(?P<file>[^`]+)`")
# A judgment the agent wrote, as against the example the report quotes indented in its instructions.
JUDGMENT_SECTION = re.compile(r"^#{1,2} Judgment\b", re.M)
JUDGED_RULE_HEADING = re.compile(r"^### `(?P<rule>[^`]+)` — Fail\s*$")
FINDING_LINE = re.compile(r"^- (?:(?P<file>[^\s:]+):(?P<line>\d+)\s+)?(?P<message>.+)$")


class Judgment:
    """One rule the judgment in a validation report fails, in one judged file, with its findings."""

    def __init__(self, file: str, rule: str) -> None:
        self._file = file
        self._rule = rule
        self._findings: list[ViolationData] = []

    @classmethod
    def from_report(cls, text: str) -> list[Judgment]:
        """The rules a report's judgment fails; none when the report has no judgment."""
        judgments: list[Judgment] = []
        judged_file, current = "", None
        for line in text.splitlines():
            heading = JUDGMENT_HEADING.match(line)
            rule = JUDGED_RULE_HEADING.match(line)
            if heading:
                judged_file, current = heading["file"], None
            elif rule and judged_file:
                current = cls(judged_file, rule["rule"])
                judgments.append(current)
            elif line.startswith("#"):
                current = None
            elif current and line.strip() and not current._add_finding_from(line.strip()):
                current = None
        return judgments

    @property
    def file(self) -> str:
        return self._file

    @property
    def rule(self) -> str:
        return self._rule

    @property
    def findings(self) -> list[ViolationData]:
        """Each finding at the file and line it names, when it names them; its source is read by whoever shows it."""
        return list(self._findings)

    def _add_finding_from(self, line: str) -> bool:
        """A bullet is a finding, and a paragraph under a rule with no bullets is its one finding. A paragraph after the
        findings ends the rule, so a Passes list the agent adds after its judgment is not read as findings."""
        bullet = FINDING_LINE.match(line)
        if bullet is None and self._findings:
            return False
        located = bullet if bullet and bullet["line"] else None
        self._findings.append({
            "location": located["file"] if located else "",
            "line": int(located["line"]) if located else None,
            "message": bullet["message"] if bullet else line,
            "source": [],
        })
        return True


SKIPPED_FOLDERS = frozenset({"node_modules"})
# Hidden folders hold tools and caches, but a module's .context folder holds its models and maps.
SEARCHED_HIDDEN_FOLDERS = frozenset({".context"})


def _files_matching_from(root: Path, pattern: str) -> list[Path]:
    """The files a pattern names, from the repository's top. A session can work outside the repository, so a pattern
    that stayed absolute searches from its drive."""
    anchor = Path(pattern).anchor
    return _files_matching(Path(anchor or root), pattern[len(anchor):])


def _files_matching(start: Path, pattern: str) -> list[Path]:
    """The files under start that pattern names. Installed packages and hidden folders hold no fidelity's work, and
    searching node_modules alone made a pattern take over a second."""
    parts = pattern.split("/")
    fixed = next((index for index, part in enumerate(parts) if set(part) & set("*?")), len(parts))
    # The search starts at the deepest folder the pattern names outright, so a pattern under one folder never walks the drive.
    base = start.joinpath(*parts[:fixed])
    matching = _pattern_matcher("/".join(parts[fixed:]))
    base_text = str(base)
    found = []
    for folder, folders, files in os.walk(base_text):
        folders[:] = [name for name in folders if name not in SKIPPED_FOLDERS and (not name.startswith(".") or name in SEARCHED_HIDDEN_FOLDERS)]
        # Plain strings here: building a Path for every file in the repository made the search take a second.
        inside = folder[len(base_text):].strip("\\/").replace("\\", "/")
        found += [Path(folder, name) for name in files if matching.fullmatch(f"{inside}/{name}" if inside else name)]
    return sorted(found)


NAMED_PART = re.compile(r"\{[^{}/]+\}")


def _named_parts_as_wildcards(path: str) -> str:
    """A declared path with its named parts, such as `{module}/{module}-model.md`, as a pattern. A named folder can be
    a module several folders deep, so it matches folders at any depth; a named part of a file name matches within it."""
    folders = re.sub(r"\{[^{}/]+\}/", "**/", path)
    return NAMED_PART.sub("*", folders)


def _pattern_matcher(pattern: str) -> re.Pattern[str]:
    """A glob pattern as a regular expression over a path written with `/`: `**/` is any number of folders, `*` and `?`
    stay inside one folder, the way Path.glob reads them."""
    parts = re.split(r"(\*\*/|\*\*|\*|\?)", pattern)
    wildcards = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
    return re.compile("".join(wildcards.get(part, re.escape(part)) for part in parts))


def _words_without_commas(line: str) -> list[str]:
    """A log line's words, without the commas that join the paths an action names."""
    return [word.rstrip(",") for word in line.split()]


def _verb_and_stage(line: str) -> tuple[str, str]:
    """A log line's verb and the word after it, which names the stage on a move or a mark."""
    words = line.split()
    verb = words[VERB_WORD] if len(words) > VERB_WORD else ""
    return verb, words[STAGE_WORD] if len(words) > STAGE_WORD else ""
