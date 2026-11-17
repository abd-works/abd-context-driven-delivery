"""The slow test tiers run on a cadence by the cdd server: heavy every hour and e2e every day, each on main, in the
background. There is no clock: every time the server health report is read, the cadence looks at how long ago each tier
last started and starts the one that is overdue. Each run's result is kept where the health report shows it, and a run
that fails after one that passed is a new failure, which the chat raises as a toast."""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Iterator

from harness.installation.data_class import data_field
from harness.git.git import Git, RepoConnectError
from harness.process.process import BackgroundStart, PythonInterpreter, RunningProcess

TEST_SCRIPT = Path("scripts") / "test.ps1"
MAIN_BRANCH = "main"
RECORD_FILE = "test-runs.json"
# Held while one process looks at what is due and starts it.
CLAIM_FILE = "test-runs.claim"
CLAIM_STALE_SECONDS = 60
# How many of a run's last output lines its result keeps, enough to name what failed.
SUMMARY_LINES = 12


class TestTier(str, Enum):
    """A test tier the cdd server runs on a cadence, by the suite name scripts/test.ps1 takes."""

    __test__ = False  # not a test class, whatever pytest-style collectors think of the name

    HEAVY = "heavy"
    E2E = "e2e"

    @property
    def interval(self) -> timedelta:
        """How long after a run starts the next one is due: heavy within the hour, e2e within the day."""
        return timedelta(hours=1) if self is TestTier.HEAVY else timedelta(days=1)


# The line test.ps1 ends every whole run with: how many spec files passed of how many it ran.
FILES_PASSED = re.compile(r"^(\d+)/(\d*) files passed\s*$", re.MULTILINE)


def _counted_every_file_passed(output: str) -> bool:
    """test.ps1 reached its count, and every file it counted passed. A run cut short prints no total ("0/ files
    passed") and can still exit 0, so its exit code alone would record a pass for specs that never ran."""
    counts = FILES_PASSED.findall(output)
    if not counts:
        return False
    passed, total = counts[-1]
    return bool(total) and int(total) > 0 and passed == total


class RunOutcome(str, Enum):
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    # Recorded as running, but its process is gone without a result, such as when the computer restarted.
    ABANDONED = "abandoned"


