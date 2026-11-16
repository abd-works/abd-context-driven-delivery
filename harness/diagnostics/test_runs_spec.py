"""The slow tiers on a cadence: heavy every hour and e2e every day on main, started when the health report is read.

The test runner, git and the clock are faked at the boundary *TestCadence* reaches them through, so nothing here runs
scripts/test.ps1 or git. test_runs_heavy_spec.py runs the real runner and git."""
import os
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from expects import be_false, be_none, be_true, contain, equal, expect, have_len
from mamba import after, before, context, description, it

from harness.diagnostics.server_health import ServerHealth
from harness.diagnostics.test_runs import RunOutcome, TestCadence, TestRun, TestRunRecord, TestTier, main_checkout
from harness.git.git import RepoConnectError

NOON = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)
# A process id that is never running.
GONE = 2 ** 22 + 7


class RunnerStub:
    """scripts/test.ps1 as the cadence sees it: a start answers this process's id, so the run reads live, and a run
    ends with the exit code and output a spec gives it."""

    def __init__(self, exit_code: int = 0, output: str = "4 examples ran") -> None:
        self.exit_code = exit_code
        self.output = output
        self.started: list[TestTier] = []
        self.ran: list[TestTier] = []

    def start(self, tier, checkout, record) -> int:
        self.started.append(tier)
        return os.getpid()

    def run(self, tier, checkout) -> tuple[int, str]:
        self.ran.append(tier)
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


with description("the test cadence") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="test-runs-"))
        self.record = TestRunRecord(self.folder / "home")
        self.runner = RunnerStub()
        self.clock = Clock(NOON)
        self.cadence = TestCadence(self.folder, self.record, self.runner, GitStub(), self.clock)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    def ran_at(self, tier: TestTier, started: datetime, outcome: RunOutcome = RunOutcome.PASSED) -> None:
        self.record.save(TestRun(tier, "old", started, outcome, pid=GONE))

    with context("that no tier has run"):
        with it("should start e2e first, the tier that runs least"):
            expect(self.cadence.start_due().tier).to(equal(TestTier.E2E))

        with it("should record the run as running on main's commit"):
            self.cadence.start_due()
            run = self.record.latest(TestTier.E2E)
            expect((run.outcome, run.commit)).to(equal((RunOutcome.RUNNING, "abc123")))

        with it("should start one tier at a time"):
            self.cadence.start_due()
            self.cadence.start_due()
            expect(self.runner.started).to(equal([TestTier.E2E]))

    with context("that e2e ran this morning and heavy ran half an hour ago"):
        with before.each:
            self.ran_at(TestTier.E2E, NOON - timedelta(hours=3))
            self.ran_at(TestTier.HEAVY, NOON - timedelta(minutes=30))

        with it("should start nothing"):
            expect(self.cadence.start_due()).to(be_none)

    with context("that heavy last started an hour ago"):
        with before.each:
            self.ran_at(TestTier.E2E, NOON - timedelta(hours=3))
            self.ran_at(TestTier.HEAVY, NOON - timedelta(hours=1))

        with it("should start heavy"):
            expect(self.cadence.start_due().tier).to(equal(TestTier.HEAVY))

    with context("that e2e last started a day ago"):
        with before.each:
            self.ran_at(TestTier.E2E, NOON - timedelta(days=1))
            self.ran_at(TestTier.HEAVY, NOON - timedelta(minutes=5))

        with it("should start e2e"):
            expect(self.cadence.start_due().tier).to(equal(TestTier.E2E))

    with context("that a run is recorded as running"):
        with it("should start nothing while its process runs"):
            self.record.save(TestRun(TestTier.HEAVY, "old", NOON - timedelta(hours=2), pid=os.getpid()))
            expect(self.cadence.start_due()).to(be_none)

        with it("should read as abandoned once its process is gone"):
            self.record.save(TestRun(TestTier.HEAVY, "old", NOON - timedelta(hours=2), pid=GONE))
            expect(self.cadence.latest_runs[0].state).to(equal("abandoned"))

    with context("that another process is looking at what is due"):
        with it("should start nothing"):
            self.record.folder.mkdir(parents=True)
            (self.record.folder / "test-runs.claim").write_text("", encoding="utf-8")
            expect(self.cadence.start_due()).to(be_none)

    with context("whose run will not start"):
        with before.each:
            def refuse(*_):
                raise PermissionError(5, "Access is denied")
            self.runner.start = refuse
            self.cadence.start_due()

        with it("should record it abandoned, saying why"):
            expect(self.cadence.latest_runs[0].summary).to(contain("Access is denied"))

        with it("should start it again on the next look"):
            self.runner.start = lambda *_: os.getpid()
            expect(self.cadence.start_due().tier).to(equal(TestTier.E2E))

    with context("with no main checkout"):
        with it("should start nothing"):
            cadence = TestCadence(None, self.record, self.runner, GitStub(), self.clock)
            expect(cadence.start_due()).to(be_none)

    with context("run to its end"):
        with it("should record a pass"):
            expect(self.cadence.run_now(TestTier.HEAVY).state).to(equal("passed"))

        with it("should finish the run the cadence started, not a new one"):
            started = self.cadence.start_due()
            self.clock.now = NOON + timedelta(minutes=20)
            expect(self.cadence.run_now(TestTier.E2E).run_id).to(equal(started.run_id))

        with it("should record HEAD, not take over a run left running on another commit"):
            self.record.save(TestRun(TestTier.E2E, "old", NOON - timedelta(hours=1), pid=GONE))
            expect(self.cadence.run_now(TestTier.E2E).commit).to(equal("abc123"))

        with it("should keep the last lines the run printed"):
            self.runner.output = "\n".join(f"line {number}" for number in range(40))
            expect(self.cadence.run_now(TestTier.HEAVY).summary.splitlines()).to(have_len(12))

    with context("that fails after a run that passed"):
        with before.each:
            self.ran_at(TestTier.HEAVY, NOON - timedelta(hours=1))
            self.runner.exit_code = 1

        with it("should be a new failure"):
            expect(self.cadence.run_now(TestTier.HEAVY).is_new_failure).to(be_true)

    with context("that fails after a run that failed"):
        with before.each:
            self.ran_at(TestTier.HEAVY, NOON - timedelta(hours=1), RunOutcome.FAILED)
            self.runner.exit_code = 1

        with it("should not be a new failure"):
            expect(self.cadence.run_now(TestTier.HEAVY).is_new_failure).to(be_false)


