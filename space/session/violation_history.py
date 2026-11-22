"""ViolationHistory - every graph hit a session's validations found, how its judges judged it, and when it was fixed,
kept as JSON lines in the session's folder, so the rules that keep breaking, the fixes that bring a hit back, and the
hits judges call noise can be read across every run."""

from __future__ import annotations

import dataclasses
import json
import re
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from harness.graph.location import Location
from harness.graph.violation import UNKNOWN_LOCATION, FoundBy, FoundOn, Violation

from space.session.validation_report import ValidationReport

if TYPE_CHECKING:
    from space.repo.repo import Repo

VIOLATION_HISTORY_FILE = "violation-history.jsonl"
# How many characters of a commit's sha the history keeps, as ``git log --oneline`` shows it.
SHORT_SHA = 7
# What a hit's subject calls its node: ``OoadClass `Graph```, whose name is in backticks.
NODE_NAME = re.compile(r"`(?P<name>[^`]+)`")
# A judged finding opens with the node it names, in backticks.
JUDGED_NODE = re.compile(r"^`(?P<name>[^`]+)`")
STANDS, NOISE = "stands", "noise"
# Held while a run is recorded: two validates of one session, from two chats, each read the history and then append to it.
RECORDING = threading.Lock()


@dataclass(frozen=True)
class RunStamp:
    """What every line of one run says: the run (its report's name), when it ran, at which commit, in which session,
    and the slug of the fidelity it validated."""

    run: str
    at: str
    commit: str
    session: str
    fidelity: str

    @classmethod
    def read(cls, record: dict[str, Any]) -> RunStamp:
        return cls(record.get("run", ""), record.get("at", ""), record.get("commit", ""), record.get("session", ""), record.get("fidelity", ""))

    @property
    def record(self) -> dict[str, Any]:
        return {"run": self.run, "at": self.at, "commit": self.commit, "session": self.session, "fidelity": self.fidelity}


@dataclass(frozen=True)
class HistoryHit:
    """One hit as the history names it: its rule, its file from the project's root, its line, and its node's name. What
    tells one hit from another across runs is its rule, file, and node, not its line, since an edit above a hit moves it
    without fixing it."""

    rule: str
    file: str
    line: int | None
    node: str

    @classmethod
    def of(cls, hit: Violation) -> HistoryHit:
        named = NODE_NAME.search(hit.subject)
        return cls(hit.rule, hit.location.replace("\\", "/"), hit.line, named["name"] if named else hit.subject)

    @classmethod
    def read(cls, record: dict[str, Any]) -> HistoryHit:
        return cls(record.get("rule", ""), record.get("file", ""), record.get("line"), record.get("node", ""))

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.rule, self.file, self.node)

    @property
    def record(self) -> dict[str, Any]:
        return {"rule": self.rule, "file": self.file, "line": self.line, "node": self.node}

    def violation(self, message: str) -> Violation:
        """The hit as a violation at its file and line on its node."""
        return Violation(FoundBy(self.rule, "", FoundOn("", f"`{self.node}`" if self.node else "")), message, Location(self.file, self.line))


@dataclass(frozen=True)
class HistoryLine:
    """One line of the history: what happened (its ``event``), in which run. Written with exactly the keys earlier lines
    carry, since a later run matches its fixes against them."""

    event: ClassVar[str] = ""
    stamp: RunStamp

    @property
    def run(self) -> str:
        return self.stamp.run

    @property
    def record(self) -> dict[str, Any]:
        return {"event": self.event, **self.stamp.record, **self._own_record}

    @property
    def _own_record(self) -> dict[str, Any]:
        return {}

    @staticmethod
    def read(record: dict[str, Any]) -> HistoryLine:
        """The line a history's JSON object records, by its ``event``."""
        kind = next((kind for kind in (RunLine, FoundLine, FixedLine, JudgedLine) if kind.event == record.get("event")), None)
        if kind is None:
            raise ValueError(f"a violation history line records no event it knows: {record!r}")
        return kind.read_own(RunStamp.read(record), record)


