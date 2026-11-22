"""A fidelity's validation reports in a session: each one markdown file, named with the fidelity's slug and the moment
it was made, with the graph its validation checked saved beside it."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.location import Location
from harness.graph.violation import FoundBy, FoundOn, Violation
from harness.process.log_timestamp import REPORT_DATE_FORMAT, LogTimestamp
from space.session.validation.validation_judgment import JUDGMENT_SECTION, ReportJudgment

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance
    from space.session.practices.practice_session_output import FidelitySessionOutput

# How many characters the moment a report's name ends with takes: ``20261116T075749``.
REPORT_STAMP_LENGTH = 15
# One graph hit as a saved report lists it under its rule's ``### `rule``` heading.
RULE_HEADING = re.compile(r"^### `(?P<rule>[^`]+)`\s*$")
HIT_LINE = re.compile(
    r"^- \[[X!i]\] \*\*\w+\*\* \*\*\[graph rule\]\*\* - "
    r"(?:\[(?P<file>[^\]]+)\]\((?P<target>[^)]*)\)|`(?P<plain>[^`]*)`): (?P<rest>.*)$"
)
LINKED_LINE = re.compile(r"#L(?P<line>\d+)$")
SUBJECT = re.compile(r"^(?P<subject>\w+ `[^`]+`): (?P<message>.*)$")


class ValidationReport:
    """One validation report of a fidelity in a session: a markdown file named with the fidelity's slug and the moment it
    was made (``stories-story-map-20261116T075749.md``; a second report in the same second takes the next number,
    ``…T075749_2.md``), and the violations of the graph its validation checked, saved beside it under the same name.
    The name is written and read here alone."""

    def __init__(self, file: Path, fidelity: FidelityGuidance) -> None:
        self._file = file
        self._fidelity = fidelity

    @property
    def file(self) -> Path:
        return self._file

    @property
    def name(self) -> str:
        return self._file.name

    @property
    def fidelity(self) -> FidelityGuidance:
        return self._fidelity

    @property
    def made_at(self) -> LogTimestamp:
        """When the validation that saved the report started, from the moment its name ends with."""
        moment = datetime.strptime(self._stamp[:REPORT_STAMP_LENGTH], REPORT_DATE_FORMAT).replace(tzinfo=timezone.utc)
        return LogTimestamp(moment)

    def is_newer_than(self, other: ValidationReport) -> bool:
        """Whether this report was made after other, of any fidelity: by the moment, then the number, its name ends with."""
        return self._stamp > other._stamp

    @property
    def _stamp(self) -> str:
        """The moment the name ends with, and the number after it for a second report in one second, which sort by time."""
        return self._file.stem[len(self._fidelity.slug) + 1:]

    @property
    def saved_graph(self) -> Path:
        """Where the violations of the graph the validation checked are saved, beside the report."""
        return self._file.with_suffix(".json")

    @property
    def text(self) -> str:
        return self._file.read_text(encoding="utf-8", errors="replace") if self._file.is_file() else ""

    def write(self, text: str) -> None:
        self._file.write_text(text, encoding="utf-8")

    @property
    def has_result(self) -> bool:
        """Validate saves a report before the agent judges it, so one with no judgment and no saved graph has no result yet."""
        return self.saved_graph.is_file() or JUDGMENT_SECTION.search(self.text) is not None

    @property
    def judgment(self) -> ReportJudgment:
        """The judgment the validating agent appended to the report; empty while it has none."""
        return ReportJudgment(self.text)

    @property
    def listed_hits(self) -> list[Violation]:
        """The graph hits the report's markdown lists, each under its rule's heading: ``- [X] **ERROR** **[graph rule]**
        - [file](target#Lnn): Kind `Name`: message``. Read only to rebuild a history from saved reports alone; a
        validation records the hits of the graph it checked."""
        hits: list[Violation] = []
        rule = ""
        for line in self.text.splitlines():
            heading = RULE_HEADING.match(line)
            rule = heading["rule"] if heading else rule
            listed = HIT_LINE.match(line)
            if listed:
                hits.append(self._listed_hit(rule, listed))
        return hits

    def _listed_hit(self, rule: str, listed: re.Match[str]) -> Violation:
        file = listed["file"] if listed["file"] is not None else listed["plain"]
        line = LINKED_LINE.search(listed["target"] or "")
        said = SUBJECT.match(listed["rest"])
        subject, message = (said["subject"], said["message"]) if said else ("", listed["rest"])
        return Violation(FoundBy(rule, "", FoundOn("", subject)), message, Location(file, int(line["line"]) if line else None))


class ValidationReports:
    """One fidelity's validation reports in a session."""

    def __init__(self, output: FidelitySessionOutput) -> None:
        self._output = output

    def listed(self) -> list[ValidationReport]:
        """This fidelity's validation reports in the session, oldest first: report names end with their moment, which
        sorts by time."""
        folder = self._output.reports_folder
        fidelity = self._output.fidelity
        files = sorted(folder.glob(f"{fidelity.slug}-*.md")) if folder.is_dir() else []
        return [ValidationReport(file, fidelity) for file in files]

    def new(self) -> ValidationReport:
        """A report of this fidelity made now, its file created empty under a name no other call holds: a call in the
        same second as another takes the next number (``…T034343_2.md``), so the moment stays where it is read and the
        names still sort by time."""
        folder = self._output.reports_folder
        folder.mkdir(parents=True, exist_ok=True)
        dated = folder / f"{self._output.fidelity.slug}-{datetime.now(timezone.utc).strftime(REPORT_DATE_FORMAT)}.md"
        path, number = dated, 1
        while not self._created(path):
            number += 1
            path = dated.with_name(f"{dated.stem}_{number}{dated.suffix}")
        return ValidationReport(path, self._output.fidelity)

    def _created(self, path: Path) -> bool:
        """Create path as an empty file; false when another call already holds that name."""
        try:
            path.touch(exist_ok=False)
        except FileExistsError:
            return False
        return True
