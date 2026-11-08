"""A validation report: the rules a fidelity's latest validation found broken, with each violation at its file and line."""

from __future__ import annotations

import json
import re
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

from cdd_guidance.actions.validate.graph_json_reader import violations_by_rule, violations_from_nodes
from harness.graph.saved_graph import SavedGraph, SavedGraphOutdated
from harness.graph.violation import UNKNOWN_LOCATION, Violation
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.rule import Rule
from harness.installation.destination import data_field

if TYPE_CHECKING:
    from space.repo.repo import Repo
    from space.session import Session

SOURCE_LINES_BEFORE = 2
SOURCE_LINES_AFTER = 4
# The judgment the validating agent adds to a report, in the shape validate.md gives it.
JUDGMENT_HEADING = re.compile(r"^## Judgment — `(?P<file>[^`]+)`")
# A judgment the agent wrote, as against the example the report quotes indented in its instructions.
JUDGMENT_SECTION = re.compile(r"^#{1,2} Judgment\b", re.M)
JUDGED_RULE_HEADING = re.compile(r"^### `(?P<rule>[^`]+)` — Fail\s*$")
FINDING_LINE = re.compile(r"^- (?:(?P<file>[^\s:]+):(?P<line>\d+)\s+)?(?P<message>.+)$")


class ReportRule:
    """One rule a report finds broken, in the one shape the board reads for graph hits and judged findings alike."""

    def __init__(self, fidelity: FidelityGuidance, rule: Rule, violations: list[Violation]) -> None:
        self._fidelity = fidelity
        self._rule = rule
        self._violations = list(violations)

    @property
    @data_field(reference=True)
    def fidelity(self) -> FidelityGuidance:
        """The fidelity whose report found the rule broken, which a fix of the rule validates again; sent by its slug,
        since the board sends each fidelity in full with its stage."""
        return self._fidelity

    @property
    @data_field
    def rule(self) -> Rule:
        """The broken rule, with its name and what it asks for. A rule no fidelity describes, such as one only a graph
        scanner checks, has its name alone."""
        return self._rule

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
        return (self._rule.slug, *((violation.practice, violation.location, violation.line, violation.message) for violation in self._violations))


class Report:
    """The rules a validation found broken. With no report it is empty, and it says when it has no saved graph, or its
    saved graph is in a shape the graph no longer writes, because the graph's rules are then missing from it."""

    def __init__(self, path: str = "", text: str = "", rules: list[ReportRule] | None = None, has_saved_graph: bool = False, is_out_of_date: bool = False) -> None:
        self._path = path
        self._text = text
        self._rules = list(rules or [])
        self._has_saved_graph = has_saved_graph
        self._is_out_of_date = is_out_of_date

    @classmethod
    def from_reports(cls, folder: str, reports: list[Report]) -> Report:
        """Every rule broken in reports, each listed once though two fidelities' reports share it, the latest first."""
        rules = {rule.identity: rule for report in reversed(reports) for rule in report.rules}
        return cls(
            folder,
            "",
            list(reversed(rules.values())),
            all(report.has_saved_graph for report in reports),
            any(report.is_out_of_date for report in reports),
        )

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
    @data_field
    def is_out_of_date(self) -> bool:
        """The saved graph was written in a shape the graph no longer reads, so validating again is the way to its rules."""
        return self._is_out_of_date

    @property
    @data_field
    def violation_count(self) -> int:
        """Graph hits and judged findings together."""
        return sum(rule.count for rule in self._rules)


