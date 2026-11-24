"""The slow test tiers run on a cadence by the cdd server: heavy every hour and e2e every day, each on main, in the
background. There is no clock: every time the server health report is read, the cadence looks at how long ago each tier
last started and starts the one that is overdue. A tier runs in a detached worktree at the commit its run records, in a
process the run names, and its result is kept where the health report shows it; a run that fails after one that passed
is a new failure, which the chat raises as a toast."""
from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Iterator

from harness.e2e_review.e2e_review import RUN_STAMP_FORMAT, ScheduledReview
from harness.installation.data_class import data_field
from harness.mcp.cdd_home import CddHome
from harness.git.git import Git, RepoConnectError
from harness.process.lock_file import LockFile
from harness.process.process import BackgroundStart, PythonInterpreter, RunningProcess
from harness.process.starter_bound_job import StarterBoundJob

TEST_SCRIPT = Path("scripts") / "test.ps1"
MAIN_BRANCH = "main"
RECORD_FILE = "test-runs.json"
# The lock file held while one process looks at what is due and starts it, or saves a run.
CLAIM_FILE = "test-runs.claim"
# How long a run waits between tries at a claim another process holds, which is held for a second or two.
CLAIM_WAIT_SECONDS = 1
# How long a save waits for another process's look at the record to end.
SAVE_WAIT_SECONDS = 30
# What the record keeps a tier run by scripts/test.ps1 itself under, beside the tier's latest run and the one before it.
SCRIPT_RUN = "script"
# Set for the scripts/test.ps1 a recorded run starts, which then does not record itself a second time.
RUN_RECORDED_VARIABLE = "CDD_TEST_RUN_RECORDED"
# How long a read or a write of the record is tried again while Windows refuses it, which it does for the instant
# another process puts a new record in the file's place.
RECORD_BUSY_SECONDS = 5
RECORD_BUSY_POLL_SECONDS = 0.01
# Under the record's folder, the detached worktree each tier's run works in.
WORKTREES_FOLDER = "test-run-worktrees"
# How long git may take to check a commit's files out into a run's worktree, or to remove it.
WORKTREE_SECONDS = 600
# The packages npm installed beside a package.json, which git does not keep and a run's worktree borrows.
INSTALLED_PACKAGES = "node_modules"
# The language adapters an install writes into the checkout, which git does not keep and a run's worktree copies.
INSTALLED_ADAPTERS = Path(".claude") / "language-adapters"
# How long a run started by hand waits between looks at whether another process's run has ended.
WAIT_SECONDS = 10
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


class RunOutcome(str, Enum):
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    # Recorded as running, but its process is gone without a result, such as when the computer restarted.
    ABANDONED = "abandoned"