class TestRun:
    """One run of a tier on one commit of main: when it started, how it ended, and the last lines it printed."""

    __test__ = False

    def __init__(self, tier: TestTier, commit: str, started_at: datetime, outcome: RunOutcome = RunOutcome.RUNNING, *,
                 pid: int = 0, finished_at: datetime | None = None, summary: str = "", is_new_failure: bool = False) -> None:
        self.tier = tier
        self.commit = commit
        self.started_at = started_at
        self.outcome = outcome
        self.pid = pid
        self.finished_at = finished_at
        self._summary = summary
        self._is_new_failure = is_new_failure

    @classmethod
    def from_json(cls, json_data: dict) -> TestRun:
        finished = json_data.get("finished_at")
        return cls(TestTier(json_data["tier"]), json_data.get("commit", ""), datetime.fromisoformat(json_data["started_at"]),
                   RunOutcome(json_data["outcome"]), pid=int(json_data.get("pid", 0)),
                   finished_at=datetime.fromisoformat(finished) if finished else None, summary=json_data.get("summary", ""),
                   is_new_failure=bool(json_data.get("is_new_failure", False)))

    def to_json(self) -> dict:
        return {"tier": self.tier.value, "commit": self.commit, "started_at": self.started_at.isoformat(), "outcome": self.outcome.value,
                "pid": self.pid, "finished_at": self.finished_at.isoformat() if self.finished_at else None,
                "summary": self._summary, "is_new_failure": self._is_new_failure}

    def finished(self, exit_code: int, output: str, previous: TestRun | None, now: datetime) -> TestRun:
        """This run ended with exit_code, having printed output; previous is the tier's run before it."""
        outcome = RunOutcome.PASSED if exit_code == 0 and _counted_every_file_passed(output) else RunOutcome.FAILED
        is_new = outcome is RunOutcome.FAILED and (previous is None or previous.outcome is not RunOutcome.FAILED)
        last_lines = "\n".join(output.strip().splitlines()[-SUMMARY_LINES:])
        return TestRun(self.tier, self.commit, self.started_at, outcome, pid=self.pid, finished_at=now, summary=last_lines, is_new_failure=is_new)

    def is_due(self, now: datetime) -> bool:
        """Its interval has passed since it started; at once when it was abandoned, since it gave no result."""
        return self.outcome is RunOutcome.ABANDONED or now - self.started_at >= self.tier.interval

    @property
    def is_run_by_this_process(self) -> bool:
        """Recorded as running for this process: the cadence records a run, then starts the process that runs it,
        which may read the record before its id is in it. A run another live process holds is not this one's."""
        return self.outcome is RunOutcome.RUNNING and (self.pid in (0, os.getpid()) or not RunningProcess(self.pid).alive)

    @property
    def is_live(self) -> bool:
        return self.outcome is RunOutcome.RUNNING and RunningProcess(self.pid).alive

    @property
    @data_field
    def name(self) -> str:
        return self.tier.value

    @property
    @data_field
    def state(self) -> str:
        """running, passed, failed or abandoned."""
        return self.outcome.value

    @property
    @data_field
    def run_id(self) -> str:
        """Names the run, so the chat raises its toast once: the tier and when it started."""
        return f"{self.tier.value}@{self.started_at.isoformat()}"

    @property
    @data_field
    def started(self) -> str:
        return self.started_at.isoformat()

    @property
    @data_field
    def summary(self) -> str:
        """The last lines the run printed."""
        return self._summary

    @property
    @data_field
    def is_new_failure(self) -> bool:
        """It failed, and the run of its tier before it did not."""
        return self._is_new_failure


class TestRunRecord:
    """The latest run of each tier, and the finished run before it, kept in one JSON file in the cdd home."""

    __test__ = False

    def __init__(self, folder: Path | str) -> None:
        self.folder = Path(folder)
        self.path = self.folder / RECORD_FILE
        self.lock = threading.RLock()

    def latest(self, tier: TestTier) -> TestRun | None:
        return self._run(tier, "latest")

    def previous(self, tier: TestTier) -> TestRun | None:
        """The run of tier before the latest, which tells whether the latest's failure is new."""
        return self._run(tier, "previous")

    def save(self, run: TestRun) -> None:
        """Keep run as its tier's latest; a different run held as latest becomes the previous one."""
        with self.lock:
            runs = self._read()
            held = runs.get(run.tier.value, {})
            latest = held.get("latest")
            if latest and TestRun.from_json(latest).run_id != run.run_id:
                held["previous"] = latest
            held["latest"] = run.to_json()
            runs[run.tier.value] = held
            self.folder.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(runs, indent=2), encoding="utf-8")

    @contextlib.contextmanager
    def claimed(self) -> Iterator[bool]:
        """Hold the record against every other process for one look at what is due: True when this one holds it. Each
        chat's health report asks, and two asking at once must not start the same tier twice. A claim older than a
        minute was left by a process that died holding it, and is taken over."""
        claim = self.folder / CLAIM_FILE
        self.folder.mkdir(parents=True, exist_ok=True)
        try:
            if claim.exists() and time.time() - claim.stat().st_mtime > CLAIM_STALE_SECONDS:
                claim.unlink(missing_ok=True)
            handle = os.open(claim, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except OSError:
            yield False
            return
        try:
            os.close(handle)
            yield True
        finally:
            claim.unlink(missing_ok=True)

    def log_path(self, tier: TestTier) -> Path:
        return self.folder / f"test-run-{tier.value}.log"

    def _run(self, tier: TestTier, which: str) -> TestRun | None:
        held = self._read().get(tier.value, {}).get(which)
        return TestRun.from_json(held) if held else None

    def _read(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}


class TestRunner:
    """The boundary to scripts/test.ps1: start a tier in a background process that records its own result, or run one
    here and answer its exit code and output."""

    __test__ = False

    def start(self, tier: TestTier, checkout: Path, record: TestRunRecord) -> int:
        """Start the tier in a process of its own, which outlives the cdd server, and answer its process id."""
        record.folder.mkdir(parents=True, exist_ok=True)
        command = [PythonInterpreter().windowless, "-m", "harness.diagnostics.test_runs", tier.value, str(checkout), str(record.folder)]
        with record.log_path(tier).open("w", encoding="utf-8") as log:
            env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2]), "PYTHONIOENCODING": "utf-8"}
            return BackgroundStart(log).run(command, checkout, env).pid

    def run(self, tier: TestTier, checkout: Path, env: dict[str, str] | None = None) -> tuple[int, str]:
        """Run the tier in checkout to its end, its output going to this process's output as well; env adds variables."""
        command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(checkout / TEST_SCRIPT), "-Suite", tier.value]
        process = subprocess.Popen(command, cwd=checkout, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                                   env={**os.environ, **env} if env else None)
        lines = []
        for line in process.stdout:
            sys.stdout.write(line)
            lines.append(line)
        return process.wait(), "".join(lines)


