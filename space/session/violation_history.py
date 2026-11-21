"""ViolationHistory - every graph hit a session's validations found, how its judges judged it, and when it was fixed,
kept as JSON lines in the session's folder, so the rules that keep breaking, the fixes that bring a hit back, and the
hits judges call noise can be read across every run."""

from __future__ import annotations

import json
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

from harness.graph.location import Location
from harness.graph.violation import UNKNOWN_LOCATION, FoundBy, FoundOn, Violation
from space.session.session_log import REPORT_DATE_FORMAT, LogTimestamp
from space.session.validation_judgment import ReportJudgment

if TYPE_CHECKING:
    from space.repo.repo import Repo

VIOLATION_HISTORY_FILE = "violation-history.jsonl"
# How many characters of a commit's sha the history keeps, as ``git log --oneline`` shows it.
SHORT_SHA = 7
# How many characters the second a report's name ends with takes: ``20261116T075749``.
REPORT_STAMP_LENGTH = 15
# What a hit's subject calls its node: ``OoadClass `Graph```, whose name is in backticks.
NODE_NAME = re.compile(r"`(?P<name>[^`]+)`")
# A judged finding opens with the node it names, in backticks.
JUDGED_NODE = re.compile(r"^`(?P<name>[^`]+)`")
# One graph hit as a saved report lists it under its rule's ``### `rule``` heading.
RULE_HEADING = re.compile(r"^### `(?P<rule>[^`]+)`\s*$")
HIT_LINE = re.compile(
    r"^- \[[X!i]\] \*\*\w+\*\* \*\*\[graph rule\]\*\* - "
    r"(?:\[(?P<file>[^\]]+)\]\((?P<target>[^)]*)\)|`(?P<plain>[^`]*)`): (?P<rest>.*)$"
)
LINKED_LINE = re.compile(r"#L(?P<line>\d+)$")
SUBJECT = re.compile(r"^(?P<subject>\w+ `[^`]+`): (?P<message>.*)$")
FOUND, JUDGED, FIXED, RUN = "found", "judged", "fixed", "run"
STANDS, NOISE = "stands", "noise"
# Held while a run is recorded: two validates of one session, from two chats, each read the history and then append to it.
RECORDING = threading.Lock()


class HistoryEvent(TypedDict, total=False):
    """One line of the history: what happened (``event``: run, found, judged, or fixed), in which run, and to which
    hit: its rule, its file from the project's root, its line, and the name of its node."""

    event: str
    run: str
    at: str
    commit: str
    session: str
    fidelity: str
    rule: str
    file: str
    line: int | None
    node: str
    message: str
    verdict: str
    reason: str
    matched: bool
    last_found_in: str
    fixed_in: str
    paths: list[str]
    hits: int


class ValidationRun:
    """One validate's saved report and the graph hits it found in the files it checked (scope, each a file or folder
    from the project's root; every file when it names none). The report's name says its fidelity and when it ran."""

    def __init__(self, report: Path, hits: list[Violation], scope: list[str]) -> None:
        self.report = report
        self.hits = list(hits)
        self.scope = list(scope)

    @classmethod
    def from_report(cls, report: Path) -> ValidationRun:
        """The run a saved report records, read from its markdown alone: each graph hit listed under its rule's heading.
        A report names no scope, so it checked every file."""
        hits: list[Violation] = []
        rule = ""
        for line in report.read_text(encoding="utf-8", errors="replace").splitlines():
            heading = RULE_HEADING.match(line)
            rule = heading["rule"] if heading else rule
            hit = HIT_LINE.match(line)
            if hit:
                hits.append(_ListedHit(rule, hit).violation)
        return cls(report, hits, [])

    @property
    def name(self) -> str:
        return self.report.name

    @property
    def fidelity(self) -> str:
        """The fidelity the run validated, by the slug its report's name opens with."""
        return self.report.stem.rsplit("-", 1)[0]

    @property
    def at(self) -> str:
        """When the run started, from the stamp its report's name ends with."""
        stamp = self.report.stem.rsplit("-", 1)[-1][:REPORT_STAMP_LENGTH]
        return str(LogTimestamp(datetime.strptime(stamp, REPORT_DATE_FORMAT).replace(tzinfo=timezone.utc)))

    def covers(self, hit: Violation) -> bool:
        """Whether the run checked the file hit is in, so a hit it does not find there is fixed."""
        return not self.scope or hit.is_under(self.scope)


