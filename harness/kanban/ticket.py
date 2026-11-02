"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

import inspect
from datetime import datetime, timezone
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.agent_tools import agent_toolset
from harness.agent_tools.agent_tools import agent_tool, noSessionLog, tool_subject
from harness.kanban.board import Board, Card, Stage, name_of
from harness.mcp.mcp_server import mcp
from space.session import Session

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
SOURCE_LINES_BEFORE = 2
SOURCE_LINES_AFTER = 4


class TicketNotFoundError(LookupError):
    """Raised when a tool names a ticket the board does not show."""

    def __init__(self, ticket: str) -> None:
        super().__init__(f"no ticket named {ticket!r} on the board")


class TicketFileError(ValueError):
    """Raised when a tool asks for a file outside the ticket's repository."""

    def __init__(self, path: str) -> None:
        super().__init__(f"{path!r} is not a file in this repository")


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
            FidelityProgress.from_log(fidelity, stage, lines)
            for stage in self._stages
            for fidelity in stage.work_required
        ]

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
        """The first fidelity in its current stage that is not done; none when it is done or Complete."""
        column = self.column
        if self.is_done:
            return None
        return next((progress for progress in self._enabled_progress if progress.stage is column and not progress.is_done), None)

    @property
    def next_action(self) -> str:
        """What Run next does: generate, validate, or review on the next fidelity, or satisfy while it has violations."""
        upcoming = self.next
        if upcoming is None:
            return ""
        return "satisfy" if upcoming.has_violations else upcoming.remaining_actions[0].__name__.lower()

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
        """The latest validation report of each fidelity that has one, as paths from the project; report names sort by their date."""
        found = {progress.slug: sorted((self._folder / REPORT_FOLDER).glob(progress.report_files)) for progress in self.progress}
        return {slug: self._from_project(files[-1]) for slug, files in found.items() if files}

    @property
    def violation_counts(self) -> dict[str, int]:
        """How many violations the latest report names, for each fidelity left with violations; a report with no saved graph has none to count."""
        reports = self.reports
        graphs = {entry: self._graph_of(reports[entry.slug]) for entry in self.progress if entry.has_violations and entry.slug in reports}
        return {entry.slug: sum(map(len, self._hits_by_rule(graph, entry).values())) for entry, graph in graphs.items() if graph.is_file()}

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
    def workspace(self) -> dict[str, bool]:
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
    def enable_practice(self, practice: str, is_enabled: bool) -> Ticket:
        """Turn practice on or off for ticket, saved in its session.json."""
        self._session.practices[practice].enabled = is_enabled
        return self

    @mcp
    @agent_tool
    @noSessionLog
    def files(self, fidelities: list[str]) -> dict[str, dict[str, list[dict[str, Any]]]]:
        """List the files fidelities declare by format, each with its path from the project and whether it exists. A pattern lists the files this ticket worked on, not every match in the repository."""
        return {progress.slug: self._files_of(progress.fidelity) for progress in self.progress if progress.slug in fidelities}

    @mcp
    @agent_tool
    @noSessionLog
    def read_file(self, path: str) -> dict[str, str]:
        """Return the text of path, a file in this repository."""
        target = self._repository_file(path)
        if target is None:
            raise TicketFileError(path)
        return {"path": path, "text": target.read_text(encoding="utf-8", errors="replace")}

    @mcp
    @agent_tool
    @noSessionLog
    def report(self, fidelity: str) -> dict[str, Any]:
        """Return the latest validation report of fidelity, a slug such as stories-story_map: its path and text, and the rules broken on the nodes of the graph saved beside it, each with its description and each violation with its line and the source around it. has_saved_graph is false when the report has no saved graph, so no rules can be listed."""
        path = self.reports.get(fidelity, "")
        if not path:
            return {"path": "", "text": "", "rules": [], "has_saved_graph": False}
        graph = self._graph_of(path)
        return {
            "path": path,
            "text": (self._board.repo_root / path).read_text(encoding="utf-8", errors="replace"),
            "rules": self._rules_broken_in(graph, fidelity) if graph.is_file() else [],
            "has_saved_graph": graph.is_file(),
        }

    @mcp
    @agent_tool
    @noSessionLog
    def violations(self) -> dict[str, Any]:
        """Return the rules broken on every fidelity left with violations, each rule naming its fidelity, in the shape of ticket.report. path is the folder the reports sit in. A saved graph holds its whole practice's hits, so a rule two fidelities share is listed once. has_saved_graph is false when a report has no saved graph, so its rules are missing."""
        reports = [self.report(entry.slug) for entry in self.progress if entry.has_violations]
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
        return [*filter(None, renders), f"/actions-generate {named} format={','.join(formats)}"]

    def to_json(self) -> dict[str, Any]:
        progress = self.progress
        upcoming = self.next
        return {
            **super().to_json(),
            "name": self.name,
            "scope": self.scope,
            "parent": self._fields.get("parent", ""),
            "column": self.column.name,
            "is_done": self.is_done,
            "can_move_next": self.column.name != "Complete",
            "next": upcoming.slug if upcoming else None,
            "next_action": self.next_action,
            "handoff": self.latest_handoff,
            "reports": self.reports,
            "violation_counts": self.violation_counts,
            "practices": self.practices,
            "progress": {entry.slug: entry.state for entry in progress},
            "actions": {entry.slug: entry.action_states for entry in progress},
            "allowed_actions": {entry.slug: entry.allowed_actions for entry in progress},
        }

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

    def _graph_of(self, report: str) -> Path:
        """The graph a validation saved beside its report."""
        return (self._board.repo_root / report).with_suffix(".json")

    def _hits_by_rule(self, graph: Path, progress: FidelityProgress) -> dict[str, list[dict[str, Any]]]:
        from validate.graph_json_reader import violations_by_rule, violations_from_graph_json_files

        return violations_by_rule(violations_from_graph_json_files([graph], [progress.practice]))

    def _rules_broken_in(self, graph: Path, fidelity: str) -> list[dict[str, Any]]:
        progress = next(entry for entry in self.progress if entry.slug == fidelity)
        descriptions = progress.rule_descriptions
        return [
            {"fidelity": fidelity, "name": name, "description": descriptions.get(name, ""), "count": len(hits), "violations": [self._violation_of(hit) for hit in hits]}
            for name, hits in self._hits_by_rule(graph, progress).items()
        ]

    def _rule_identity(self, rule: dict[str, Any]) -> tuple[Any, ...]:
        practice = rule["fidelity"].split("-")[0]
        return (practice, rule["name"], *((violation["location"], violation["line"], violation["message"]) for violation in rule["violations"]))

    def _violation_of(self, hit: dict[str, Any]) -> dict[str, Any]:
        location = self._relative_to(self._board.repo_root.resolve(), hit["location"])
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
        wanted = [label for label in formats if label in earlier.fidelity.output_files and label not in made]
        if not made or not wanted:
            return ""
        return f"/actions-render {earlier.slug.replace('_', '-')} format={','.join(wanted)} source={sorted(made)[0]}"

    def _file_entries(self, declared: str) -> list[dict[str, Any]]:
        """A declared path, or each file a pattern finds; a pattern that finds none stays as written, not yet there."""
        root = self._board.repo_root.resolve()
        relative = self._relative_to(root, declared)
        if "*" not in relative:
            return [{"path": relative, "exists": (root / relative).exists()}]
        # A session can work outside the repository, and glob takes no absolute pattern, so a path that stayed absolute searches from its drive.
        start = Path(Path(relative).anchor or root)
        found = sorted(path for path in start.glob(relative[len(Path(relative).anchor):]) if path.is_file())
        return [{"path": self._relative_to(root, str(path)), "exists": True} for path in self._worked_on(found)] or [{"path": relative, "exists": False}]

    def _worked_on(self, found: list[Path]) -> list[Path]:
        """The files of a pattern that are this ticket's. A folder of its own holds only its work; on the whole repository, only what its branch changed is."""
        repo_root = self._board.repo_root.resolve()
        if Path(self._session.workpath or repo_root).resolve() != repo_root:
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

    def __init__(self, fidelity: FidelityGuidance, stage: Stage, done_actions: list[type], has_violations: bool) -> None:
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
        done = [action for action in stage.actions if action.__name__.lower() in done_verbs]
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
    def done_actions(self) -> list[type]:
        return list(self._done_actions)

    @property
    def remaining_actions(self) -> list[type]:
        return [action for action in self._stage.actions if action not in self._done_actions]

    @property
    def has_violations(self) -> bool:
        return self._has_violations

    @property
    def is_done(self) -> bool:
        return not self.remaining_actions

    @property
    def slug(self) -> str:
        return f"{self.practice}-{self._fidelity.name}"

    @property
    def report_files(self) -> str:
        """The name pattern of this fidelity's dated validation reports."""
        return f"{self.slug.replace('_', '-')}-*.md"

    @property
    def rule_descriptions(self) -> dict[str, str]:
        """Each rule's text by slug. A saved graph holds the whole practice's hits, so every fidelity's rules count; this fidelity's own win."""
        practice = self._fidelity.practice_guidance
        entries = practice.fidelities.entries
        fidelities = entries.values() if isinstance(entries, dict) else entries
        rules = [*practice.rules, *(rule for fidelity in fidelities for rule in fidelity.rules), *self._fidelity.rules]
        return {rule.slug: rule.body.strip() for rule in rules}

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
        states = {action.__name__.lower(): "done" if action in self._done_actions else "to_do" for action in self._stage.actions}
        if self._has_violations:
            states["validate"] = "in_progress"
        return states

    @property
    def allowed_actions(self) -> list[str]:
        """What can run now: Validate once generated, and Review only after a clean Validate."""
        states = self.action_states
        allowed = ["generate"]
        if states["generate"] == "done":
            allowed.append("validate")
        if states["validate"] == "done":
            allowed.append("review")
        return allowed


def practice_key(practice: PracticeGuidance) -> str:
    """A practice's folder name (`clean_engineering`): how action lines in the session log name it."""
    return Path(inspect.getfile(type(practice))).parent.name


def _words(line: str) -> list[str]:
    return [word.rstrip(",") for word in line.split()]