class ReportFile:
    """A validation report of one fidelity, saved in a session folder, with the graph the validation checked saved
    beside it. It knows which of its practice's rules it answers for."""

    # The fidelity is the one its session holds, so it lists its own reports; the session its practice works in names
    # the folder the saved graph names its files from, and its repository names the report's files from its top.

    def __init__(self, file: Path, fidelity: FidelityGuidance) -> None:
        self._file = file
        self._fidelity = fidelity

    @classmethod
    def from_fidelity(cls, fidelity: FidelityGuidance) -> ReportFile | None:
        """The latest report of fidelity in the session its practice works in that has its result, else its latest;
        none when it has none. Validate saves a report before the agent judges it, so a report with no judgment and no
        saved graph yet does not hide an earlier one that has its result."""
        own = [cls(path, fidelity) for path in fidelity.reports()]
        with_result = [report for report in own if report.has_result]
        return (with_result or own or [None])[-1]

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
        """The rules broken on the nodes of the saved graph, then each rule the agent's judgment fails that the graph did
        not hit. A saved graph in a shape the graph no longer writes gives no rules, and the report says it is out of date."""
        text = self.text
        has_graph = self._graph.is_file()
        try:
            graph_rules = self._graph_rules() if has_graph else []
            is_out_of_date = False
        except SavedGraphOutdated:
            graph_rules, is_out_of_date = [], True
        hit = {rule.rule.slug for rule in graph_rules}
        judged = [rule for rule in self._judged_rules(text) if rule.rule.slug not in hit]
        return Report(self._repo.path_from_top(self._file), text, graph_rules + judged, has_graph, is_out_of_date)

    @property
    def _practice(self) -> PracticeGuidance:
        return self._fidelity.practice_guidance

    @property
    def _session(self) -> Session:
        return self._practice.session

    @property
    def _repo(self) -> Repo:
        return self._session.repo

    @property
    def _workpath(self) -> Path:
        """The folder the saved graph names its files from: the session's workpath, else the repository's top."""
        return Path(self._session.workpath or self._repo.root).resolve()

    @property
    def _graph(self) -> Path:
        return self._file.with_suffix(".json")

    @cached_property
    def _answered_rules(self) -> list[Rule]:
        """The rules this report answers for: its practice's shared rules, its fidelity's own, and every earlier
        fidelity's but those an earlier fidelity's newer report answers for."""
        earlier = [rule for fidelity in self._earlier_fidelities if not self._has_newer_report(fidelity) for rule in fidelity.rules]
        return [*self._practice.rules, *earlier, *self._fidelity.rules]

    @property
    def _described_rules(self) -> list[Rule]:
        """Every rule of the practice, its fidelity's own last: a saved graph holds the whole practice's hits, so every
        fidelity's rules count, and a rule two fidelities share is described as this one describes it."""
        return [*self._practice.every_rule(), *self._fidelity.rules]

    @property
    def _earlier_fidelities(self) -> list[FidelityGuidance]:
        """The fidelities of this report's practice that come before its fidelity."""
        fidelities = list(self._practice.fidelities)
        names = [fidelity.name for fidelity in fidelities]
        return fidelities[:names.index(self._fidelity.name)] if self._fidelity.name in names else []

    def _has_newer_report(self, earlier: FidelityGuidance) -> bool:
        """Whether an earlier fidelity was validated after this report was written, so its own report answers for its rules."""
        latest = ReportFile.from_fidelity(earlier)
        return latest is not None and latest.stamp > self.stamp

    def _rule_named(self, name: str) -> Rule:
        """The rule a graph hit or a judgment names, as this report's fidelity describes it; a rule no fidelity
        describes has its name alone."""
        return next((rule for rule in reversed(self._described_rules) if rule.slug == name), None) or Rule(name, "")

    def _graph_rules(self) -> list[ReportRule]:
        return [ReportRule(self._fidelity, self._rule_named(name), [self._violation_of(hit) for hit in hits]) for name, hits in self._hits_by_rule().items()]

    @cached_property
    def _checked_graph(self) -> SavedGraph | list[dict[str, Any]]:
        """The graph the validation checked, read from beside the report once: its saved graph, or the list of violating
        nodes validate keeps when it checked several graphs. SavedGraphOutdated when it was saved in a shape the graph
        no longer writes."""
        text = self._graph.read_text(encoding="utf-8")
        document = json.loads(text) if text.strip() else None
        if isinstance(document, list):
            return document
        return SavedGraph.from_document(document, str(self._graph)) if document is not None else SavedGraph([], {})

    def _hits_by_rule(self) -> dict[str, list[Violation]]:
        """The hits on the rules this report answers for: a saved graph holds its whole practice's hits. A rule no
        fidelity describes belongs to none, so every report keeps it."""
        checked = self._checked_graph
        practices = [self._practice.key]
        found = violations_from_nodes(checked, practices) if isinstance(checked, list) else checked.violations(practices)
        answered = {rule.slug for rule in self._answered_rules}
        described = {rule.slug for rule in self._described_rules}
        scanned = self._scanned_rules()
        return {name: rule_hits for name, rule_hits in violations_by_rule(found).items() if name in scanned and (name in answered or name not in described)}

    def _scanned_rules(self) -> set[str]:
        """The rules a scanner checks now; a saved graph keeps the hits of a scanner deleted since it was saved. A list
        of violating nodes keeps no overlays, so only the practice's own scanners count."""
        checked = self._checked_graph
        saved = SavedGraph([], {}) if isinstance(checked, list) else checked
        return set(saved.checks_of(self._practice))

    def _judged_rules(self, text: str) -> list[ReportRule]:
        """Each rule the judgment fails, once however many judged files fail it, with its findings at the judged files' lines."""
        findings: dict[str, list[Violation]] = {}
        for judgment in Judgment.from_report(text):
            findings.setdefault(judgment.rule, []).extend(self._judged_violation(judgment.file, finding) for finding in judgment.findings)
        return [ReportRule(self._fidelity, self._rule_named(rule), violations) for rule, violations in findings.items()]

    def _judged_violation(self, judged_file: str, finding: Violation) -> Violation:
        """A finding names the judged file by its name alone, or no file; one that names another file keeps that file's path."""
        named = finding.location
        location = judged_file if named in ("", UNKNOWN_LOCATION) or Path(named).name == Path(judged_file).name else named
        return finding.in_file(location, self._file_in_repository(location), SOURCE_LINES_BEFORE, SOURCE_LINES_AFTER)

    def _violation_of(self, hit: Violation) -> Violation:
        """A hit as the saved graph names it, from the workpath, named from the project with the lines around it."""
        file = self._workpath / hit.location
        return hit.in_file(self._repo.path_from_top(file), file, SOURCE_LINES_BEFORE, SOURCE_LINES_AFTER)

    def _file_in_repository(self, location: str) -> Path:
        """The file location names, a path from the project; the repository's top, which is no file, for a location
        outside the repository, so no file outside it is read."""
        root = self._repo.root
        target = (root / location).resolve()
        return target if root in target.parents else root


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
            self._rule,
            bullet["message"] if bullet else line,
            location=located["file"] if located else "",
            line=int(located["line"]) if located else None,
        ))
        return True