class TestRun:
    """One run of a tier on one commit of one checkout: when it started, the process that runs it, how it ended, and
    the last lines it printed."""

    __test__ = False

    def __init__(self, tier: TestTier, commit: str, started_at: datetime, outcome: RunOutcome = RunOutcome.RUNNING, *,
                 checkout: str = "", pid: int = 0, process_started: datetime | None = None, finished_at: datetime | None = None,
                 summary: str = "", is_new_failure: bool = False) -> None:
        self.tier = tier
        self.commit = commit
        self.started_at = started_at
        self.outcome = outcome
        self.checkout = checkout
        self.pid = pid
        self.process_started = process_started
        self.finished_at = finished_at
        self._summary = summary
        self._is_new_failure = is_new_failure

    @classmethod
    def from_json(cls, json_data: dict) -> TestRun:
        """The run json_data holds. Raises ValueError, KeyError, TypeError or AttributeError for what is no run."""
        started_at = datetime.fromisoformat(json_data["started_at"])
        if started_at.tzinfo is None:
            raise ValueError(f"started_at {json_data['started_at']!r} has no UTC offset")
        finished, process_started = json_data.get("finished_at"), json_data.get("process_started")
        return cls(TestTier(json_data["tier"]), json_data.get("commit", ""), started_at, RunOutcome(json_data["outcome"]),
                   checkout=json_data.get("checkout", ""), pid=int(json_data.get("pid", 0)),
                   process_started=datetime.fromisoformat(process_started) if process_started else None,
                   finished_at=datetime.fromisoformat(finished) if finished else None, summary=json_data.get("summary", ""),
                   is_new_failure=bool(json_data.get("is_new_failure", False)))

    def to_json(self) -> dict:
        return {"tier": self.tier.value, "commit": self.commit, "checkout": self.checkout, "started_at": self.started_at.isoformat(),
                "outcome": self.outcome.value, "pid": self.pid,
                "process_started": self.process_started.isoformat() if self.process_started else None,
                "finished_at": self.finished_at.isoformat() if self.finished_at else None,
                "summary": self._summary, "is_new_failure": self._is_new_failure}

    def taken_by(self, process: RunningProcess) -> TestRun:
        """process runs this from now on: the run keeps its id and when it started, which together name that one
        process, since the system gives an ended process's id to a later one."""
        self.pid = process.pid
        self.process_started = process.started_at
        return self

    def finished(self, exit_code: int, output: str, previous: TestRun | None, now: datetime) -> TestRun:
        """This run ended with exit_code, having printed output; previous is the tier's run before it."""
        outcome = RunOutcome.PASSED if exit_code == 0 and self._counted_every_file_passed(output) else RunOutcome.FAILED
        is_new = outcome is RunOutcome.FAILED and (previous is None or previous.outcome is not RunOutcome.FAILED)
        last_lines = "\n".join(output.strip().splitlines()[-SUMMARY_LINES:])
        return TestRun(self.tier, self.commit, self.started_at, outcome, checkout=self.checkout, pid=self.pid,
                       process_started=self.process_started, finished_at=now, summary=last_lines, is_new_failure=is_new)

    def _counted_every_file_passed(self, output: str) -> bool:
        """test.ps1 reached its count, and every file it counted passed. A run cut short prints no total ("0/ files
        passed") and can still exit 0, so its exit code alone would record a pass for specs that never ran."""
        counts = FILES_PASSED.findall(output)
        if not counts:
            return False
        passed, total = counts[-1]
        return bool(total) and int(total) > 0 and passed == total

    def not_started(self, reason: OSError) -> TestRun:
        """The process that was to run this never started: it is abandoned, and its summary says why."""
        self.outcome = RunOutcome.ABANDONED
        self._summary = f"The run did not start: {reason}"
        return self

    def settled(self) -> TestRun:
        """This run as it stands now: abandoned when it is recorded as running and its process is gone."""
        if self.outcome is RunOutcome.RUNNING and not self.is_live:
            self.outcome = RunOutcome.ABANDONED
        return self

    @property
    def folder_name(self) -> str:
        """The folder the scheduled e2e run's screenshots are kept under: run- and when it started."""
        return f"run-{self.started_at.strftime(RUN_STAMP_FORMAT)}"

    def is_due(self, now: datetime) -> bool:
        """Its interval has passed since it started; at once when it was abandoned, since it gave no result."""
        return self.outcome is RunOutcome.ABANDONED or now - self.started_at >= self.tier.interval

    def is_on(self, checkout: Path | None) -> bool:
        """It ran, or runs, on checkout."""
        return bool(checkout) and os.path.normcase(self.checkout) == os.path.normcase(str(checkout))

    @property
    def is_live(self) -> bool:
        """Recorded as running, and the process it names still runs: one with its id that started when the record
        says. A record with an id alone, or an id a later program was given, names no process that runs this."""
        if self.outcome is not RunOutcome.RUNNING or self.process_started is None:
            return False
        process = RunningProcess(self.pid)
        return process.alive and process.started_at == self.process_started

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


class TestRunRecordUnreadable(Exception):
    """The record's file holds something that is no record of test runs. It is left as it is, for a person to mend or
    remove: written over, it would lose the earlier results, and the next failure would be called new."""

    __test__ = False

    def __init__(self, path: Path, held: object, reason: str) -> None:
        super().__init__(f"{path} is not a record of test runs: {reason}. It holds {str(held)[:200]!r}. "
                         "Mend the file or remove it; nothing has changed it.")
        self.path = path
        self.held = held


