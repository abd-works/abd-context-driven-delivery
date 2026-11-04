"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

import inspect
import json
import os
import re
from datetime import datetime, timezone
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.installation.destination import language_adapter
from harness.kanban.board import Board, Card, Stage
from harness.kanban.data import FileEntryData, FileTextData, PracticeRootData, ReportData, TicketData, WorkspaceData
from harness.mcp.mcp_server import mcp
from space.session import Session, name_of

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.kanban.backlog_item import BacklogItem
    from harness.kanban.board import Column

LOG_FILE = "session.log"
HANDOFF_FILES = "handoff-*.md"
REPORT_FOLDER = "validation-reports"
GRAPH_RULE_VIOLATION = "graph-rule"
MOVED_INTO = "move"
OLDER_MOVED_INTO = "pull"
MARKED_DONE = "done"
MARKED_IN_PROGRESS = "in-progress"
LEAVE_COMMIT = "commit"
LEAVE_PUSH = "push"
LEAVE_MERGE = "merge"
# Logs written before moves were named `move` say `pull`; both still place a ticket.
MOVE_WORDS = (MOVED_INTO, OLDER_MOVED_INTO)
OPEN_BRANCH = "branch"
OPEN_WORKTREE = "worktree"
BACKLOG_COLUMN = "Backlog"
ALWAYS_ALLOWED = ("generate",)
ONCE_THERE_IS_OUTPUT = ("validate", "review")
SOURCE_LINES_BEFORE = 2
SOURCE_LINES_AFTER = 4


class TicketNotFoundError(LookupError):
    """Raised when a tool names a ticket the board does not show."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"no ticket named {ticket!r} on the board")


class FidelityNotFoundError(LookupError):
    """Raised when a tool names a fidelity, such as stories-story_map, that the ticket's practices do not have."""

    def __init__(self, fidelity: str) -> None:
        super().__init__(f"no fidelity named {fidelity!r} on this ticket")


class NotAStageError(ValueError):
    """Raised when a ticket is moved into a column that is not a stage, such as the Backlog or Complete."""

    def __init__(self, stage: str) -> None:
        super().__init__(f"{stage!r} is not a stage a ticket can be moved into")


