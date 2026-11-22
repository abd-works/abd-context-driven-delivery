"""The judgment the validating agent appends to a validation report: the rules it fails, file by file, with a finding
at each line, and the graph hits it judges noise."""

from __future__ import annotations

import re

from harness.graph.location import Location
from harness.graph.violation import NOWHERE, FoundBy, Violation

# The judgment the validating agent adds to a report, in the shape validate.md gives it.
JUDGMENT_HEADING = re.compile(r"^## Judgment — `(?P<file>[^`]+)`")
# A judgment the agent wrote, as against the example the report quotes indented in its instructions.
JUDGMENT_SECTION = re.compile(r"^#{1,2} Judgment\b", re.M)
JUDGED_RULE_HEADING = re.compile(r"^### `(?P<rule>[^`]+)` — Fail\s*$")
FINDING_LINE = re.compile(r"^- (?:(?P<file>[^\s:]+):(?P<line>\d+)\s+)?(?P<message>.+)$")
# The table of graph hits a judge calls noise: one row per hit, its file and line, its rule, and why.
NOISE_HEADING = re.compile(r"^## Graph hits judged noise\s*$")
NOISE_ROW = re.compile(r"^\|\s*`?(?P<file>[^|`:]+):(?P<line>\d+)`?\s*\|\s*`?(?P<rule>[^|`]+?)`?\s*\|\s*(?P<reason>.*?)\s*\|\s*$")


class Judgment:
    """One rule the judgment in a validation report fails, in one judged file, with its findings."""

    def __init__(self, file: str, rule: str) -> None:
        self._file = file
        self._rule = rule
        self._findings: list[Violation] = []

    @classmethod
    def from_report(cls, text: str) -> list[Judgment]:
        """The rules a report's judgment fails; none when the report has no judgment."""
        judgments: list[Judgment] = []
        judged_file, current = "", None
        for line in text.splitlines():
            heading = JUDGMENT_HEADING.match(line)
            if heading:
                judged_file, current = heading["file"], None
                continue
            rule = JUDGED_RULE_HEADING.match(line)
            if rule and judged_file:
                current = cls(judged_file, rule["rule"])
                judgments.append(current)
                continue
            if line.startswith("#"):
                current = None
                continue
            if current and line.strip() and not current._add_finding_from(line.strip()):
                current = None
        return judgments

    @property
    def file(self) -> str:
        return self._file

    @property
    def rule(self) -> str:
        return self._rule

    @property
    def findings(self) -> list[Violation]:
        """Each finding at the file and line it names, when it names them; its source is read by whoever shows it."""
        return list(self._findings)

    def _add_finding_from(self, line: str) -> bool:
        """A bullet is a finding, and a paragraph under a rule with no bullets is its one finding. A paragraph after the
        findings ends the rule, so a Passes list the agent adds after its judgment is not read as findings."""
        bullet = FINDING_LINE.match(line)
        if bullet is None and self._findings:
            return False
        located = bullet if bullet and bullet["line"] else None
        self._findings.append(Violation(
            FoundBy(self._rule),
            bullet["message"] if bullet else line,
            Location(located["file"], int(located["line"])) if located else NOWHERE,
        ))
        return True


class ReportJudgment:
    """The judgment appended to one validation report: the rules it fails, with their findings, and the graph hits it
    calls noise in its ``## Graph hits judged noise`` table."""

    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def fails(self) -> list[Judgment]:
        """Each rule the judgment fails in each judged file; none when the report has no judgment."""
        return Judgment.from_report(self._text)

    @property
    def noise(self) -> list[Violation]:
        """Each row of the noise table as the hit it names: its rule, at its file and line, with why the judge calls it
        noise as its message; none when the report has no such table."""
        rows: list[Violation] = []
        in_table = False
        for line in self._text.splitlines():
            if line.startswith("#"):
                in_table = NOISE_HEADING.match(line) is not None
                continue
            row = NOISE_ROW.match(line.strip()) if in_table else None
            if row:
                rows.append(Violation(FoundBy(row["rule"].strip()), row["reason"], Location(row["file"].strip(), int(row["line"]))))
        return rows
