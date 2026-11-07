"""A validation report: the rules a fidelity's latest validation found broken, with each violation at its file and line."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.installation.destination import data_field

if TYPE_CHECKING:
    from space.kanban.ticket import FidelityProgress
    from space.repo.repo import Repo

SOURCE_LINES_BEFORE = 2
SOURCE_LINES_AFTER = 4
# The judgment the validating agent adds to a report, in the shape validate.md gives it.
JUDGMENT_HEADING = re.compile(r"^## Judgment — `(?P<file>[^`]+)`")
# A judgment the agent wrote, as against the example the report quotes indented in its instructions.
JUDGMENT_SECTION = re.compile(r"^#{1,2} Judgment\b", re.M)
JUDGED_RULE_HEADING = re.compile(r"^### `(?P<rule>[^`]+)` — Fail\s*$")
FINDING_LINE = re.compile(r"^- (?:(?P<file>[^\s:]+):(?P<line>\d+)\s+)?(?P<message>.+)$")


class SourceLine:
    """One numbered line of the file a violation names."""

    def __init__(self, number: int, text: str) -> None:
        self._number = number
        self._text = text

    @property
    @data_field
    def number(self) -> int:
        return self._number

    @property
    @data_field
    def text(self) -> str:
        return self._text


class Violation:
    """One place a report says a rule is broken: the file and line it names, when it names them, and the lines around it."""

    def __init__(self, location: str, line: int | None, message: str, source: list[SourceLine] | None = None) -> None:
        self._location = location
        self._line = line
        self._message = message
        self._source = list(source or [])

    @property
    @data_field
    def location(self) -> str:
        return self._location

    @property
    @data_field
    def line(self) -> int | None:
        return self._line

    @property
    @data_field
    def message(self) -> str:
        return self._message

    @property
    @data_field
    def source(self) -> list[SourceLine]:
        return list(self._source)

    def at(self, location: str, source: list[SourceLine]) -> Violation:
        """This violation in location, with the lines around it read from there."""
        return Violation(location, self._line, self._message, source)


class ReportRule:
    """One rule a report finds broken, in the one shape the board reads for graph hits and judged findings alike."""

    def __init__(self, fidelity: str, name: str, description: str, violations: list[Violation]) -> None:
        self._fidelity = fidelity
        self._name = name
        self._description = description
        self._violations = list(violations)

    @property
    @data_field
    def fidelity(self) -> str:
        return self._fidelity

    @property
    @data_field
    def name(self) -> str:
        return self._name

    @property
    @data_field
    def description(self) -> str:
        return self._description

    @property
    @data_field
    def count(self) -> int:
        return len(self._violations)

    @property
    @data_field
    def violations(self) -> list[Violation]:
        return list(self._violations)

    @property
    def identity(self) -> tuple:
        """A saved graph holds its whole practice's hits, so two fidelities of one practice report the same broken rule."""
        practice = self._fidelity.split("-")[0]
        return (practice, self._name, *((violation.location, violation.line, violation.message) for violation in self._violations))


class Report:
    """The rules a validation found broken. With no report it is empty, and it says when it has no saved graph, because
    the graph's rules are then missing from it."""

    def __init__(self, path: str = "", text: str = "", rules: list[ReportRule] | None = None, has_saved_graph: bool = False) -> None:
        self._path = path
        self._text = text
        self._rules = list(rules or [])
        self._has_saved_graph = has_saved_graph

    @classmethod
    def from_reports(cls, folder: str, reports: list[Report]) -> Report:
        """Every rule broken in reports, each listed once though two fidelities' reports share it, the latest first."""
        rules = {rule.identity: rule for report in reversed(reports) for rule in report.rules}
        return cls(folder, "", list(reversed(rules.values())), all(report.has_saved_graph for report in reports))

    @property
    @data_field
    def path(self) -> str:
        return self._path

    @property
    @data_field
    def text(self) -> str:
        return self._text

    @property
    @data_field
    def rules(self) -> list[ReportRule]:
        return list(self._rules)

    @property
    @data_field
    def has_saved_graph(self) -> bool:
        return self._has_saved_graph

    @property
    def violation_count(self) -> int:
        """Graph hits and judged findings together."""
        return sum(rule.count for rule in self._rules)