class TicketFileError(ValueError):
    """Raised when a tool asks for a file outside the ticket's repository."""

    def __init__(self, path: str) -> None:
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
    def new(cls, title: str, scope: str = "feature", parent: str = "", path: str = "") -> Ticket:
        """Open a new ticket titled title in Discovery. scope is feature, story, or slice; parent names the ticket it was split from; path is the folder in the repository its session works on."""
        board = Board.current()
        name = name_of(title)
        workpath = (board.repo_root / path).resolve() if path else board.repo_root
        fields = {"title": title, "scope": scope, "parent": parent}
        Session.new(name, workpath, board.repo_root, fields, is_current=False)
        return board.ticket(name)

    @property
    def session(self) -> Session:
        return self._session

    @property
    def name(self) -> str:
        return self._session.name

    @property
    def title(self) -> str:
        return self._fields.get("title") or self.name

    @property
    def scope(self) -> str:
        return self._fields.get("scope", "")

    @property
    def lineage(self) -> Ticket | None:
        parent = self._fields.get("parent", "")
        return self._board.ticket(parent) if parent else None

    @property
    def practices(self) -> dict[str, bool]:
        """Which practices this ticket works on: every practice until a person turns it off."""
        active = {practice.name for practice in self._session.active_practices}
        return {key: key in active for key in map(practice_key, self._board.practices)}

    @property
    def progress(self) -> list[FidelityProgress]:
        """One per fidelity the board requires, in stage order; read from the session log each time."""
        lines = self._log_lines()
        return [
            self._judged(FidelityProgress.from_log(fidelity, stage, lines))
            for stage in self._stages
            for fidelity in stage.work_required
        ]

    def _judged(self, progress: FidelityProgress) -> FidelityProgress:
        """A validate the log shows passing still failed when the judgment the validating agent added to its report fails a rule."""
        if "validate" not in progress.done_actions:
            return progress
        reports = sorted((self._folder / REPORT_FOLDER).glob(progress.report_files))
        if not reports or not _judgments_in(reports[-1].read_text(encoding="utf-8", errors="replace")):
            return progress
        return progress.with_violations()

    @property
    def column(self) -> Column:
        """Complete once closed; otherwise the stage of its latest move, or the earliest stage it has work in."""
        if self._session.is_closed:
            return self._board.column("Complete")
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
    def next(self) -> FidelityProgress | None:
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
        upcoming = self.next
        if upcoming is None:
            return ""
        return "satisfy" if upcoming.has_violations else upcoming.remaining_actions[0]

    @property
    def last_activity(self) -> str:
        lines = self._log_lines()
        return lines[-1].split(" ", 1)[0] if lines else ""

    @property
    def latest_handoff(self) -> str:
        """The newest handoff file, as a path from the project; handoff names sort by their timestamp."""
        handoffs = sorted(self._folder.glob(HANDOFF_FILES))
        return self._from_project(handoffs[-1]) if handoffs else ""

    @property
    def reports(self) -> dict[str, str]:
        """The latest validation report of each fidelity that has one, as paths from the project; report names sort by their date.
        Validate saves a report before the agent judges it, so a report with no judgment and no saved graph yet does not
        hide an earlier one that has its result."""
        found = {progress.slug: sorted((self._folder / REPORT_FOLDER).glob(progress.report_files)) for progress in self.progress}
        return {slug: self._from_project(self._latest_with_result(files)) for slug, files in found.items() if files}

    def _latest_with_result(self, reports: list[Path]) -> Path:
        with_result = [report for report in reports if report.with_suffix(".json").is_file() or JUDGMENT_SECTION.search(report.read_text(encoding="utf-8"))]
        return (with_result or reports)[-1]

    @property
    def violation_counts(self) -> dict[str, int]:
        """How many violations the latest report names, graph hits and judged findings, for each fidelity left with violations."""
        counts = {entry.slug: sum(rule["count"] for rule in self.report(entry.slug)["rules"]) for entry in self.progress if entry.has_violations}
        return {slug: count for slug, count in counts.items() if count}

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
            return self._to_backlog()
        return self._enter(earlier)._mark(MARKED_DONE, earlier)

    @mcp
    @agent_tool
    @noSessionLog
    def move_to(self, stage: str, done: bool = False) -> Ticket | BacklogItem:
        """Move ticket straight into stage's In progress, or its Done when done is true, whatever its work; dragging a card does this. Out of Complete it reopens first. Into the Backlog, from any column, it becomes a backlog item that keeps its whole folder."""
        if stage == BACKLOG_COLUMN:
            return self._to_backlog()
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
        """Close ticket: its session ends, its folder moves to closed/, and it shows in Complete. leaving names what to do with its work first: commit, push, merge."""
        self._leave(leaving or [])
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
            active._leave(leaving or [])
        wanted = opening or []
        if OPEN_BRANCH in wanted:
            self._board.repo.switch_branch(self.name)
        if OPEN_WORKTREE in wanted:
            self._board.repo.switch_worktree(self.name)
        Session.switch(self.name, repo_path=self._board.repo_root)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def workspace(self) -> WorkspaceData:
        """Say whether ticket already has its branch and its worktree, so activating it offers only what is missing, and whether the active ticket being left is on a branch of its own, so its work can be committed, pushed, and merged."""
        repo = self._board.repo
        active = self._board.active
        return {
            "has_branch": repo.has_branch(self.name),
            "has_worktree": repo.worktree_for(self.name) is not None,
            "leaving_has_branch": active is not None and active._is_on_its_branch,
        }

    @mcp
    @agent_tool
    @noSessionLog
    def finish_review(self, fidelities: list[str]) -> Ticket:
        """Record that a person has reviewed and approved fidelities, slugs such as stories-story_map, on ticket: one review line each in its session log. A review counts once its fidelity's latest Validate has passed, and a fidelity whose actions are all done is done in its stage."""
        by_slug = {entry.slug: entry for entry in self.progress}
        unknown = [slug for slug in fidelities if slug not in by_slug]
        if unknown:
            raise FidelityNotFoundError(unknown[0])
        for slug in fidelities:
            fidelity = by_slug[slug].fidelity
            self.record(f"review {type(fidelity.practice_guidance).__name__} {fidelity.name}")
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def choose_root(self, path: str) -> Ticket:
        """Make path, a folder in the repository, ticket's root: the folder its session works in and its graph loads from. An empty path is the whole repository."""
        self._session.change_workpath(self._board.repo_root / path)
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def choose_practice_root(self, practice: str, path: str) -> Ticket:
        """Write practice's files under path, a folder in the repository, for this ticket."""
        self._session.choose_output_root(practice, self._board.repo_root / path)
        return self

    @property
    def root(self) -> str:
        """The folder the session works in, as a path from the project; empty for the whole repository."""
        return self._from_repository(Path(self._session.workpath or self._board.repo_root))

    @mcp
    @agent_tool
    @noSessionLog
    def use_default_practice_root(self, practice: str) -> Ticket:
        """Write practice's files under its default root again: the ticket's root plus the practice's own folder."""
        self._session.forget_output_root(practice)
        return self

    @property
    def practice_roots(self) -> dict[str, PracticeRootData]:
        """Where each practice writes, as a path from the project, and whether a person chose it or it is the default."""
        guidances = {entry.practice: entry.fidelity.practice_guidance for entry in self.progress}
        return {
            practice: {"root": self._from_repository(self._session.practice_root(guidance, practice)), "is_chosen": self._session.has_chosen_output_root(practice)}
            for practice, guidance in guidances.items()
        }

    def _from_repository(self, folder: Path) -> str:
        relative = self._relative_to(self._board.repo_root.resolve(), str(folder.resolve()))
        return "" if relative == "." else relative

    @mcp
    @agent_tool
    @noSessionLog
    def enable_practice(self, practice: str, is_enabled: bool) -> Ticket:
        """Turn practice on or off for ticket, saved in its session.json."""
        self._session.practices[practice].enabled = is_enabled
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
        return [{"path": self._from_project(path), "exists": True} for path in files]

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str) -> FileTextData:
        """Return the text of path, a file in this repository."""
        target = self._repository_file(path)
        if target is None:
            raise TicketFileError(path)
        return {"path": path, "text": target.read_text(encoding="utf-8", errors="replace")}

    @mcp
    @agent_tool
    @noSessionLog
    def report(self, fidelity: str) -> ReportData:
        """Return the latest validation report of fidelity, a slug such as stories-story_map: its path and text, and the rules broken in it, each with its description and each violation with its line and the source around it. The rules are those broken on the nodes of the graph saved beside the report, then each rule the validating agent's judgment fails that the graph did not hit. has_saved_graph is false when the report has no saved graph, so its graph's rules are missing."""
        path = self.reports.get(fidelity, "")
        if not path:
            return {"path": "", "text": "", "rules": [], "has_saved_graph": False}
        graph = self._graph_of(path)
        text = (self._board.repo_root / path).read_text(encoding="utf-8", errors="replace")
        graph_rules = self._rules_broken_in(path, fidelity) if graph.is_file() else []
        hit = {rule["name"] for rule in graph_rules}
        judged = [rule for rule in self._judged_rules(text, fidelity) if rule["name"] not in hit]
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
            "path": self._from_project(self._folder / REPORT_FOLDER),
            "text": "",
            "rules": list(reversed(rules.values())),
            "has_saved_graph": all(report["has_saved_graph"] for report in reports),
        }

    @mcp
    @agent_tool
    @noSessionLog
    def generate_commands(self, fidelities: list[str], formats: list[str]) -> list[str]:
        """Return the commands that generate fidelities in formats. A format the same practice's earlier fidelity has no file in is rendered from that fidelity first."""
        renders = [self._render_command(slug, formats) for slug in fidelities]
        named = " ".join(slug.replace("_", "-") for slug in fidelities)
        commands = [*filter(None, renders), f"/actions-generate {named} format={','.join(formats)}"]
        return [f"{command} session={self.session_file}" for command in commands]

    @property
    def session_file(self) -> str:
        """Its session.json as a path from the project. Every command the board sends names it, because a command runs
        in whichever chat it is sent to, and that chat's open session can be another."""
        return self._from_project(self._folder / "session.json")

    def to_json(self) -> TicketData:
        progress = self.progress
        upcoming = self.next
        return {
            **super().to_json(),
            "name": self.name,
            "scope": self.scope,
            "parent": self._fields.get("parent", ""),
            "column": self.column.name,
            "is_done": self.is_done,
            "next": upcoming.slug if upcoming else None,
            "next_action": self.next_action,
            "handoff": self.latest_handoff,
            "reports": self.reports,
            "violation_counts": self.violation_counts,
            "practices": self.practices,
            "root": self.root,
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
    def _stages(self) -> list[Stage]:
        return [column for column in self._board.columns if isinstance(column, Stage)]

    @property
    def _fields(self) -> dict[str, Any]:
        return self._session.fields

    @property
    def _enabled_progress(self) -> list[FidelityProgress]:
        practices = self.practices
        return [entry for entry in self.progress if practices[entry.practice]]

    def keep(self, file: Path) -> Path:
        """Move file into this ticket's session folder, where it stays with the ticket's work until it becomes lasting
        context, such as part of a story map. A started backlog item's text is the only copy of the idea."""
        kept = self._folder / file.name
        file.replace(kept)
        return kept

    def record(self, entry: str) -> None:
        """Append entry to the session log, timestamped."""
        with (self._folder / LOG_FILE).open("a", encoding="utf-8") as log:
            log.write(f"{self._timestamp(datetime.now(timezone.utc))} {entry}\n")

    def _log_lines(self) -> list[str]:
        path = self._folder / LOG_FILE
        if not path.is_file():
            return []
        return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _moved_into(self) -> Stage | None:
        moves = [line.split()[2] for line in self._log_lines() if len(line.split()) > 2 and line.split()[1] in MOVE_WORDS]
        return next((stage for stage in self._stages if moves and stage.name == moves[-1]), None)

    def _latest_mark(self, stage: Stage) -> str | None:
        """The latest mark a person made in stage since entering it; none when they have made none."""
        marks = None
        for line in self._log_lines():
            words = line.split()
            if len(words) > 2 and words[2] == stage.name and words[1] in (*MOVE_WORDS, MARKED_DONE, MARKED_IN_PROGRESS):
                marks = None if words[1] in MOVE_WORDS else words[1]
        return marks

    def _mark(self, mark: str, stage: Stage) -> Ticket:
        self.record(f"{mark} {stage.name}")
        return self

    def _enter(self, stage: Stage) -> Ticket:
        self.record(f"{MOVED_INTO} {stage.name}")
        return self

    def _from_project(self, path: Path) -> str:
        return path.relative_to(self._board.repo_root).as_posix()

    @property
    def _is_on_its_branch(self) -> bool:
        """Whether the repository has this ticket's branch checked out; a commit lands on whatever is checked out."""
        repo = self._board.repo
        return repo.has_branch(self.name) and repo.current_branch == self.name

    def _leave(self, leaving: list[str]) -> None:
        if not leaving or not self._is_on_its_branch:
            return
        repo = self._board.repo
        if LEAVE_COMMIT in leaving or LEAVE_PUSH in leaving:
            repo.push_commit(f"{self.name}: leave session", sync_remote=LEAVE_PUSH in leaving)
        if LEAVE_MERGE in leaving:
            repo.close_branch(self.name)

    def _reopen(self) -> Ticket:
        reopened = Ticket(self._session.reopen(), self._board)
        final = self._stages[-1]
        return reopened._enter(final)._mark(MARKED_DONE, final)

    def _to_backlog(self) -> BacklogItem:
        from harness.kanban.backlog_item import BacklogItem

        self._session.close()
        held = Ticket(self._session.move_to_backlog(), self._board)
        return BacklogItem.holding(held, self._board)

    @property
    def _graph_root(self) -> Path:
        """The folder a saved graph names its files from: the session's root, or the project's when it has none."""
        return Path(self._session.workpath or self._board.repo_root).resolve()

    def _graph_of(self, report: str) -> Path:
        """The graph a validation saved beside its report."""
        return (self._board.repo_root / report).with_suffix(".json")

    def _hits_by_rule(self, report: str, progress: FidelityProgress) -> dict[str, list[dict[str, Any]]]:
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

    def _rules_broken_in(self, report: str, fidelity: str) -> list[dict[str, Any]]:
        progress = next(entry for entry in self.progress if entry.slug == fidelity)
        descriptions = progress.rule_descriptions
        return [
            {"fidelity": fidelity, "name": name, "description": descriptions.get(name, ""), "count": len(hits), "violations": [self._violation_of(hit) for hit in hits]}
            for name, hits in self._hits_by_rule(report, progress).items()
        ]

    def _judged_rules(self, text: str, fidelity: str) -> list[dict[str, Any]]:
        """Each rule the judgment in a report fails, with its findings at the judged file's lines."""
        descriptions = next(entry for entry in self.progress if entry.slug == fidelity).rule_descriptions
        rules = []
        for judgment in _judgments_in(text):
            violations = [self._judged_violation(judgment.file, finding) for finding in judgment.findings]
            rules.append({"fidelity": fidelity, "name": judgment.rule, "description": descriptions.get(judgment.rule, ""), "count": len(violations), "violations": violations})
        return rules

    def _judged_violation(self, judged_file: str, finding: Finding) -> dict[str, Any]:
        """A finding names the judged file by its name alone, or no file; one that names another file keeps that file's path."""
        location = judged_file if not finding.file or Path(finding.file).name == Path(judged_file).name else finding.file
        return {"location": location, "line": finding.line, "message": finding.message, "source": self._source_around(location, finding.line)}

    def _rule_identity(self, rule: dict[str, Any]) -> tuple[Any, ...]:
        practice = rule["fidelity"].split("-")[0]
        return (practice, rule["name"], *((violation["location"], violation["line"], violation["message"]) for violation in rule["violations"]))

    def _violation_of(self, hit: dict[str, Any]) -> dict[str, Any]:
        location = self._relative_to(self._board.repo_root.resolve(), str(self._graph_root / hit["location"]))
        line = hit["line_number"]
        return {"location": location, "line": line, "message": hit["violation_message"], "source": self._source_around(location, line)}

    def _source_around(self, location: str, line: int | None) -> list[dict[str, Any]]:
        """The numbered lines around line; none when the violation names no line or the file is not in this repository."""
        target = self._repository_file(location)
        if target is None or line is None:
            return []
        # Split on newlines alone: a graph counts lines that way, and splitlines() also breaks on form feeds.
        lines = target.read_text(encoding="utf-8", errors="replace").split("\n")
        first = max(line - SOURCE_LINES_BEFORE, 1)
        return [{"number": number, "text": text.rstrip("\r")} for number, text in enumerate(lines[first - 1:line + SOURCE_LINES_AFTER], first)]

    def _repository_file(self, path: str) -> Path | None:
        root = self._board.repo_root.resolve()
        target = (root / path).resolve()
        return target if root in target.parents and target.is_file() else None

    def _files_of(self, fidelity: FidelityGuidance) -> dict[str, list[dict[str, Any]]]:
        practice = fidelity.practice_guidance
        previous = practice.fidelities.current
        practice.fidelities.current = fidelity
        try:
            outputs = self._session.fidelity_outputs(practice)
        finally:
            practice.fidelities.current = previous
        return {label: [entry for path in paths for entry in self._file_entries(path)] for label, paths in outputs.items()}

    def _render_command(self, slug: str, formats: list[str]) -> str:
        """The command that renders the fidelity before slug into formats it has no file in, when it has work to render."""
        fidelity = next(entry for entry in self.progress if entry.slug == slug)
        earlier = next((entry for entry in self.progress if entry.practice == fidelity.practice and entry.stage.next_stage is fidelity.stage), None)
        if earlier is None:
            return ""
        made = {label for label, entries in self._files_of(earlier.fidelity).items() if any(entry["exists"] for entry in entries)}
        wanted = [label for label in formats if label in earlier.fidelity.outputs and label not in made]
        if not made or not wanted:
            return ""
        return f"/actions-render {earlier.slug.replace('_', '-')} format={','.join(wanted)} source={sorted(made)[0]}"

    def _file_entries(self, declared: str) -> list[dict[str, Any]]:
        """A declared path, or each file a pattern finds; a pattern that finds none stays as written, not yet there."""
        root = self._board.repo_root.resolve()
        relative = self._relative_to(root, declared)
        pattern = _named_parts_as_wildcards(relative)
        if "*" not in pattern:
            return [{"path": relative, "exists": (root / relative).exists()}]
        # A session can work outside the repository, so a path that stayed absolute searches from its drive.
        start = Path(Path(pattern).anchor or root)
        found = _files_matching(start, pattern[len(Path(pattern).anchor):])
        return [{"path": self._relative_to(root, str(path)), "exists": True} for path in self._worked_on(found)] or [{"path": relative, "exists": False}]

    def _worked_on(self, found: list[Path]) -> list[Path]:
        """The files of a pattern that are this ticket's. A folder of its own holds only its work; on the whole repository, only what its branch changed is."""
        repo_root = self._board.repo_root.resolve()
        if not found or Path(self._session.workpath or repo_root).resolve() != repo_root:
            return found
        return [path for path in found if path.resolve() in self._changed_on_branch]

    @cached_property
    def _changed_on_branch(self) -> set[Path]:
        repo_root = self._board.repo_root.resolve()
        return {(repo_root / path).resolve() for path in self._board.repo.files_changed_on(self.name)}

    def _relative_to(self, root: Path, declared: str) -> str:
        path = Path(declared)
        return path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()


class FidelityProgress:
    """*FidelityProgress* is how far one fidelity has got through its stage's actions on one ticket."""

    # validate is done only when its latest line names no graph-rule violations; review is done only after that

    def __init__(self, fidelity: FidelityGuidance, stage: Stage, done_actions: list[str], has_violations: bool) -> None:
        self._fidelity = fidelity
        self._stage = stage
        self._done_actions = list(done_actions)
        self._has_violations = has_violations

    @classmethod
    def from_log(cls, fidelity: FidelityGuidance, stage: Stage, lines: list[str]) -> FidelityProgress:
        """Read the actions done on this fidelity from session log lines, finding it by name, never by position."""
        practice = fidelity.practice_guidance
        spellings = {practice_key(practice), type(practice).__name__}
        naming = [(index, words[1]) for index, words in enumerate(_words(line) for line in lines)
                  if len(words) > 1 and fidelity.name in words[2:] and spellings & set(words[2:])]
        validations = [index for index, verb in naming if verb == "validate"]
        latest_validation = validations[-1] if validations else None
        has_violations = latest_validation is not None and GRAPH_RULE_VIOLATION in lines[latest_validation]
        validated = latest_validation is not None and not has_violations
        reviewed = validated and any(verb == "review" and index > latest_validation for index, verb in naming)
        done_verbs = {verb for _, verb in naming if verb == "generate"}
        done_verbs |= {"validate"} if validated else set()
        done_verbs |= {"review"} if reviewed else set()
        done = [action for action in stage.actions if action in done_verbs]
        return cls(fidelity, stage, done, has_violations)

    @property
    def fidelity(self) -> FidelityGuidance:
        return self._fidelity

    @property
    def stage(self) -> Stage:
        return self._stage

    @property
    def practice(self) -> str:
        return practice_key(self._fidelity.practice_guidance)

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
        """This progress with its latest validate failed, so validate and review are to do again."""
        return FidelityProgress(self._fidelity, self._stage, [action for action in self._done_actions if action == "generate"], True)

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
    def report_files(self) -> str:
        """The name pattern of this fidelity's dated validation reports."""
        return f"{self.slug.replace('_', '-')}-*.md"

    @property
    def rule_descriptions(self) -> dict[str, str]:
        """Each rule's text by slug. A saved graph holds the whole practice's hits, so every fidelity's rules count; this fidelity's own win."""
        practice = self._fidelity.practice_guidance
        rules = [*practice.rules, *(rule for fidelity in self._practice_fidelities for rule in fidelity.rules), *self._fidelity.rules]
        return {rule.slug: rule.body.strip() for rule in rules}

    @property
    def _practice_fidelities(self) -> list[FidelityGuidance]:
        entries = self._fidelity.practice_guidance.fidelities.entries
        return list(entries.values() if isinstance(entries, dict) else entries)

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
            states["validate"] = "in_progress"
        return states


def _report_stamp(report: str) -> str:
    """The date a report's name ends with; names stamp it in a form that sorts by time. Nothing for no report."""
    return Path(report).stem.rsplit("-", 1)[-1] if report else ""


# The judgment the validating agent adds to a report, in the shape validate.md gives it. A report written before
# validate.md allowed only Pass and Fail can mark a rule Warn, which is a Fail.
JUDGMENT_HEADING = re.compile(r"^## Judgment — `(?P<file>[^`]+)`")
# A judgment the agent wrote, as against the example the report quotes indented in its instructions.
JUDGMENT_SECTION = re.compile(r"^#{1,2} Judgment", re.M)
JUDGED_RULE_HEADING = re.compile(r"^### `(?P<rule>[^`]+)` — (?:Fail|Warn)\s*$")
FINDING_LINE = re.compile(r"^- (?:(?P<file>[^\s:]+):(?P<line>\d+)\s+)?(?P<message>.+)$")
# A finding written before validate.md gave the judgment its shape names its file and line mid-sentence.
NAMED_LINE = re.compile(r"(?P<file>[\w./-]+\.\w+):(?P<line>\d+)")


class Finding:
    """One finding of a judged rule: the file and line it names, when it names them, and what it says."""

    def __init__(self, file: str, line: int | None, message: str) -> None:
        self.file = file
        self.line = line
        self.message = message


class Judgment:
    """One rule the judgment fails, in one judged file, with its findings."""

    def __init__(self, file: str, rule: str) -> None:
        self.file = file
        self.rule = rule
        self.findings: list[Finding] = []

    def add(self, line: str) -> None:
        """A bullet is a finding; a paragraph under a rule with no bullets is its one finding."""
        bullet = FINDING_LINE.match(line)
        if bullet is None and self.findings:
            return
        message = bullet["message"] if bullet else line
        named = (bullet if bullet and bullet["line"] else None) or NAMED_LINE.search(message)
        self.findings.append(Finding(named["file"] if named else "", int(named["line"]) if named else None, message))


def _judgments_in(text: str) -> list[Judgment]:
    """The rules a report's judgment fails; none when the report has no judgment."""
    judgments: list[Judgment] = []
    judged_file, current = "", None
    for line in text.splitlines():
        heading = JUDGMENT_HEADING.match(line)
        rule = JUDGED_RULE_HEADING.match(line)
        if heading:
            judged_file, current = heading["file"], None
        elif rule and judged_file:
            current = Judgment(judged_file, rule["rule"])
            judgments.append(current)
        elif line.startswith("#"):
            current = None
        elif current and line.strip():
            current.add(line.strip())
    return judgments


def practice_key(practice: PracticeGuidance) -> str:
    """A practice's folder name (`clean_engineering`): how action lines in the session log name it."""
    return Path(inspect.getfile(type(practice))).parent.name


SKIPPED_FOLDERS = frozenset({"node_modules"})
# Hidden folders hold tools and caches, but a module's .context folder holds its models and maps.
SEARCHED_HIDDEN_FOLDERS = frozenset({".context"})


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


def _words(line: str) -> list[str]:
    return [word.rstrip(",") for word in line.split()]