class _ListedHit:
    """One graph hit as a saved report lists it: ``- [X] **ERROR** **[graph rule]** - [file](target#Lnn): Kind `Name`:
    message``, under the heading of its rule."""

    def __init__(self, rule: str, listed: re.Match[str]) -> None:
        self._rule = rule
        self._listed = listed

    @property
    def violation(self) -> Violation:
        listed = self._listed
        file = listed["file"] if listed["file"] is not None else listed["plain"]
        line = LINKED_LINE.search(listed["target"] or "")
        said = SUBJECT.match(listed["rest"])
        subject, message = (said["subject"], said["message"]) if said else ("", listed["rest"])
        return Violation(FoundBy(self._rule, "", FoundOn("", subject)), message, Location(file, int(line["line"]) if line else None))


class _HitKey:
    """What tells one hit from another across runs: its rule, its file, and its node's name. Not its line, since an
    edit above a hit moves it without fixing it."""

    def __init__(self, hit: Violation) -> None:
        self._hit = hit
        self.rule = hit.rule
        self.file = hit.location.replace("\\", "/")
        named = NODE_NAME.search(hit.subject)
        self.node = named["name"] if named else hit.subject

    @property
    def parts(self) -> tuple[str, str, str]:
        return (self.rule, self.file, self.node)

    @property
    def fields(self) -> HistoryEvent:
        """The hit as a history line names it: its rule, file, line, and node."""
        return {"rule": self.rule, "file": self.file, "line": self._hit.line, "node": self.node}


class _MeasuredRun:
    """A run as the history records it: at the commit it measured, in the session whose history it joins."""

    def __init__(self, run: ValidationRun, commit: str, session: str) -> None:
        self.run = run
        self.commit = commit
        self._session = session

    @property
    def stamp(self) -> HistoryEvent:
        """What every line of the run says: the run, when, at which commit, in which session, and its fidelity."""
        run = self.run
        return {"run": run.name, "at": run.at, "commit": self.commit, "session": self._session, "fidelity": run.fidelity}

    @property
    def events(self) -> list[HistoryEvent]:
        """The run itself, with the files it checked and how many hits it found, then each hit it found."""
        run = self.run
        found = [{"event": FOUND, **self.stamp, **_HitKey(hit).fields, "message": hit.message} for hit in run.hits]
        return [{"event": RUN, **self.stamp, "paths": run.scope, "hits": len(run.hits)}, *found]

    def fixed_since(self, previous: str, hits: list[Violation]) -> list[HistoryEvent]:
        """Each of hits, which the previous run found, in a file this run checked and no longer found there, matched by
        rule, file, and node; each once."""
        now = {_HitKey(hit).parts for hit in self.run.hits}
        gone = {_HitKey(hit).parts: hit for hit in hits if self.run.covers(hit) and _HitKey(hit).parts not in now}
        return [{"event": FIXED, **self.stamp, **_HitKey(hit).fields, "last_found_in": previous, "fixed_in": self.commit} for hit in gone.values()]


class ViolationHistory:
    """A session's ``violation-history.jsonl``: one JSON line for each validate run, each graph hit it found, each
    finding its judge wrote or hit it called noise, and each hit a later run of the same fidelity no longer finds. It
    is only appended to, and it reads the commit each run measured from the checkout the session works in."""

    def __init__(self, file: Path, checkout: Repo | None = None) -> None:
        self._file = file
        self._checkout = checkout

    @property
    def file(self) -> Path:
        return self._file

    @property
    def events(self) -> list[HistoryEvent]:
        """Every line of the history, oldest first; none while it has none."""
        if not self._file.is_file():
            return []
        return [json.loads(line) for line in self._file.read_text(encoding="utf-8").splitlines() if line.strip()]

    def record(self, report: Path, hits: list[Violation], scope: list[str]) -> None:
        """Record the validate run that saved report and found hits in the files of scope, at the commit the checkout
        has checked out now."""
        self._record_at(ValidationRun(report, hits, scope), self._head())

    def _record_at(self, run: ValidationRun, commit: str) -> None:
        """Record run as measuring commit: first the judgment of the previous run of its fidelity, which its judge has
        surely appended by now, then the run, each hit it found, and each hit of that previous run it no longer finds."""
        with RECORDING:
            history = _HistoryRuns(self.events)
            previous = history.last_run(run.fidelity)
            measured = _MeasuredRun(run, commit, self._file.parent.name)
            fixed = measured.fixed_since(previous["run"], history.hits_of(previous["run"])) if previous is not None else []
            self._append([*self._judged(history, previous, run), *measured.events, *fixed])

    def rebuild(self, reports: list[Path], commits: dict[str, str]) -> None:
        """Write the history again from a session's saved reports alone, oldest first, each run at the commit commits
        names for its report (none when it names none), and the judgment of each fidelity's last run folded in too."""
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text("", encoding="utf-8")
        runs = [ValidationRun.from_report(report) for report in sorted(reports, key=lambda report: report.name)]
        for run in runs:
            self._record_at(run, commits.get(run.name, ""))
        history = _HistoryRuns(self.events)
        last = {run.fidelity: run for run in runs}
        self._append([event for run in last.values() for event in self._judged(history, history.last_run(run.fidelity), run)])

    def _head(self) -> str:
        """The commit the checkout has checked out, shortened; empty for a folder git does not know."""
        checkout = self._checkout
        return checkout.current_commit[:SHORT_SHA] if checkout is not None and checkout.is_clone else ""

    def _judged(self, history: _HistoryRuns, previous: HistoryEvent | None, folding: ValidationRun) -> list[HistoryEvent]:
        """The judgment appended to previous's report, read from the folder folding's report is in; none when there is
        no previous run, it is already folded in, or its report is gone."""
        if previous is None or history.is_judged(previous["run"]):
            return []
        report = folding.report.parent / previous["run"]
        if not report.is_file():
            return []
        judged = _JudgedRun(previous, history.hits_of(previous["run"]), ReportJudgment(report.read_text(encoding="utf-8", errors="replace")))
        return [{**event, "at": folding.at} for event in judged.events]

    def _append(self, events: list[HistoryEvent]) -> None:
        if not events:
            return
        self._file.parent.mkdir(parents=True, exist_ok=True)
        with self._file.open("a", encoding="utf-8") as history:
            history.writelines(json.dumps(event, ensure_ascii=False) + "\n" for event in events)