def main_checkout(project: Path | str, git: Git | None = None) -> Path | None:
    """The repository's own folder, the first worktree git lists, while it has main checked out and is a CDD checkout
    with scripts/test.ps1; else none, and the cadence runs nothing."""
    project = Path(project)
    if not (project / TEST_SCRIPT).is_file():
        return None
    try:
        listing = (git or Git(project)).run("worktree", "list", "--porcelain")
    except RepoConnectError:
        return None
    first = listing.split("\n\n")[0].splitlines()
    folder = next((line.removeprefix("worktree ") for line in first if line.startswith("worktree ")), "")
    branch = next((line.removeprefix("branch refs/heads/") for line in first if line.startswith("branch ")), "")
    return Path(folder) if folder and branch == MAIN_BRANCH and (Path(folder) / TEST_SCRIPT).is_file() else None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# The scheduled e2e run's screenshots sit under .sessions/scheduled/e2e-test-results/, apart from ticket and hand runs.
SCHEDULED_RELEASE = "scheduled"


def e2e_run_name(run: TestRun) -> str:
    """The folder name the scheduled e2e run's screenshots are kept under: run- and when it started."""
    return f"run-{run.started_at.strftime('%Y-%m-%d-%H-%M-%S')}"


def _review_screens(checkout: Path, run_name: str) -> list[str]:
    from harness.e2e_review.e2e_review import ScheduledReview

    return ScheduledReview(checkout, run_name).start()


