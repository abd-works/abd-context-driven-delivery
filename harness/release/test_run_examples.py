"""The test runner, git, and the clock as the test cadence reaches them, faked at that boundary for the specs of the
cadence and of the server health report that starts it."""
import os
from datetime import datetime, timezone

from harness.git.git import RepoConnectError
from harness.process.process import RunningProcess
from harness.release.test_runs import TestRun, TestRunRecord, TestTier

NOON = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)
THIS_PROCESS = RunningProcess(os.getpid())


class RunnerStub:
    """scripts/test.ps1 as the cadence sees it: a start answers this process, so the run reads live, and a run ends
    with the exit code and output a spec gives it, having looked at the record as it stood while the tier ran."""

    def __init__(self, record: TestRunRecord, exit_code: int = 0, output: str = "4 examples ran\n\n3/3 files passed") -> None:
        self.record = record
        self.exit_code = exit_code
        self.output = output
        self.started: list[TestTier] = []
        self.ran: list[TestTier] = []
        self.runs: list[TestRun] = []
        self.recorded_while_running: TestRun | None = None

    def start(self, run: TestRun) -> RunningProcess:
        self.started.append(run.tier)
        return THIS_PROCESS

    def run(self, run: TestRun, env=None) -> tuple[int, str]:
        self.ran.append(run.tier)
        self.runs.append(run)
        self.env = env or {}
        self.recorded_while_running = self.record.latest(run.tier)
        return self.exit_code, self.output


class GitStub:
    def __init__(self, listing: str = "", head: str = "abc123") -> None:
        self.listing = listing
        self.head = head

    def run(self, *args: str, **_: object) -> str:
        if args[0] == "worktree":
            if not self.listing:
                raise RepoConnectError("Cannot connect git: not a git repository.")
            return self.listing
        return self.head


class Clock:
    def __init__(self, now: datetime) -> None:
        self.now = now

    def __call__(self) -> datetime:
        return self.now