class TestRunRecord:
    """The latest run of each tier on one checkout, and the finished run before it, kept with every other checkout's
    in one JSON file in the cdd home, with the run scripts/test.ps1 makes of a tier when a person or an agent starts it
    in the checkout's own folder. A record with no checkout holds the runs kept before runs named theirs. One process at
    a time looks at the record and changes it, holding its claim, a *LockFile* beside it."""

    __test__ = False

    def __init__(self, folder: Path | str, checkout: Path | str | None = None) -> None:
        self.folder = Path(folder)
        self.path = self.folder / RECORD_FILE
        self.checkout = Path(checkout).resolve() if checkout else None
        self.lock = threading.RLock()
        self._claim = LockFile(self.folder / CLAIM_FILE, SAVE_WAIT_SECONDS)

    def latest(self, tier: TestTier) -> TestRun | None:
        return self._run(tier, "latest")

    def previous(self, tier: TestTier) -> TestRun | None:
        """The run of tier before the latest, which tells whether the latest's failure is new."""
        return self._run(tier, "previous")

    @property
    def runs(self) -> list[TestRun]:
        """Every run the file holds, of every tier and every checkout: any of them may be live on this computer."""
        return [self._as_run(held[which]) for held in self._read().values() for which in ("latest", "previous", SCRIPT_RUN)
                if held.get(which)]

    def new_run(self, tier: TestTier, commit: str, started_at: datetime) -> TestRun:
        """A run of tier on commit of this record's checkout, not yet kept."""
        return TestRun(tier, commit, started_at, checkout=str(self.checkout or ""))

    def save(self, run: TestRun) -> None:
        """Keep run as its tier's latest on this checkout; a different run held as latest becomes the previous one."""
        def as_latest(held: dict) -> None:
            latest = held.get("latest")
            if latest and self._as_run(latest).run_id != run.run_id:
                held["previous"] = latest
            held["latest"] = run.to_json()
        self._change(run.tier, as_latest)

    def save_script_run(self, run: TestRun) -> None:
        """Keep run as the tier scripts/test.ps1 runs in this checkout's own folder: live while its process runs, so
        the runner and the cadence wait for it, and never the tier's latest result, since it tests the folder's files as
        they stand, uncommitted edits too, not a commit."""
        self._change(run.tier, lambda held: held.update({SCRIPT_RUN: run.to_json()}))

    @contextlib.contextmanager
    def claimed(self) -> Iterator[bool]:
        """Hold the record against every other process for one look at what is due: True when this one holds it, False
        at once while another does. Each chat's health report asks, and two asking at once must not start the same tier
        twice. The operating system gives the claim back when the process holding it ends, however it ends, so a claim
        file a killed process left holds nothing. The saves a look makes are steps of its claim."""
        with self.lock:
            if not self._claim.try_claim():
                yield False
                return
            try:
                yield True
            finally:
                self._claim.release()

    @property
    def claim_wait(self) -> str:
        """What a process kept waiting by another's claim tells its reader: the file it waits for, and the process that
        holds it, which gives it back when it has looked, or when it ends."""
        return (f"waiting for {self._claim.path}, which process {self._claim.holder} holds while it looks at which tier is due; "
                "it is given back when that process has looked, or has ended")

    def log_path(self, tier: TestTier) -> Path:
        return self.folder / f"test-run-{tier.value}.log"

    def _key(self, tier: TestTier) -> str:
        """What the file keeps this checkout's runs of tier under."""
        return f"{tier.value}@{os.path.normcase(str(self.checkout))}" if self.checkout else tier.value

    def _held(self, runs: dict, tier: TestTier) -> dict:
        """This checkout's runs of tier; a file written before runs named their checkout keeps them under the tier
        alone, and the first checkout to save a run takes those as its own."""
        return runs.get(self._key(tier)) or runs.get(tier.value) or {}

    def _change(self, tier: TestTier, change: Callable[[dict], None]) -> None:
        """Make change to this checkout's runs of tier, holding the claim from the record's read to its write, so a
        change another process makes at the same time waits its turn and neither is lost."""
        with self.lock, self._claim.held():
            runs = self._read()
            held = dict(self._held(runs, tier))
            change(held)
            runs.pop(tier.value, None)
            runs[self._key(tier)] = held
            self._write(runs)

    def _run(self, tier: TestTier, which: str) -> TestRun | None:
        held = self._held(self._read(), tier).get(which)
        return self._as_run(held) if held else None

    def _as_run(self, held: object) -> TestRun:
        try:
            return TestRun.from_json(held)
        except (ValueError, KeyError, TypeError, AttributeError) as not_a_run:
            raise TestRunRecordUnreadable(self.path, held, f"one entry is no run ({not_a_run})") from not_a_run

    def _read(self) -> dict:
        """Each tier's runs as the file holds them; none before any run is kept."""
        try:
            text = self._while_busy(lambda: self.path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        try:
            runs = json.loads(text)
        except ValueError as not_json:
            raise TestRunRecordUnreadable(self.path, text, f"it is not JSON ({not_json})") from not_json
        if not isinstance(runs, dict) or not all(isinstance(held, dict) for held in runs.values()):
            raise TestRunRecordUnreadable(self.path, text, "it does not hold each tier's runs by name")
        return runs

    def _write(self, runs: dict) -> None:
        """Put the whole record in the file's place at once: written beside it, then moved over it, so a process
        reading at that moment gets the record before or the record after, never part of one."""
        self.folder.mkdir(parents=True, exist_ok=True)
        beside = self.path.with_name(f"{RECORD_FILE}.{os.getpid()}.writing")
        beside.write_text(json.dumps(runs, indent=2), encoding="utf-8")
        self._while_busy(lambda: os.replace(beside, self.path))

    def _while_busy(self, reach_file: Callable[[], str | None]) -> str | None:
        """What reach_file answers, tried again while Windows refuses the file because another process is putting a
        new record in its place."""
        deadline = time.monotonic() + RECORD_BUSY_SECONDS
        while True:
            try:
                return reach_file()
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(RECORD_BUSY_POLL_SECONDS)


# What the scheduled e2e run captures in its worktree, brought back to the checkout where its screens are reviewed.
CAPTURED_BY_RUN = Path(".sessions") / ScheduledReview.RELEASE


class RunWorktree:
    """The folder a run's tier works in: a detached git worktree of the checkout, holding the files of the commit the
    run records. The checkout's own folder goes on changing while a tier runs, so a tier run there tests whatever
    commit the folder has reached, under the name of the one it started on."""

    def __init__(self, record: TestRunRecord, run: TestRun) -> None:
        self._checkout = record.checkout
        self._commit = run.commit
        self.folder = record.folder / WORKTREES_FOLDER / run.tier.value
        self._git = Git(self._checkout)

    @contextlib.contextmanager
    def made(self) -> Iterator[Path]:
        """The worktree's folder while the tier runs, removed after; one a killed run left is removed first."""
        self._remove()
        self.folder.parent.mkdir(parents=True, exist_ok=True)
        self._git.run("worktree", "add", "--detach", str(self.folder), self._commit, timeout=WORKTREE_SECONDS)
        try:
            self._borrow_installed_packages()
            self._copy_installed_adapters()
            yield self.folder
        finally:
            self._bring_back_captures()
            # A file a process of the tier still holds keeps the folder; the next run removes it first, or fails naming it.
            with contextlib.suppress(OSError):
                self._remove()

    def _borrow_installed_packages(self) -> None:
        """Link each package.json's installed packages from the checkout, since git keeps none and a tier needs them."""
        for package in self._git.run("ls-files", "--", "*package.json").splitlines():
            installed = self._checkout / Path(package).parent / INSTALLED_PACKAGES
            borrowed = self.folder / Path(package).parent / INSTALLED_PACKAGES
            if Path(package).name == "package.json" and installed.is_dir() and borrowed.parent.is_dir():
                self._link(installed, borrowed)

    def _copy_installed_adapters(self) -> None:
        """Copy the language adapters the checkout's install wrote, which every app's page imports and git does not
        keep. They are copied, not linked: nothing then needs giving back before the worktree is removed, and a tier
        that writes among them, or a removal that goes wrong, cannot reach the person's own installed folder."""
        installed = self._checkout / INSTALLED_ADAPTERS
        if installed.is_dir():
            shutil.copytree(installed, self.folder / INSTALLED_ADAPTERS)

    def _link(self, installed: Path, borrowed: Path) -> None:
        if sys.platform == "win32":
            import _winapi

            _winapi.CreateJunction(str(installed), str(borrowed))
        else:
            os.symlink(installed, borrowed, target_is_directory=True)

    def _return_installed_packages(self) -> None:
        """Take every link to the checkout's installed packages away, so removing the worktree removes none of them."""
        for folder, names, _ in os.walk(self.folder):
            if INSTALLED_PACKAGES not in names:
                continue
            names.remove(INSTALLED_PACKAGES)
            borrowed = Path(folder) / INSTALLED_PACKAGES
            if borrowed.is_symlink() or borrowed.is_junction():
                os.rmdir(borrowed) if sys.platform == "win32" else borrowed.unlink()

    def _bring_back_captures(self) -> None:
        captured = self.folder / CAPTURED_BY_RUN
        if captured.is_dir():
            shutil.copytree(captured, self._checkout / CAPTURED_BY_RUN, dirs_exist_ok=True)

    def _remove(self) -> None:
        if self.folder.exists():
            self._return_installed_packages()
            if not self._git.succeeds("worktree", "remove", "--force", str(self.folder)):
                shutil.rmtree(self._reachable_beyond_path_limit(), onexc=self._removed_once_writable)
        self._git.succeeds("worktree", "prune")

    def _reachable_beyond_path_limit(self) -> Path:
        """The folder as Windows opens paths past 260 characters, which git checks out under core.longpaths and
        Windows otherwise refuses to remove."""
        if sys.platform != "win32" or str(self.folder).startswith("\\\\?\\"):
            return self.folder
        return Path("\\\\?\\" + str(self.folder.resolve()))

    def _removed_once_writable(self, remove: Callable[[str], None], path: str, error: BaseException) -> None:
        """Remove path again once it is writable: the install marks the folders of its language adapters read-only,
        and a copy keeps that, which Windows refuses to remove. A failure for another reason is raised as it was."""
        if not isinstance(error, PermissionError):
            raise error
        os.chmod(path, stat.S_IWRITE)
        remove(path)


class TestRunner:
    """The boundary to scripts/test.ps1 for one record's checkout: start a run in a background process that records
    its own result, or run one here and answer its exit code and output."""

    __test__ = False

    def __init__(self, record: TestRunRecord) -> None:
        self._record = record

    def start(self, run: TestRun) -> RunningProcess:
        """Start run in a process of its own, which outlives the cdd server and goes on with the run as recorded, and
        answer that process."""
        record, checkout = self._record, self._record.checkout
        record.folder.mkdir(parents=True, exist_ok=True)
        command = [PythonInterpreter().windowless, "-m", "harness.release.test_runs", run.tier.value, str(checkout), str(record.folder),
                   "--started", run.started]
        with record.log_path(run.tier).open("w", encoding="utf-8") as log:
            env = {**os.environ, "PYTHONPATH": str(Path(__file__).resolve().parents[2]), "PYTHONIOENCODING": "utf-8"}
            return BackgroundStart(log).run(command, checkout, env)

    def run(self, run: TestRun, env: dict[str, str] | None = None) -> tuple[int, str]:
        """Run the tier to its end on the files of the commit run records, its output going to this process's output
        as well; env adds variables. A run that records no commit, its checkout no git repository, works in the
        checkout's own folder."""
        worktree = RunWorktree(self._record, run).made() if run.commit else contextlib.nullcontext(self._record.checkout)
        with worktree as folder:
            return self._run_script(run.tier, folder, env)

    def _run_script(self, tier: TestTier, folder: Path, env: dict[str, str] | None) -> tuple[int, str]:
        command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(folder / TEST_SCRIPT), "-Suite", tier.value]
        # The run is recorded already, so test.ps1 does not record itself as a second run beside it.
        process = subprocess.Popen(command, cwd=folder, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                                   env={**os.environ, **(env or {}), RUN_RECORDED_VARIABLE: "1"})
        # Killing this process ends PowerShell and the specs it runs, so no tier goes on working after its run is gone.
        StarterBoundJob().take_in(process)
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