class _HistoryRuns:
    """The history as runs: the last run of each fidelity, the hits each run found, and which runs are judged."""

    def __init__(self, events: list[HistoryEvent]) -> None:
        self._events = events

    def last_run(self, fidelity: str) -> HistoryEvent | None:
        runs = [event for event in self._events if event.get("event") == RUN and event.get("fidelity") == fidelity]
        return runs[-1] if runs else None

    def hits_of(self, run: str) -> list[Violation]:
        """The hits run found, as violations at their file and line on their node."""
        found = [event for event in self._events if event.get("event") == FOUND and event.get("run") == run]
        return [
            Violation(FoundBy(event["rule"], "", FoundOn("", f"`{event['node']}`" if event.get("node") else "")), event.get("message", ""), Location(event["file"], event.get("line")))
            for event in found
        ]

    def is_judged(self, run: str) -> bool:
        return any(event.get("event") == JUDGED and event.get("run") == run for event in self._events)


class _JudgedRun:
    """The judgment of one run's report as history lines: each finding of a rule it fails (``stands``) and each graph
    hit it calls noise (``noise``), each saying whether it is one of the hits the run found or the judge's own."""

    def __init__(self, run: HistoryEvent, hits: list[Violation], judgment: ReportJudgment) -> None:
        self._run = run
        self._hits = hits
        self._judgment = judgment

    @property
    def events(self) -> list[HistoryEvent]:
        standing = [(self._judged_file(failed.file, finding), finding) for failed in self._judgment.fails for finding in failed.findings]
        noise = [(hit.location, hit) for hit in self._judgment.noise]
        return [self._event(STANDS, judged) for judged in standing] + [self._event(NOISE, judged) for judged in noise]

    def _event(self, verdict: str, judged: tuple[str, Violation]) -> HistoryEvent:
        file, finding = judged
        matched = self._matching(finding, file)
        node = self._node_named_by(finding) or (_HitKey(matched).node if matched is not None else "")
        run = self._run
        return {
            "event": JUDGED, "run": run["run"], "at": "", "commit": run.get("commit", ""), "session": run.get("session", ""), "fidelity": run.get("fidelity", ""),
            "rule": finding.rule, "file": file, "line": finding.line, "node": node,
            "verdict": verdict, "reason": finding.message, "matched": matched is not None,
        }

    def _matching(self, finding: Violation, file: str) -> Violation | None:
        """The hit the run found that the judged finding names: of the same rule, in file, at its line or on its node;
        none for a finding of the judge's own."""
        line, node = finding.line, self._node_named_by(finding)
        same = [hit for hit in self._hits if hit.rule == finding.rule and _HitKey(hit).file == file]
        return next((hit for hit in same if (line is not None and hit.line == line) or (node and _HitKey(hit).node == node)), None)

    def _node_named_by(self, finding: Violation) -> str:
        """The node a judged finding opens with, in backticks; empty when it names none."""
        named = JUDGED_NODE.match(finding.message)
        return named["name"] if named else ""

    def _judged_file(self, judged_file: str, finding: Violation) -> str:
        """A finding names the judged file by its name alone, or no file; one that names another file keeps it."""
        named = finding.location
        same = named in ("", UNKNOWN_LOCATION) or Path(named).name == Path(judged_file).name
        return (judged_file if same else named).replace("\\", "/")
