"""A ticket: one work session, placed on the board by reading its own session log."""

from __future__ import annotations

import inspect
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from harness.kanban.board import CLOSED_FOLDER, Stage

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.kanban.board import Board, Column

ARCHIVE_FOLDER = "_archive"
LOG_FILE = "session.log"
FIELDS_FILE = "session.json"
GRAPH_RULE_VIOLATION = "graph-rule"
PULL = "pull"
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class StageNotDone(Exception):
    """A pull refused because the ticket's stage is not done, or there is no stage after it."""

    def __init__(self, ticket: Ticket, stage: Column) -> None:
        super().__init__(f"{ticket.name} cannot be pulled out of {stage.name}: its stage is not done, or it has no next stage.")
        self.ticket = ticket
        self.stage = stage


class Ticket:
    """*Ticket* is one work session seen as a unit of delivery. It knows its column and progress by reading its
    own session log against the board's stages."""

    # never moves to the next stage by itself: someone pulls it, and the pull is written to its session log

    def __init__(self, session_folder: Path, board: Board) -> None:
        self._folder = Path(session_folder)
        self._board = board

    @property
    def name(self) -> str:
        return self._folder.name

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
        """Complete once closed; otherwise the stage of its latest pull, or the earliest stage it has work in."""
        if self._folder.parent.name == CLOSED_FOLDER:
            return self._board.column("Complete")
        pulled = self._pulled_into()
        if pulled is not None:
            return pulled
        worked = [progress.stage for progress in self.progress if progress.done_actions]
        return worked[0] if worked else self._stages[0]

    @property
    def is_done(self) -> bool:
        column = self.column
        if not isinstance(column, Stage):
            return False
        return all(progress.is_done for progress in self.progress if progress.stage is column)

    @property
    def next(self) -> FidelityProgress | None:
        """The first fidelity in its current stage that is not done; none when it is done or Complete."""
        column = self.column
        return next((progress for progress in self.progress if progress.stage is column and not progress.is_done), None)

    @property
    def last_activity(self) -> str:
        lines = self._log_lines()
        return lines[-1].split(" ", 1)[0] if lines else ""

    def pull(self) -> Stage:
        """Move a done ticket into the next stage by writing that stage to its session log."""
        column = self.column
        following = column.next_stage if isinstance(column, Stage) else None
        if not self.is_done or following is None:
            raise StageNotDone(self, column)
        self._append_log(f"{PULL} {following.name}")
        return following

    def close(self) -> Ticket:
        return self._move_to(self._board.sessions_folder / CLOSED_FOLDER)

    def archive(self) -> Ticket:
        return self._move_to(self._board.sessions_folder / ARCHIVE_FOLDER)

    def to_json(self) -> dict[str, Any]:
        upcoming = self.next
        return {
            "name": self.name,
            "title": self.title,
            "scope": self.scope,
            "parent": self._fields.get("parent", ""),
            "column": self.column.name,
            "is_done": self.is_done,
            "next": upcoming.slug if upcoming else None,
            "last_activity": self.last_activity,
            "progress": {progress.slug: progress.state for progress in self.progress},
        }

    @property
    def _stages(self) -> list[Stage]:
        return [column for column in self._board.columns if isinstance(column, Stage)]

    @property
    def _fields(self) -> dict[str, str]:
        path = self._folder / FIELDS_FILE
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    def _log_lines(self) -> list[str]:
        path = self._folder / LOG_FILE
        if not path.is_file():
            return []
        return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _pulled_into(self) -> Stage | None:
        pulls = [line.split()[2] for line in self._log_lines() if len(line.split()) > 2 and line.split()[1] == PULL]
        return next((stage for stage in self._stages if pulls and stage.name == pulls[-1]), None)

    def _append_log(self, entry: str) -> None:
        stamp = datetime.now(timezone.utc).strftime(TIMESTAMP_FORMAT)
        with (self._folder / LOG_FILE).open("a", encoding="utf-8") as log:
            log.write(f"{stamp} {entry}\n")

    def _move_to(self, parent: Path) -> Ticket:
        parent.mkdir(parents=True, exist_ok=True)
        destination = parent / self.name
        shutil.move(str(self._folder), str(destination))
        return Ticket(destination, self._board)


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
    def done_actions(self) -> list[type]:
        return list(self._done_actions)

    @property
    def remaining_actions(self) -> list[type]:
        return [action for action in self._stage.actions if action not in self._done_actions]

    @property
    def is_done(self) -> bool:
        return not self.remaining_actions

    @property
    def slug(self) -> str:
        return f"{practice_key(self._fidelity.practice_guidance)}-{self._fidelity.name}"

    @property
    def state(self) -> str:
        """done, violations, in_progress, or not_started: what the board pane colours."""
        if self.is_done:
            return "done"
        if self._has_violations:
            return "violations"
        return "in_progress" if self._done_actions else "not_started"


def practice_key(practice: PracticeGuidance) -> str:
    """A practice's folder name (`clean_engineering`): how action lines in the session log name it."""
    return Path(inspect.getfile(type(practice))).parent.name


def _words(line: str) -> list[str]:
    return [word.rstrip(",") for word in line.split()]