class ReportFile:
    """A validation report saved in a session folder, with the graph the validation checked saved beside it."""

    # It is made for the fidelity progress it reports on, which holds the ticket's session, the repository its files
    # are named from, and the rules this report answers for.

    def __init__(self, file: Path, progress: FidelityProgress) -> None:
        self._file = file
        self._progress = progress

    @property
    def file(self) -> Path:
        return self._file

    @property
    def stamp(self) -> str:
        """The date the report's name ends with, in a form that sorts by time."""
        return self._file.stem.rsplit("-", 1)[-1]

    @property
    def text(self) -> str:
        return self._file.read_text(encoding="utf-8", errors="replace")

    @property
    def has_result(self) -> bool:
        """Validate saves a report before the agent judges it, so one with no judgment and no saved graph has no result yet."""
        return self._graph.is_file() or JUDGMENT_SECTION.search(self.text) is not None

    @property
    def is_judged_failing(self) -> bool:
        return bool(Judgment.from_report(self.text))

    def report(self) -> Report:
        """The rules broken on the nodes of the saved graph, then each rule the agent's judgment fails that the graph did not hit."""
        text = self.text
        graph_rules = self._graph_rules() if self._graph.is_file() else []
        hit = {rule.name for rule in graph_rules}
        judged = [rule for rule in self._judged_rules(text) if rule.name not in hit]
        return Report(self._repo.path_from_top(self._file), text, graph_rules + judged, self._graph.is_file())

    @property
    def _repo(self) -> Repo:
        return self._progress.repo

    @property
    def _workpath(self) -> Path:
        """The folder the saved graph names its files from: the session's workpath, else the repository's top."""
        return Path(self._progress.session.workpath or self._repo.root).resolve()

    @property
    def _graph(self) -> Path:
        return self._file.with_suffix(".json")

    def _graph_rules(self) -> list[ReportRule]:
        return [self._rule(name, [self._violation_of(hit) for hit in hits]) for name, hits in self._hits_by_rule().items()]

    def _hits_by_rule(self) -> dict[str, list[dict]]:
        """The hits on the rules this report answers for: a saved graph holds its whole practice's hits. A rule no
        fidelity describes belongs to none, so every report keeps it."""
        from validate.graph_json_reader import violations_by_rule, violations_from_graph_json_files

        progress = self._progress
        answered = progress.rules_answered_by(self)
        described = progress.rule_descriptions
        scanned = self._scanned_rules()
        hits = violations_by_rule(violations_from_graph_json_files([self._graph], [progress.practice]))
        return {name: rule_hits for name, rule_hits in hits.items() if name in scanned and (name in answered or name not in described)}

    def _scanned_rules(self) -> set[str]:
        """The rules a scanner checks now; a saved graph keeps the hits of a scanner deleted since it was saved."""
        from harness.graph.practice_rules_registry import checks_for_practice
        from harness.graph.schema_rules import active_overlay_patterns

        overlays = json.loads(self._graph.read_text(encoding="utf-8")).get("overlays", [])
        return set(checks_for_practice(self._progress.practice, active_overlay_patterns(tuple(overlays))))

    def _judged_rules(self, text: str) -> list[ReportRule]:
        """Each rule the judgment fails, once however many judged files fail it, with its findings at the judged files' lines."""
        findings: dict[str, list[Violation]] = {}
        for judgment in Judgment.from_report(text):
            findings.setdefault(judgment.rule, []).extend(self._judged_violation(judgment.file, finding) for finding in judgment.findings)
        return [self._rule(rule, violations) for rule, violations in findings.items()]

    def _rule(self, name: str, violations: list[Violation]) -> ReportRule:
        progress = self._progress
        return ReportRule(progress.fidelity_slug, name, progress.rule_descriptions.get(name, ""), violations)

    def _judged_violation(self, judged_file: str, finding: Violation) -> Violation:
        """A finding names the judged file by its name alone, or no file; one that names another file keeps that file's path."""
        named = finding.location
        location = judged_file if not named or Path(named).name == Path(judged_file).name else named
        return finding.at(location, self._source_around(location, finding.line))

    def _violation_of(self, hit: dict) -> Violation:
        location = self._repo.path_from_top(self._workpath / hit["location"])
        line = hit["line_number"]
        return Violation(location, line, hit["violation_message"], self._source_around(location, line))

    def _source_around(self, location: str, line: int | None) -> list[SourceLine]:
        """The numbered lines around line; none when the violation names no line or the file is not in this repository."""
        root = self._repo.root
        target = (root / location).resolve()
        if line is None or root not in target.parents or not target.is_file():
            return []
        # Split on newlines alone: a graph counts lines that way, and splitlines() also breaks on form feeds.
        lines = target.read_text(encoding="utf-8", errors="replace").split("\n")
        first = max(line - SOURCE_LINES_BEFORE, 1)
        return [SourceLine(number, text.rstrip("\r")) for number, text in enumerate(lines[first - 1:line + SOURCE_LINES_AFTER], first)]


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
            located["file"] if located else "",
            int(located["line"]) if located else None,
            bullet["message"] if bullet else line,
        ))
        return True
