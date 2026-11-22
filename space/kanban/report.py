"""A validation report: the rules a fidelity's latest validation found broken, with each violation at its file and line."""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.saved_graph import SavedGraph, SavedGraphOutdated
from harness.graph.violation import UNKNOWN_LOCATION, Violation
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.rule import Rule
from harness.installation.data_class import data_field
from space.session.validation_judgment import Judgment
from space.session.validation_report import ValidationReport

if TYPE_CHECKING:
    from space.repo.repo import Repo
    from space.session import Session
    from space.session.accepted_violations import AcceptedViolations


class ViolationNotInReportError(LookupError):
    """A person accepted, or took back the acceptance of, a violation the fidelity's latest report does not list, such
    as one a newer validate no longer finds. It names the rule and the place asked for, and the report read."""

    def __init__(self, shown: Violation, report: Path) -> None:
        self.rule = shown.rule
        self.location = shown.location
        self.line = shown.line
        self.report = report
        super().__init__(f"{report.name} lists no violation of {shown.rule} at {shown.location}:{shown.line or ''} saying {shown.message!r}; read the report again")


class ListedViolation:
    """One violation of a report as its finder names it (found), which is what an acceptance is matched on, and as the
    report shows it (shown), named from the project with the lines around it."""

    def __init__(self, found: Violation, shown: Violation) -> None:
        self.found = found
        self.shown = shown

    def is_shown_as(self, asked: Violation) -> bool:
        """Whether asked, a violation a page sends back, is this one as the report showed it."""
        shown = self.shown
        return (shown.rule, shown.node_id, shown.message, shown.location, shown.line) == (asked.rule, asked.node_id, asked.message, asked.location, asked.line)


# A fix in one format alone leaves the fidelity's other formats still breaking the rule, so every fix asks for all of them.
_EVERY_FORMAT = "Fix every format of the fidelity: its documents, its diagrams, and its code."
# What a prompt's lines are joined with.
_LINE = "\n"


def _in_session(prompt: str, fidelity: FidelityGuidance) -> str:
    """prompt naming the session of fidelity's ticket: a prompt runs in whichever chat it is sent to, whose open session
    can be another ticket's, as the session's action commands name it."""
    return f"{prompt} session={fidelity.practice_guidance.session.session_file_from_project}"


def _error_lines(violation: Violation) -> list[str]:
    """Where a violation is and what it says, then the lines around it, the failing line marked >, so the agent edits
    the content validate judged, not a line near it."""
    place = f"{violation.location}:{violation.line}" if violation.line else violation.location
    return [f"{place}: {violation.message}", *(f"{'>' if line.number == violation.line else ' '} {line.number} | {line.text}" for line in violation.source)]


class ViolationPrompts:
    """What a report's Fix and False buttons send a ticket's chat about one violation, in the report's own words, so the
    agent needs no second validate to find out what failed."""

    def __init__(self, fidelity: FidelityGuidance, rule: Rule, violation: Violation) -> None:
        self._fidelity = fidelity
        self._rule = rule
        self._violation = violation

    @property
    @data_field
    def fix(self) -> str:
        """Fix this violation, and nothing the error does not name, in every format of the fidelity, then validate it
        with this rule on the files changed."""
        slug, rule = self._fidelity.slug, self._rule.slug
        return _in_session(_LINE.join([
            f"Fix this violation of the {slug} rule.",
            "",
            f"{rule}: {self._rule.body}",
            "",
            f"1. {_LINE.join(_error_lines(self._violation))}",
            "",
            f"Change each file so the content marked > follows the rule, and change nothing the errors do not name. {_EVERY_FORMAT} Then validate {slug} with rule {rule} on the files you changed.",
        ]), self._fidelity)

    @property
    @data_field(key="false")
    def false_positive(self) -> str:
        """The person says the finding is wrong, a defect in the rule or the check behind it: the chat looks there and
        leaves the judged content alone."""
        slug, rule = self._fidelity.slug, self._rule.slug
        return _in_session(_LINE.join([
            f"This violation of the {slug} rule is false. Investigate the rule for errors.",
            "",
            f"{rule}: {self._rule.body}",
            "",
            _LINE.join(_error_lines(self._violation)),
            "",
            f"Find why {rule} reported this: read the rule's text and the check that judges it, and run it on the content marked >. Say whether the rule's wording, its check, or what the check read is wrong, then correct that test first. Change none of the content the finding names. If the finding turns out to be right, say why and change nothing.",
        ]), self._fidelity)