class TestCadence:
    """Runs heavy every hour and e2e every day on main. Nothing keeps time: ``start_due`` is called whenever the health
    report is read, and starts the overdue tier, one run at a time, e2e first since it is the one that runs least."""

    __test__ = False

    def __init__(self, checkout: Path | None, record: TestRunRecord, runner: TestRunner | None = None, git: Git | None = None,
                 clock: Callable[[], datetime] = _utc_now, review: Callable[[Path, str], list[str]] | None = None) -> None:
        self.checkout = checkout
        self.record = record
        self._runner = runner or TestRunner()
        self._git = git or (Git(checkout) if checkout else None)
        self._clock = clock
        self._review = review or _review_screens

    @property
    def latest_runs(self) -> list[TestRun]:
        """The latest run of each tier that has run, a run whose process is gone read as abandoned."""
        runs = [self.record.latest(tier) for tier in TestTier]
        return [self._settled(run) for run in runs if run is not None]

    def due(self) -> list[TestTier]:
        """The tiers whose interval has passed since they last started, or that never ran; none while a run is live."""
        latest = {run.tier: run for run in self.latest_runs}
        if any(run.outcome is RunOutcome.RUNNING for run in latest.values()):
            return []
        return [tier for tier in (TestTier.E2E, TestTier.HEAVY) if tier not in latest or latest[tier].is_due(self._clock())]

    def start_due(self) -> TestRun | None:
        """Start the first overdue tier on main in the background and record it as running; nothing when none is due or
        there is no main checkout."""
        if self.checkout is None:
            return None
        with self.record.lock, self.record.claimed() as is_claimed:
            due = self.due() if is_claimed else []
            if not due:
                return None
            run = TestRun(due[0], self._head(), self._clock())
            self.record.save(run)
            try:
                run.pid = self._runner.start(run.tier, self.checkout, self.record)
            except OSError as not_started:
                run.outcome = RunOutcome.ABANDONED
                run._summary = f"The run did not start: {not_started}"
            self.record.save(run)
            return run

    def run_now(self, tier: TestTier) -> TestRun:
        """Run tier here to its end and record its result: the background process the cadence starts runs this, and so
        can a person. A run the cadence recorded as running is the one finished; otherwise a new one starts."""
        started = self.record.latest(tier)
        head = self._head()
        # A run left as running by a process that ended, on another commit, is not taken over: this run tests HEAD.
        if started is None or not started.is_run_by_this_process or started.commit != head:
            started = TestRun(tier, head, self._clock(), pid=os.getpid())
            self.record.save(started)
        if tier is TestTier.E2E:
            # Each browser story step is screenshotted into this run's folder under .sessions/scheduled/, then reviewed.
            run_name = e2e_run_name(started)
            exit_code, output = self._runner.run(tier, self.checkout, {"E2E_RELEASE": SCHEDULED_RELEASE, "E2E_RUN": run_name})
            output += "".join(f"\nscreen review: {line}" for line in self._reviewed(run_name))
        else:
            exit_code, output = self._runner.run(tier, self.checkout)
        finished = started.finished(exit_code, output, self.record.previous(tier), self._clock())
        self.record.save(finished)
        return finished

    def _reviewed(self, run_name: str) -> list[str]:
        """The screen review of the e2e run just ended; a review that cannot start says why and leaves the run's result."""
        try:
            return self._review(self.checkout, run_name)
        except Exception as not_reviewed:  # the tests' result stands whatever the review does
            return [f"not started: {not_reviewed}"]

    def _settled(self, run: TestRun) -> TestRun:
        if run.outcome is RunOutcome.RUNNING and not run.is_live:
            run.outcome = RunOutcome.ABANDONED
        return run

    def _head(self) -> str:
        try:
            return self._git.run("rev-parse", "HEAD") if self._git else ""
        except RepoConnectError:
            return ""


def main(argv: list[str] | None = None) -> int:
    """python -m harness.diagnostics.test_runs <tier> <checkout> <record folder>: run a tier and record its result. The
    cadence starts it this way in the background; the /release command runs it the same way."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("tier", choices=[tier.value for tier in TestTier])
    parser.add_argument("checkout")
    parser.add_argument("record", nargs="?", default="")
    arguments = parser.parse_args(argv)
    # Run from a console, the output is echoed in its code page, such as cp1252, which cannot write every character a
    # spec prints; one it cannot write is shown as ? rather than ending the run.
    sys.stdout.reconfigure(errors="replace")
    checkout = Path(arguments.checkout).resolve()
    record = TestRunRecord(arguments.record or default_record_folder())
    run = TestCadence(checkout, record).run_now(TestTier(arguments.tier))
    print(f"{run.tier.value} {run.outcome.value} on {run.commit[:9]}")
    return 0 if run.outcome is RunOutcome.PASSED else 1


def default_record_folder() -> Path:
    """The cdd home, where the one cdd server keeps the record every chat's health report reads."""
    from harness.mcp.cdd_home import CddHome

    return CddHome().folder


if __name__ == "__main__":
    sys.exit(main())