def _say(line: str) -> None:
    print(line, flush=True)


def _review_screens(checkout: Path, run_name: str) -> list[str]:
    return ScheduledReview(checkout, run_name).start()


class TestCadence:
    """Runs heavy every hour and e2e every day on the main checkout its record is of. Nothing keeps time: ``start_due``
    is called whenever the health report is read, and starts the overdue tier, one run at a time, e2e first since it is
    the one that runs least."""

    __test__ = False

    def __init__(self, record: TestRunRecord, runner: TestRunner | None = None, git: Git | None = None,
                 clock: Callable[[], datetime] = _utc_now, review: Callable[[Path, str], list[str]] | None = None,
                 wait: Callable[[float], None] = time.sleep, say: Callable[[str], None] = _say) -> None:
        self.record = record
        self.checkout = record.checkout
        self._wait = wait
        self._say = say
        self._runner = runner or TestRunner(record)
        self._git = git or (Git(self.checkout) if self.checkout else None)
        self._clock = clock
        self._review = review or _review_screens
        self._process = RunningProcess(os.getpid())

    @property
    def latest_runs(self) -> list[TestRun]:
        """The latest run of each tier that has run, a run whose process is gone read as abandoned."""
        runs = [self.record.latest(tier) for tier in TestTier]
        return [run.settled() for run in runs if run is not None]

    def due(self) -> list[TestTier]:
        """The tiers whose interval has passed since they last started, or that never ran; none while a run is live,
        on this checkout or another, held as its tier's latest run or as the previous one a later run was recorded over."""
        latest = {run.tier: run for run in self.latest_runs}
        if any(run.outcome is RunOutcome.RUNNING for run in latest.values()) or self._live_elsewhere():
            return []
        return [tier for tier in (TestTier.E2E, TestTier.HEAVY) if tier not in latest or latest[tier].is_due(self._clock())]

    def start_due(self) -> TestRun | None:
        """Start the first overdue tier on main in the background and record it as running; nothing when none is due or
        there is no main checkout."""
        if self.checkout is None:
            return None
        with self.record.claimed() as is_claimed:
            due = self.due() if is_claimed else []
            if not due:
                return None
            run = self.record.new_run(due[0], self._head(), self._clock())
            self.record.save(run)
            try:
                run.taken_by(self._runner.start(run))
            except OSError as not_started:
                run.not_started(not_started)
            self.record.save(run)
            return run

    def run_now(self, tier: TestTier, recorded_start: datetime | None = None) -> TestRun:
        """Run tier here to its end and record its result: the background process the cadence starts runs this, naming
        the run by when the cadence recorded it as started, and so can a person, naming none. The run so named is the
        one finished; otherwise a new one starts."""
        started = self._started(tier, recorded_start)
        if tier is TestTier.E2E:
            # Each browser story step is screenshotted into this run's folder under .sessions/scheduled/, then reviewed.
            run_name = started.folder_name
            exit_code, output = self._runner.run(started, {"E2E_RELEASE": ScheduledReview.RELEASE, "E2E_RUN": run_name})
            output += "".join(f"\nscreen review: {line}" for line in self._reviewed(run_name))
        else:
            exit_code, output = self._runner.run(started)
        with self._claim():
            finished = started.finished(exit_code, output, self.record.previous(tier), self._clock())
            self.record.save(finished)
        return finished

    def record_script_run(self, tier: TestTier, script: RunningProcess) -> TestRun:
        """Record scripts/test.ps1, run by a person or an agent in this checkout's own folder, as running tier in its
        process script, once no run is live on this checkout, so the runner and the cadence wait for it as for their
        own runs. Two runs of one checkout's tiers at once start its servers on the same ports and fail on each other."""
        def live_on_this_checkout() -> list[TestRun]:
            return [run for run in self._live_elsewhere() if run.is_on(self.checkout)]

        def recorded() -> TestRun:
            run = self.record.new_run(tier, "", self._clock()).taken_by(script)
            self.record.save_script_run(run)
            return run
        return self._once_none_live(live_on_this_checkout, recorded)

    def _started(self, tier: TestTier, recorded_start: datetime | None) -> TestRun:
        """The run this process goes on with, recorded under this process once no other process has a run live. The
        e2e tier's board specs all serve on one port, and every tier's specs load the one computer, so a second run
        started beside a live one fails on what the first holds, not on the code it tests."""
        return self._once_none_live(lambda: self._live_elsewhere(recorded_start), lambda: self._taken(tier, recorded_start))

    def _once_none_live(self, live_runs: Callable[[], list[TestRun]], record_run: Callable[[], TestRun]) -> TestRun:
        """The run record_run records once live_runs names no run, both under the record's claim; until then this says,
        each time it looks, which run it waits for."""
        while True:
            with self._claim():
                live = live_runs()
                if not live:
                    return record_run()
            self._say(f"waiting for the {live[0].tier.value} run process {live[0].pid} started at {live[0].started} to end; "
                      f"looking again every {WAIT_SECONDS} seconds")
            self._wait(WAIT_SECONDS)

    def _taken(self, tier: TestTier, recorded_start: datetime | None) -> TestRun:
        """The tier's run, recorded as this process's: the run the cadence recorded at recorded_start for the process it
        started, which started this one; else a new one on HEAD. A run another process left running, that process gone,
        is recorded as abandoned, not taken over: it gave no result, and a run of its own keeps both runs and how long
        each took."""
        run = self.record.latest(tier)
        if not self._is_recorded_for_this_process(run, recorded_start):
            if run is not None and run.outcome is RunOutcome.RUNNING:
                self.record.save(run.settled())
            run = self.record.new_run(tier, self._head(), self._clock())
        self.record.save(run.taken_by(self._process))
        return run

    def _is_recorded_for_this_process(self, run: TestRun | None, recorded_start: datetime | None) -> bool:
        """run is the one the cadence recorded as running at recorded_start, for the process it started to run it."""
        return run is not None and run.outcome is RunOutcome.RUNNING and recorded_start is not None and run.started_at == recorded_start

    @contextlib.contextmanager
    def _claim(self) -> Iterator[None]:
        """Hold the record's claim, saying what is waited for while another process holds it."""
        while True:
            with self.record.claimed() as is_claimed:
                if is_claimed:
                    yield
                    return
            self._say(self.record.claim_wait)
            self._wait(CLAIM_WAIT_SECONDS)

    def _live_elsewhere(self, recorded_start: datetime | None = None) -> list[TestRun]:
        """Every recorded run, of any tier and checkout, that another process runs now; a run recorded over a live one
        leaves it held as the previous run, so both are looked at. The run the cadence recorded at recorded_start
        names the process the cadence started, which runs this one: that run is this process's own."""
        return [run for run in self.record.runs
                if run.is_live and run.pid != self._process.pid and run.started_at != recorded_start]

    def _reviewed(self, run_name: str) -> list[str]:
        """The screen review of the e2e run just ended; a review that cannot start says why and leaves the run's result."""
        try:
            return self._review(self.checkout, run_name)
        except Exception as not_reviewed:  # the tests' result stands whatever the review does
            return [f"not started: {not_reviewed}"]

    def _head(self) -> str:
        try:
            return self._git.run("rev-parse", "HEAD") if self._git else ""
        except RepoConnectError:
            return ""