class ReportRule:
    """One rule a report finds broken, in the one shape the board reads for graph hits and judged findings alike, with
    the prompts its Fix buttons send."""

    def __init__(self, fidelity: FidelityGuidance, rule: Rule, violations: list[Violation], report_path: str) -> None:
        self._fidelity = fidelity
        self._rule = rule
        self._violations = list(violations)
        # The report, as a path from the project, that found the rule broken, which a fix of the whole rule reads.
        self._report_path = report_path

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
    @data_field
    def violation_prompts(self) -> list[ViolationPrompts]:
        """What each violation's Fix and False send, one for each of violations, in the same order."""
        return [ViolationPrompts(self._fidelity, self._rule, violation) for violation in self._violations]

    @property
    @data_field
    def fix_prompt(self) -> str:
        """Fix every violation of the rule the report found, read from the report itself."""
        return _in_session(f"Fix all violations of {self._rule.slug} found in this report: {self._report_path}. {_EVERY_FORMAT}", self._fidelity)

    @property
    def identity(self) -> tuple:
        """A saved graph holds its whole practice's hits, so two fidelities of one practice report the same broken rule."""
        return (self._rule.slug, *((violation.practice, violation.location, violation.line, violation.message) for violation in self._violations))


class ReportSource:
    """Where a report was read from: its path from the project, or the reports folder of several, and its text."""

    def __init__(self, path: str = "", text: str = "") -> None:
        self.path = path
        self.text = text


class SavedGraphStanding:
    """Whether the graph a validation checked is saved beside its report, and whether it was saved in a shape the graph
    no longer writes: either way the graph's rules are missing from the report."""

    def __init__(self, has_saved_graph: bool = False, is_out_of_date: bool = False) -> None:
        self.has_saved_graph = has_saved_graph
        self.is_out_of_date = is_out_of_date


class Report:
    """The rules a validation found broken. With no report it is empty, and it says when it has no saved graph, or its
    saved graph is in a shape the graph no longer writes, because the graph's rules are then missing from it."""

    def __init__(self, source: ReportSource | None = None, rules: list[ReportRule] | None = None, standing: SavedGraphStanding | None = None) -> None:
        source = source or ReportSource()
        standing = standing or SavedGraphStanding()
        self._path = source.path
        self._text = source.text
        self._rules = list(rules or [])
        self._accepted: list[ReportRule] = []
        self._has_saved_graph = standing.has_saved_graph
        self._is_out_of_date = standing.is_out_of_date

    @classmethod
    def from_reports(cls, folder: str, reports: list[Report]) -> Report:
        """Every rule broken in reports, each listed once though two fidelities' reports share it, the latest first."""
        rules = {rule.identity: rule for report in reversed(reports) for rule in report.rules}
        accepted = {rule.identity: rule for report in reversed(reports) for rule in report.accepted}
        standing = SavedGraphStanding(all(report.has_saved_graph for report in reports), any(report.is_out_of_date for report in reports))
        return cls(ReportSource(folder), list(reversed(rules.values())), standing).leaving_out(list(reversed(accepted.values())))

    def leaving_out(self, accepted: list[ReportRule]) -> Report:
        """This report saying which violations it leaves out because a person accepted them, under the rule each breaks."""
        self._accepted = list(accepted)
        return self

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
    def fix_prompt(self) -> str:
        """Fix every violation the report found: the report already holds them, so the chat reads them there rather than
        from a copy in the message. It names the session of the report's rules' ticket; empty for a report of none."""
        if not self._rules:
            return ""
        return _in_session(f"Fix all violations found in this report: {self._path}. {_EVERY_FORMAT}", self._rules[0].fidelity)

    @property
    @data_field
    def is_out_of_date(self) -> bool:
        """The saved graph was written in a shape the graph no longer reads, so validating again is the way to its rules."""
        return self._is_out_of_date

    @property
    @data_field
    def violation_count(self) -> int:
        """Graph hits and judged findings together, without the ones a person accepted."""
        return sum(rule.count for rule in self._rules)

    @property
    @data_field
    def accepted(self) -> list[ReportRule]:
        """The violations a person accepted as they are, under the rule each breaks: left out of the rules and the
        count, and listed so a person can take an acceptance back."""
        return list(self._accepted)

    @property
    @data_field
    def accepted_count(self) -> int:
        """How many violations the report leaves out because a person accepted them."""
        return sum(rule.count for rule in self._accepted)