with description("the main checkout the cadence runs in") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="main-checkout-"))
        (self.folder / "scripts").mkdir()
        (self.folder / "scripts" / "test.ps1").write_text("exit 0", encoding="utf-8")

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    def listing(self, branch: str) -> str:
        return f"worktree {self.folder.as_posix()}\nHEAD abc\nbranch refs/heads/{branch}\n\nworktree C:/elsewhere\nbranch refs/heads/x\n"

    with context("that has main checked out"):
        with it("should be the repository's own folder"):
            expect(main_checkout(self.folder, GitStub(self.listing("main")))).to(equal(Path(self.folder.as_posix())))

    with context("that has another branch checked out"):
        with it("should be none"):
            expect(main_checkout(self.folder, GitStub(self.listing("release-cadence")))).to(be_none)

    with context("that is no CDD checkout"):
        with it("should be none"):
            (self.folder / "scripts" / "test.ps1").unlink()
            expect(main_checkout(self.folder, GitStub(self.listing("main")))).to(be_none)


with description("the server health report's test runs") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="health-runs-"))
        self.record = TestRunRecord(self.folder)
        self.runner = RunnerStub()
        cadence = TestCadence(self.folder, self.record, self.runner, GitStub(), Clock(NOON))
        self.health = ServerHealth(self.folder, hook_daemon=object(), cadence=cadence)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("read"):
        with it("should start the overdue tier"):
            self.health.report()
            expect(self.runner.started).to(contain(TestTier.E2E))

        with it("should list the run it started"):
            expect([run.name for run in self.health.report().test_runs]).to(equal(["e2e"]))