@dataclass(frozen=True)
class RunLine(HistoryLine):
    """A validate run: the files it checked (paths, each a file or folder from the project's root; every file when it
    names none) and how many hits it found."""

    event: ClassVar[str] = "run"
    paths: list[str] = dataclasses.field(default_factory=list)
    hits: int = 0

    @classmethod
    def read_own(cls, stamp: RunStamp, record: dict[str, Any]) -> RunLine:
        return cls(stamp, list(record.get("paths", [])), record.get("hits", 0))

    @property
    def _own_record(self) -> dict[str, Any]:
        return {"paths": self.paths, "hits": self.hits}

    def covers(self, hit: HistoryHit) -> bool:
        """Whether the run checked the file hit is in, so a hit it does not find there is fixed."""
        return not self.paths or hit.violation("").is_under(self.paths)


@dataclass(frozen=True)
class FoundLine(HistoryLine):
    """A graph hit a run found, with its message."""

    event: ClassVar[str] = "found"
    hit: HistoryHit = HistoryHit("", "", None, "")
    message: str = ""

    @classmethod
    def read_own(cls, stamp: RunStamp, record: dict[str, Any]) -> FoundLine:
        return cls(stamp, HistoryHit.read(record), record.get("message", ""))

    @property
    def _own_record(self) -> dict[str, Any]:
        return {**self.hit.record, "message": self.message}


@dataclass(frozen=True)
class FixedLine(HistoryLine):
    """A hit the previous run of the fidelity found, in a file this run checked, that this run no longer finds."""

    event: ClassVar[str] = "fixed"
    hit: HistoryHit = HistoryHit("", "", None, "")
    last_found_in: str = ""
    fixed_in: str = ""

    @classmethod
    def read_own(cls, stamp: RunStamp, record: dict[str, Any]) -> FixedLine:
        return cls(stamp, HistoryHit.read(record), record.get("last_found_in", ""), record.get("fixed_in", ""))

    @property
    def _own_record(self) -> dict[str, Any]:
        return {**self.hit.record, "last_found_in": self.last_found_in, "fixed_in": self.fixed_in}


