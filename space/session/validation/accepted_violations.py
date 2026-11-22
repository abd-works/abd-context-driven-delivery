"""AcceptedViolations - the violations a person accepts as they are, kept in a project's
``.context/violations-accepted.json``, so a later validate, report, or count leaves the very same violation out."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from harness.graph.violation import UNKNOWN_LOCATION, Violation
from harness.installation.json_file import JsonFile, JsonFileUnreadable
from harness.process.log_timestamp import LogTimestamp

ACCEPTED_VIOLATIONS_FILE = "violations-accepted.json"
# The one key of the file: the list of acceptances.
ACCEPTED = "accepted"


class AcceptedViolationsUnreadable(JsonFileUnreadable):
    """A project's ``violations-accepted.json`` does not read as a list of acceptances. Nothing is written over it, and
    nothing is reported as if no violation were accepted, so a person repairs the file first."""

    def message(self, path: Path, cause: Exception) -> str:
        return (
            f"{path} does not read as the accepted violations ({cause}). It holds one JSON object whose "
            f'"{ACCEPTED}" is a list of acceptances, each an object with a rule. Repair it, or delete it to accept nothing.'
        )


class AcceptanceData(TypedDict, total=False):
    """One acceptance as the file keeps it. ``rule``, ``node_id``, and ``message`` are what a violation on a node is
    matched on; ``rule``, ``file``, and ``content`` (the judged line's text) what a finding that names no node is
    matched on, by its ``message`` when it names no line either. ``subject`` and ``accepted_at`` are for a person
    reading the file."""

    rule: str
    node_id: str
    subject: str
    file: str
    content: str
    message: str
    accepted_at: str


class Acceptance:
    """One violation accepted as it is. It covers the same rule on the same node with the same message; for a finding
    that names no node, the same rule in the same file on the same judged content, whatever line that content is on
    now and however the judge words the finding, or the same message when the finding names no line."""

    def __init__(self, kept: AcceptanceData) -> None:
        self._kept = kept

    @property
    def kept(self) -> AcceptanceData:
        """The acceptance as the file keeps it."""
        return dict(self._kept)

    def covers(self, found: Acceptance) -> bool:
        """Whether found, a violation read as an acceptance of itself, is the violation this one accepts."""
        mine, theirs = self._kept, found._kept
        if mine.get("rule") != theirs.get("rule"):
            return False
        if mine.get("node_id") or theirs.get("node_id"):
            return self._same(theirs, "node_id", "message")
        if mine.get("content") or theirs.get("content"):
            return self._same(theirs, "file", "content")
        return self._same(theirs, "file", "message")

    def _same(self, theirs: AcceptanceData, *fields: str) -> bool:
        return all(self._kept.get(field, "") == theirs.get(field, "") for field in fields)


class AcceptedViolations:
    """A project's ``.context/violations-accepted.json``: each violation a person accepted, kept with the rule and the
    id of the node it is on, in a file committed with the project, so an acceptance holds for everyone and in every
    session. It reads a judged line's content from folders, the folders a violation's file is named from. A missing
    file accepts nothing; one that does not read raises *AcceptedViolationsUnreadable* and is left as it is."""

    def __init__(self, file: Path, folders: list[Path]) -> None:
        self._file = JsonFile(file, AcceptedViolationsUnreadable)
        self._folders = list(folders)

    @property
    def file(self) -> Path:
        return self._file.path

    @property
    def holds_any(self) -> bool:
        return bool(self._acceptances())

    def accept(self, violation: Violation) -> None:
        """Keep violation as accepted, once however often it is accepted."""
        acceptances = self._acceptances()
        accepted = self._acceptance_of(violation)
        if any(acceptance.covers(accepted) for acceptance in acceptances):
            return
        stamped = Acceptance({**accepted.kept, "accepted_at": str(LogTimestamp.now())})
        self._write([*acceptances, stamped])

    def reopen(self, violation: Violation) -> None:
        """Take back the acceptance of violation, so it is reported again."""
        acceptances = self._acceptances()
        found = self._acceptance_of(violation)
        left = [acceptance for acceptance in acceptances if not acceptance.covers(found)]
        if len(left) != len(acceptances):
            self._write(left)

    def open_among(self, violations: list[Violation]) -> list[Violation]:
        """The violations of violations nobody accepted, in their order."""
        accepted = self.accepted_among(violations)
        return [violation for violation in violations if not any(violation is left_out for left_out in accepted)]

    def accepted_among(self, violations: list[Violation]) -> list[Violation]:
        """The violations of violations a person accepted, which a report leaves out and counts."""
        acceptances = self._acceptances()
        if not acceptances:
            return []
        return [violation for violation in violations if self._is_covered(violation, acceptances)]

    def _is_covered(self, violation: Violation, acceptances: list[Acceptance]) -> bool:
        found = self._acceptance_of(violation)
        return any(acceptance.covers(found) for acceptance in acceptances)

    def _acceptance_of(self, violation: Violation) -> Acceptance:
        """Violation as an acceptance of itself: on its node when it names one, else on the content of its line."""
        file = violation.location.replace("\\", "/")
        named: AcceptanceData = {"rule": violation.rule, "file": file, "message": violation.message}
        if violation.node_id:
            return Acceptance({**named, "node_id": violation.node_id, "subject": violation.subject})
        return Acceptance({**named, "content": self._judged_content(violation)})

    def _judged_content(self, violation: Violation) -> str:
        """The text of the line a finding names, without the space around it; nothing when it names no line or its
        file is in none of the folders."""
        if not violation.line or violation.location == UNKNOWN_LOCATION:
            return ""
        file = next((folder / violation.location for folder in self._folders if (folder / violation.location).is_file()), None)
        if file is None:
            return ""
        lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[violation.line - 1].strip() if violation.line <= len(lines) else ""

    def _acceptances(self) -> list[Acceptance]:
        listed = self._file.read().get(ACCEPTED, [])
        if not isinstance(listed, list) or not all(isinstance(entry, dict) and entry.get("rule") for entry in listed):
            raise AcceptedViolationsUnreadable(self.file, TypeError(f'"{ACCEPTED}" is not a list of acceptances'))
        return [Acceptance(entry) for entry in listed]

    def _write(self, acceptances: list[Acceptance]) -> None:
        self._file.write({ACCEPTED: [{name: value for name, value in acceptance.kept.items() if value} for acceptance in acceptances]})