def main(argv: list[str] | None = None) -> int:
    """python -m harness.release.test_runs <tier> <checkout> <record folder>: run a tier and record its result. The
    cadence starts it this way in the background, with --started naming the run it recorded; the /release command runs
    it the same way. scripts/test.ps1 calls it with --script naming its own process, to be recorded as running."""
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("tier", choices=[tier.value for tier in TestTier])
    parser.add_argument("checkout")
    parser.add_argument("record", nargs="?", default="")
    parser.add_argument("--started", default="", help="when the cadence recorded the run this process goes on with")
    parser.add_argument("--script", type=int, default=0,
                        help="the scripts/test.ps1 process running the tier in the checkout's own folder: record it as running once "
                             "no run is live on the checkout, and end")
    arguments = parser.parse_args(argv)
    # Run from a console, the output is echoed in its code page, such as cp1252, which cannot write every character a
    # spec prints; one it cannot write is shown as ? rather than ending the run.
    sys.stdout.reconfigure(errors="replace")
    record = TestRunRecord(arguments.record or default_record_folder(), Path(arguments.checkout))
    recorded_start = datetime.fromisoformat(arguments.started) if arguments.started else None
    try:
        if arguments.script:
            run = TestCadence(record).record_script_run(TestTier(arguments.tier), RunningProcess(arguments.script))
            print(f"{run.tier.value} run by scripts/test.ps1 (process {run.pid}) recorded as running in {record.path}")
            return 0
        run = TestCadence(record).run_now(TestTier(arguments.tier), recorded_start)
    except TestRunRecordUnreadable as unreadable:
        print(f"{arguments.tier} not run: {unreadable}", file=sys.stderr)
        return 1
    print(f"{run.tier.value} {run.outcome.value} on {run.commit[:9]}")
    return 0 if run.outcome is RunOutcome.PASSED else 1


def default_record_folder() -> Path:
    """The cdd home, where the one cdd server keeps the record every chat's health report reads."""
    return CddHome().folder


if __name__ == "__main__":
    sys.exit(main())