@dataclass(frozen=True)
class JudgedLine(HistoryLine):
    """A finding a run's judge wrote on a rule it fails (``stands``), or a graph hit it called noise (``noise``), saying
    whether it is one of the hits the run found (matched) or the judge's own."""

    event: ClassVar[str] = "judged"
    hit: HistoryHit = HistoryHit("", "", None, "")
    verdict: str = ""
    reason: str = ""
    matched: bool = False

    @classmethod
    def read_own(cls, stamp: RunStamp, record: dict[str, Any]) -> JudgedLine:
        return cls(stamp, HistoryHit.read(record), record.get("verdict", ""), record.get("reason", ""), bool(record.get("matched")))

    @property
    def _own_record(self) -> dict[str, Any]:
        return {**self.hit.record, "verdict": self.verdict, "reason": self.reason, "matched": self.matched}


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
    def lines(self) -> list[HistoryLine]:
        """Every line of the history, oldest first; none while it has none."""
        if not self._file.is_file():
            return []
        return [HistoryLine.read(json.loads(line)) for line in self._file.read_text(encoding="utf-8").splitlines() if line.strip()]

    def record(self, report: ValidationReport, hits: list[Violation], scope: list[str]) -> None:
        """Record the validate run that saved report and found hits in the files of scope, at the commit the checkout
        has checked out now."""
        self._record_at(report, RunLine(self._stamp(report, self._head()), list(scope), len(hits)), hits)

    def rebuild(self, reports: list[ValidationReport], commits: dict[str, str]) -> None:
        """Write the history again from a session's saved reports alone, oldest first, each run at the commit commits
        names for its report (none when it names none), its hits those its markdown lists, and the judgment of each
        fidelity's last run folded in too."""
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._file.write_text("", encoding="utf-8")
        ordered = sorted(reports, key=lambda report: report.name)
        for report in ordered:
            hits = report.listed_hits
            self._record_at(report, RunLine(self._stamp(report, commits.get(report.name, "")), [], len(hits)), hits)
        last = {report.fidelity.slug: report for report in ordered}
        lines = self.lines
        self._append([line for report in last.values() for line in self._judged(lines, self._last_run(lines, report.fidelity.slug), report)])

    def _stamp(self, report: ValidationReport, commit: str) -> RunStamp:
        return RunStamp(report.name, str(report.made_at), commit, self._file.parent.name, report.fidelity.slug)

    def _record_at(self, report: ValidationReport, run: RunLine, hits: list[Violation]) -> None:
        """Record run, which saved report and found hits: first the judgment of the previous run of its fidelity, which
        its judge has surely appended by now, then the run, each hit it found, and each hit of that previous run it no
        longer finds."""
        with RECORDING:
            lines = self.lines
            previous = self._last_run(lines, run.stamp.fidelity)
            found = [FoundLine(run.stamp, HistoryHit.of(hit), hit.message) for hit in hits]
            fixed = self._fixed(run, found, previous, self._found_in(lines, previous)) if previous is not None else []
            self._append([*self._judged(lines, previous, report), run, *found, *fixed])

    def _fixed(self, run: RunLine, found: list[FoundLine], previous: RunLine, earlier: list[FoundLine]) -> list[FixedLine]:
        """Each hit previous found (earlier), in a file run checked, that run no longer finds, matched by rule, file,
        and node; each once."""
        now = {line.hit.key for line in found}
        gone = {line.hit.key: line.hit for line in earlier if run.covers(line.hit) and line.hit.key not in now}
        return [FixedLine(run.stamp, hit, previous.run, run.stamp.commit) for hit in gone.values()]

    def _last_run(self, lines: list[HistoryLine], fidelity: str) -> RunLine | None:
        runs = [line for line in lines if isinstance(line, RunLine) and line.stamp.fidelity == fidelity]
        return runs[-1] if runs else None

    def _found_in(self, lines: list[HistoryLine], run: RunLine | None) -> list[FoundLine]:
        return [line for line in lines if isinstance(line, FoundLine) and run is not None and line.run == run.run]

    def _head(self) -> str:
        """The commit the checkout has checked out, shortened; empty for a folder git does not know."""
        checkout = self._checkout
        return checkout.current_commit[:SHORT_SHA] if checkout is not None and checkout.is_clone else ""

    def _judged(self, lines: list[HistoryLine], previous: RunLine | None, folding: ValidationReport) -> list[JudgedLine]:
        """The judgment appended to previous's report, read from the folder folding's report is in, each line stamped
        with when folding ran; none when there is no previous run, it is already folded in, or its report is gone."""
        if previous is None or any(isinstance(line, JudgedLine) and line.run == previous.run for line in lines):
            return []
        report = ValidationReport(folding.file.parent / previous.run, folding.fidelity)
        if not report.file.is_file():
            return []
        judgment = report.judgment
        hits = [line.hit for line in self._found_in(lines, previous)]
        stamp = dataclasses.replace(previous.stamp, at=str(folding.made_at))
        standing = [(self._judged_file(failed.file, finding), finding) for failed in judgment.fails for finding in failed.findings]
        noise = [(hit.location, hit) for hit in judgment.noise]
        return [self._judged_line(stamp, hits, STANDS, judged) for judged in standing] + [self._judged_line(stamp, hits, NOISE, judged) for judged in noise]

    def _judged_line(self, stamp: RunStamp, hits: list[HistoryHit], verdict: str, judged: tuple[str, Violation]) -> JudgedLine:
        """One judged finding as a line: on the hit the run found that it names, of the same rule, in its file, at its
        line or on its node; else on the node it names, as the judge's own."""
        file, finding = judged
        named = JUDGED_NODE.match(finding.message)
        node = named["name"] if named else ""
        same = [hit for hit in hits if hit.rule == finding.rule and hit.file == file]
        matched = next((hit for hit in same if (finding.line is not None and hit.line == finding.line) or (node and hit.node == node)), None)
        hit = HistoryHit(finding.rule, file, finding.line, node or (matched.node if matched is not None else ""))
        return JudgedLine(stamp, hit, verdict, finding.message, matched is not None)

    def _judged_file(self, judged_file: str, finding: Violation) -> str:
        """A finding names the judged file by its name alone, or no file; one that names another file keeps it."""
        named = finding.location
        same = named in ("", UNKNOWN_LOCATION) or Path(named).name == Path(judged_file).name
        return (judged_file if same else named).replace("\\", "/")

    def _append(self, lines: list[HistoryLine]) -> None:
        if not lines:
            return
        self._file.parent.mkdir(parents=True, exist_ok=True)
        with self._file.open("a", encoding="utf-8") as history:
            history.writelines(json.dumps(line.record, ensure_ascii=False) + "\n" for line in lines)