class ReportFile:
    """A validation report of one fidelity as the board reads it: the rules it finds broken, with the violations of the
    graph the validation checked, saved beside it, each with the node it was found on. It knows which of its practice's
    rules it answers for, and describes each from its practice, since the saved report points at a rule's text instead
    of copying it."""

    # The report's fidelity is the one its session holds, so it lists its own reports; the session its practice works
    # in names the folder the saved graph names its files from, and its repository names the report's files from its top.

    def __init__(self, report: ValidationReport) -> None:
        self._report = report
        self._file = report.file
        self._fidelity = report.fidelity

    @classmethod
    def from_fidelity(cls, fidelity: FidelityGuidance) -> ReportFile | None:
        """The latest report of fidelity in the session its practice works in that has its result, else its latest;
        none when it has none. Validate saves a report before the agent judges it, so a report with no judgment and no
        saved graph yet does not hide an earlier one that has its result."""
        own = [cls(report) for report in fidelity.session_output.validation_reports.listed()]
        with_result = [report for report in own if report.has_result]
        return (with_result or own or [None])[-1]

    @property
    def file(self) -> Path:
        return self._file

    @property
    def version(self) -> str:
        """What changes whenever what this report counts can change: the report itself, which the agent's judgment is
        added to after Validate saves it, the graph saved beside it, the session's reports folder, which a newer
        report of an earlier fidelity joins and so takes over that fidelity's rules, and the project's accepted
        violations, which leave a violation out of the count or bring it back."""
        stamps = [self._changed_at(path) for path in (self._file, self._graph, self._file.parent, self._accepted_violations.file)]
        return ":".join([self._file.name, *map(str, stamps)])

    @property
    def text(self) -> str:
        return self._report.text

    @property
    def has_result(self) -> bool:
        return self._report.has_result

    @property
    def is_judged_failing(self) -> bool:
        """Whether the judgment fails a rule with a finding nobody accepted. The judged files are read, for the content
        an acceptance is matched on, only once the project holds an acceptance: the board asks this on every read."""
        text = self.text
        if not Judgment.from_report(text):
            return False
        if not self._accepted_violations.holds_any:
            return True
        judged = [listed.found for findings in self._judged(text).values() for listed in findings]
        return bool(self._accepted_violations.open_among(judged))

    def report(self) -> Report:
        """The rules broken on the nodes of the saved graph, then each rule the agent's judgment fails that the graph did
        not hit, each without the violations a person accepted, which the report lists apart. A saved graph in a shape
        the graph no longer writes gives no rules, and the report says it is out of date."""
        text = self.text
        has_graph = self._graph.is_file()
        try:
            graph_hits = self._graph_hits() if has_graph else {}
            is_out_of_date = False
        except SavedGraphOutdated:
            graph_hits, is_out_of_date = {}, True
        graph_rules, accepted_hits = self._open_and_accepted(graph_hits)
        hit = {rule.rule.slug for rule in graph_rules}
        judged, accepted_findings = self._open_and_accepted({rule: findings for rule, findings in self._judged(text).items() if rule not in hit})
        return Report(self._source, graph_rules + judged, SavedGraphStanding(has_graph, is_out_of_date)).leaving_out(accepted_hits + accepted_findings)

    @property
    def _source(self) -> ReportSource:
        """Where the report was read from: its path from the project, and its text."""
        return ReportSource(self._repo.path_from_top(self._file), self.text)

    def accept(self, asked: Violation) -> None:
        """Accept the violation this report shows as asked, so no later report, validate, or count names it while it
        stays the same. *ViolationNotInReportError* when the report lists no such violation."""
        self._accepted_violations.accept(self._listed_as(asked).found)

    def reopen(self, asked: Violation) -> None:
        """Take back the acceptance of the violation this report shows as asked, so it is reported again."""
        self._accepted_violations.reopen(self._listed_as(asked).found)

    def _listed_as(self, asked: Violation) -> ListedViolation:
        """The violation of this report, a graph hit or a judged finding, shown as asked."""
        graph_hits = self._graph_hits() if self._graph.is_file() else {}
        every = [listed for by_rule in (graph_hits, self._judged(self.text)) for violations in by_rule.values() for listed in violations]
        found = next((listed for listed in every if listed.is_shown_as(asked)), None)
        if found is None:
            raise ViolationNotInReportError(asked, self._file)
        return found

    def _open_and_accepted(self, by_rule: dict[str, list[ListedViolation]]) -> tuple[list[ReportRule], list[ReportRule]]:
        """The rules of by_rule with the violations nobody accepted, and the same rules with the accepted ones; a rule
        with none of a kind is left out of that kind."""
        still_open: list[ReportRule] = []
        accepted: list[ReportRule] = []
        for name, listed in by_rule.items():
            left_out = self._accepted_violations.accepted_among([violation.found for violation in listed])
            is_left_out = [any(violation.found is found for found in left_out) for violation in listed]
            for rules, wanted in ((still_open, False), (accepted, True)):
                shown = [violation.shown for violation, out in zip(listed, is_left_out) if out is wanted]
                if shown:
                    rules.append(ReportRule(self._fidelity, self._rule_named(name), shown, self._source.path))
        return still_open, accepted

    @cached_property
    def _accepted_violations(self) -> AcceptedViolations:
        return self._session.accepted_violations

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
        return self._report.saved_graph

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
        return [*self._practice.every_rule, *self._fidelity.rules]

    @property
    def _earlier_fidelities(self) -> list[FidelityGuidance]:
        """The fidelities of this report's practice that come before its fidelity."""
        fidelities = list(self._practice.fidelities)
        names = [fidelity.name for fidelity in fidelities]
        return fidelities[:names.index(self._fidelity.name)] if self._fidelity.name in names else []

    def _has_newer_report(self, earlier: FidelityGuidance) -> bool:
        """Whether an earlier fidelity was validated after this report was written, so its own report answers for its rules."""
        latest = ReportFile.from_fidelity(earlier)
        return latest is not None and latest._report.is_newer_than(self._report)

    def _rule_named(self, name: str) -> Rule:
        """The rule a graph hit or a judgment names, as this report's fidelity describes it; a rule no fidelity
        describes has its name alone."""
        return next((rule for rule in reversed(self._described_rules) if rule.slug == name), None) or Rule(name, "")

    def _graph_hits(self) -> dict[str, list[ListedViolation]]:
        """Each graph hit this report answers for, under its rule, as the saved graph names it and as the report shows it."""
        return {name: [ListedViolation(hit, self._violation_of(hit)) for hit in hits] for name, hits in self._hits_by_rule().items()}

    @cached_property
    def _checked_graph(self) -> SavedGraph:
        """The violations of the graph the validation checked, and the overlays it was loaded with, read from beside the
        report once: all a report reads of it, so that is all Validate keeps there. SavedGraphOutdated when it was saved
        in a shape the graph no longer writes."""
        return SavedGraph.from_file(self._graph)

    def _hits_by_rule(self) -> dict[str, list[Violation]]:
        """The hits on the rules this report answers for: a saved graph holds its whole practice's hits. A rule no
        fidelity describes belongs to none, so every report keeps it."""
        found = self._checked_graph.violations([self._practice.key])
        answered = {rule.slug for rule in self._answered_rules}
        described = {rule.slug for rule in self._described_rules}
        scanned = self._scanned_rules()
        return {name: rule_hits for name, rule_hits in Violation.by_rule(found).items() if name in scanned and (name in answered or name not in described)}

    def _scanned_rules(self) -> set[str]:
        """The rules a scanner checks now, with the overlays the graph was saved with; a saved graph keeps the hits of a
        scanner deleted since it was saved. The session's graph answers, with the patterns it already holds."""
        return set(self._session.graph.applied_patterns.checks_of(self._practice, self._checked_graph.overlays))

    def _judged(self, text: str) -> dict[str, list[ListedViolation]]:
        """Each rule the judgment fails, once however many judged files fail it, with its findings at the judged files'
        lines. A finding is shown as its judge names it, so that is also what its acceptance is matched on."""
        findings: dict[str, list[ListedViolation]] = {}
        for judgment in Judgment.from_report(text):
            shown = [self._judged_violation(judgment.file, finding) for finding in judgment.findings]
            findings.setdefault(judgment.rule, []).extend(ListedViolation(violation, violation) for violation in shown)
        return findings

    def _judged_violation(self, judged_file: str, finding: Violation) -> Violation:
        """A finding names the judged file by its name alone, or no file; one that names another file keeps that file's path."""
        named = finding.location
        location = judged_file if named in ("", UNKNOWN_LOCATION) or Path(named).name == Path(judged_file).name else named
        return finding.in_file(location, self._file_in_repository(location))

    def _violation_of(self, hit: Violation) -> Violation:
        """A hit as the saved graph names it, from the workpath, named from the project with the lines around it."""
        file = self._workpath / hit.location
        return hit.in_file(self._repo.path_from_top(file), file)

    def _file_in_repository(self, location: str) -> Path:
        """The file location names, a path from the project; the repository's top, which is no file, for a location
        outside the repository, so no file outside it is read."""
        root = self._repo.root
        target = (root / location).resolve()
        return target if root in target.parents else root

    def _changed_at(self, path: Path) -> int:
        """When path was last written, in nanoseconds; none while it is not there."""
        return path.stat().st_mtime_ns if path.exists() else 0
