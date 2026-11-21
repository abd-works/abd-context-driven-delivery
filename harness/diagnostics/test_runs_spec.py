"""The slow tiers on a cadence: heavy every hour and e2e every day on main, started when the health report is read.

The test runner, git and the clock are faked at the boundary *TestCadence* reaches them through, so nothing here runs
scripts/test.ps1 or git. test_runs_heavy_spec.py runs the real runner, git and processes."""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from expects import be_false, be_none, be_true, contain, equal, expect, have_len, raise_error
from mamba import after, before, context, description, it

from harness.diagnostics.server_health import ServerHealth
from harness.diagnostics.test_runs import RunOutcome, TestCadence, TestRun, TestRunRecord, TestRunRecordUnreadable, TestTier, main_checkout
from harness.git.git import RepoConnectError
from harness.process.process import RunningProcess

NOON = datetime(2026, 11, 15, 12, 0, tzinfo=timezone.utc)
# A process id that is never running.
GONE = 2 ** 22 + 7
# A live process that is neither this one nor its parent, as a run another process started is; it ends with the spec.
ANOTHER_PROCESS = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(600)"], stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
atexit.register(ANOTHER_PROCESS.kill)
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


with description("the test cadence") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="test-runs-"))
        self.record = TestRunRecord(self.folder / "home", self.folder)
        self.runner = RunnerStub(self.record)
        self.clock = Clock(NOON)
        self.reviewed = []
        self.review_lines = ["move-work-forward-on-session-board/maintain-tickets: 3 changed step(s)", "review agent started on 1 run(s)"]
        self.waits = []
        self.said = []
        self.claim = self.record.folder / "test-runs.claim"
        self.cadence = TestCadence(self.record, self.runner, GitStub(), self.clock, review=self.review, wait=self.wait, say=self.said.append)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    def review(self, checkout: Path, run_name: str) -> list[str]:
        self.reviewed.append(run_name)
        if isinstance(self.review_lines, Exception):
            raise self.review_lines
        return self.review_lines

    def wait(self, seconds: float) -> None:
        """While run_now waits, the other process releases its claim, its run ends, and a run after it ends too, so
        neither the latest nor the previous run of a tier is live; what had run here by then is kept for the spec."""
        self.waits.append(list(self.runner.ran))
        self.claim.unlink(missing_ok=True)
        for tier in TestTier:
            for minutes in (3, 4):
                self.record.save(TestRun(tier, "abc123", NOON - timedelta(minutes=minutes), RunOutcome.FAILED, pid=GONE))

    def running_elsewhere(self, tier: TestTier) -> TestRun:
        """A run of tier another live process holds, one this spec started that runs until the spec ends."""
        run = TestRun(tier, "abc123", NOON - timedelta(minutes=2)).taken_by(RunningProcess(ANOTHER_PROCESS.pid))
        self.record.save(run)
        return run

    def held_claim(self, age_seconds: float = 0) -> None:
        """The claim another process holds, taken age_seconds ago; a negative age dates it ahead of the clock."""
        self.record.folder.mkdir(parents=True, exist_ok=True)
        self.claim.write_text("", encoding="utf-8")
        os.utime(self.claim, (time.time() - age_seconds,) * 2)

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
            self.record.save(TestRun(TestTier.HEAVY, "old", NOON - timedelta(hours=2)).taken_by(THIS_PROCESS))
            expect(self.cadence.start_due()).to(be_none)

        with it("should start nothing while a run recorded over it was abandoned, its own process still running"):
            self.running_elsewhere(TestTier.E2E)
            self.record.save(TestRun(TestTier.E2E, "abc123", NOON - timedelta(minutes=1), RunOutcome.RUNNING, pid=GONE))
            expect(self.cadence.start_due()).to(be_none)

        with it("should read as abandoned once its process is gone"):
            self.record.save(TestRun(TestTier.HEAVY, "old", NOON - timedelta(hours=2), pid=GONE))
            expect(self.cadence.latest_runs[0].state).to(equal("abandoned"))

        with context("under a process id another program now has"):
            with before.each:
                # The record names the run's process by its id and when it started; the program that has the id now started later.
                self.record.save(TestRun(TestTier.HEAVY, "old", NOON - timedelta(days=9), pid=ANOTHER_PROCESS.pid, process_started=NOON - timedelta(days=9)))
                self.record.save(TestRun(TestTier.E2E, "old", NOON - timedelta(minutes=5), RunOutcome.PASSED))

            with it("should read as abandoned"):
                expect(self.cadence.latest_runs[0].state).to(equal("abandoned"))

            with it("should have its tier started again"):
                expect(self.cadence.start_due().tier).to(equal(TestTier.HEAVY))

            with it("should not keep a run by hand waiting"):
                self.cadence.run_now(TestTier.HEAVY)
                expect(self.waits).to(equal([]))

        with context("by a file kept before runs named when their process started"):
            with it("should read as abandoned, whatever process has its id now"):
                self.record.save(TestRun(TestTier.HEAVY, "old", NOON - timedelta(hours=2), pid=ANOTHER_PROCESS.pid))
                expect(self.cadence.latest_runs[0].state).to(equal("abandoned"))

    with context("that another checkout's run is live"):
        with it("should start nothing"):
            run = TestRun(TestTier.HEAVY, "def456", NOON - timedelta(minutes=2)).taken_by(RunningProcess(ANOTHER_PROCESS.pid))
            TestRunRecord(self.record.folder, self.folder / "another-checkout").save(run)
            expect(self.cadence.start_due()).to(be_none)

    with context("that another process is looking at what is due"):
        with it("should start nothing"):
            self.held_claim()
            expect(self.cadence.start_due()).to(be_none)

        with it("should say, to a run by hand, which file it waits for and how long until it takes it over"):
            self.held_claim(age_seconds=20)
            self.cadence.run_now(TestTier.HEAVY)
            expect(self.said[0]).to(contain(str(self.claim), "taken over in 40 seconds"))

        with it("should then run the tier"):
            self.held_claim()
            self.cadence.run_now(TestTier.HEAVY)
            expect(self.runner.ran).to(equal([TestTier.HEAVY]))

    with context("that a process left its claim behind, dated ahead of the clock"):
        with it("should take the claim over and start the tier that is due"):
            self.held_claim(age_seconds=-3600)
            expect(self.cadence.start_due().tier).to(equal(TestTier.E2E))

    with context("whose run will not start"):
        with before.each:
            def refuse(*_):
                raise PermissionError(5, "Access is denied")
            self.runner.start = refuse
            self.cadence.start_due()

        with it("should record it abandoned, saying why"):
            expect(self.cadence.latest_runs[0].summary).to(contain("Access is denied"))

        with it("should start it again on the next look"):
            self.runner.start = lambda *_: THIS_PROCESS
            expect(self.cadence.start_due().tier).to(equal(TestTier.E2E))

    with context("with no main checkout"):
        with it("should start nothing"):
            cadence = TestCadence(TestRunRecord(self.record.folder), self.runner, GitStub(), self.clock)
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

        with it("should run the tier on the commit it records"):
            self.cadence.run_now(TestTier.HEAVY)
            expect(self.runner.runs[0].commit).to(equal("abc123"))

        with it("should record which checkout it ran on"):
            expect(self.cadence.run_now(TestTier.HEAVY).checkout).to(equal(str(self.folder.resolve())))

        with it("should record the process that runs it while it runs"):
            self.cadence.run_now(TestTier.HEAVY)
            expect(self.runner.recorded_while_running.is_live).to(be_true)

        with it("should keep the last lines the run printed"):
            self.runner.output = "\n".join(f"line {number}" for number in range(40))
            expect(self.cadence.run_now(TestTier.HEAVY).summary.splitlines()).to(have_len(12))

    with context("that another process is running the same tier"):
        # Two e2e runs of one checkout both start the board's Playwright server on its one port, and the second fails.
        with before.each:
            self.running_elsewhere(TestTier.E2E)

        with it("should run nothing until that run ends"):
            self.cadence.run_now(TestTier.E2E)
            expect(self.waits[0]).to(equal([]))

        with it("should then run the tier itself"):
            self.cadence.run_now(TestTier.E2E)
            expect(self.runner.ran).to(equal([TestTier.E2E]))

        with it("should record its own run, not take over the other process's"):
            expect(self.cadence.run_now(TestTier.E2E).started_at).to(equal(NOON))

    with context("that another process is running the other tier"):
        with it("should run nothing until that run ends"):
            self.running_elsewhere(TestTier.HEAVY)
            self.cadence.run_now(TestTier.E2E)
            expect(self.waits[0]).to(equal([]))

    with context("whose live run is held as the previous one, a later run recorded over it"):
        with it("should run nothing until that run ends"):
            self.running_elsewhere(TestTier.E2E)
            self.record.save(TestRun(TestTier.E2E, "abc123", NOON - timedelta(minutes=1), RunOutcome.FAILED, pid=GONE))
            self.cadence.run_now(TestTier.E2E)
            expect(self.waits[0]).to(equal([]))

    with context("with no other run live"):
        with it("should not wait"):
            self.cadence.run_now(TestTier.E2E)
            expect(self.waits).to(equal([]))

    with context("that the cadence recorded under the process it started, which started this one"):
        with before.each:
            self.ran_at(TestTier.E2E, NOON - timedelta(days=2), RunOutcome.FAILED)
            self.recorded = TestRun(TestTier.E2E, "abc123", NOON - timedelta(seconds=1)).taken_by(RunningProcess(ANOTHER_PROCESS.pid))
            self.record.save(self.recorded)

        with it("should not wait for itself"):
            self.cadence.run_now(TestTier.E2E, self.recorded.started_at)
            expect(self.waits).to(equal([]))

        with it("should finish that run, not record a second"):
            expect(self.cadence.run_now(TestTier.E2E, self.recorded.started_at).run_id).to(equal(self.recorded.run_id))

        with it("should record this process as the one that runs it"):
            self.cadence.run_now(TestTier.E2E, self.recorded.started_at)
            expect(self.runner.recorded_while_running.pid).to(equal(os.getpid()))

        with it("should keep the run before it as the previous one"):
            self.cadence.run_now(TestTier.E2E, self.recorded.started_at)
            expect(self.record.previous(TestTier.E2E).state).to(equal("failed"))

    with context("that a process that ended left running on this commit"):
        with before.each:
            self.left = TestRun(TestTier.HEAVY, "abc123", NOON - timedelta(minutes=10), pid=GONE, process_started=NOON - timedelta(minutes=10))
            self.record.save(self.left)

        with it("should go on with that run"):
            expect(self.cadence.run_now(TestTier.HEAVY).run_id).to(equal(self.left.run_id))

        with it("should read as running to the cadence while this process runs it"):
            self.cadence.run_now(TestTier.HEAVY)
            expect(self.runner.recorded_while_running.is_live).to(be_true)

    with context("of the e2e tier"):
        with it("should screenshot its steps under the scheduled release"):
            self.cadence.run_now(TestTier.E2E)
            expect(self.runner.env["E2E_RELEASE"]).to(equal("scheduled"))

        with it("should name the run's screenshot folder after when it started"):
            self.cadence.run_now(TestTier.E2E)
            expect(self.runner.env["E2E_RUN"]).to(equal("run-2026-11-15-12-00-00"))

        with it("should review the run's screens once its tests end"):
            self.cadence.run_now(TestTier.E2E)
            expect(self.reviewed).to(equal(["run-2026-11-15-12-00-00"]))

        with it("should keep what the screen review did in the run's summary"):
            expect(self.cadence.run_now(TestTier.E2E).summary).to(contain("screen review: review agent started on 1 run(s)"))

        with context("with a screen review that cannot start"):
            with it("should keep the tests' result"):
                self.review_lines = RuntimeError("npx is not on PATH")
                expect(self.cadence.run_now(TestTier.E2E).state).to(equal("passed"))

            with it("should say in the run's summary why the review did not start"):
                self.review_lines = RuntimeError("npx is not on PATH")
                expect(self.cadence.run_now(TestTier.E2E).summary).to(contain("screen review: not started: npx is not on PATH"))

    with context("of the heavy tier"):
        with it("should not review screens"):
            self.cadence.run_now(TestTier.HEAVY)
            expect(self.reviewed).to(equal([]))

    with context("that test.ps1 cut short before counting its files"):
        with before.each:
            # What test.ps1 printed when a held timing file ended its run after one spec, exiting 0.
            self.runner.output = "End-to-end spec (1)\nSet-Content : The process cannot access the file\n\n0/ files passed"

        with it("should record a failure, though the run exited 0"):
            expect(self.cadence.run_now(TestTier.E2E).state).to(equal("failed"))

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
        self.record = TestRunRecord(self.folder, self.folder)
        self.runner = RunnerStub(self.record)
        cadence = TestCadence(self.record, self.runner, GitStub(), Clock(NOON))
        self.health = ServerHealth(self.folder, cadence=cadence)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("read"):
        with it("should start the overdue tier"):
            self.health.report()
            expect(self.runner.started).to(contain(TestTier.E2E))

        with it("should list the run it started"):
            expect([run.name for run in self.health.report().test_runs]).to(equal(["e2e"]))


with description("the record of test runs") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="test-runs-record-"))
        self.record = TestRunRecord(self.folder, self.folder / "main")
        self.failed = TestRun(TestTier.HEAVY, "abc123", NOON - timedelta(hours=1), RunOutcome.FAILED)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    def holding(self, text: str) -> TestRunRecord:
        self.record.path.write_text(text, encoding="utf-8")
        return self.record

    def run_json(self, **changed: object) -> str:
        """The file with one heavy run, some of its values changed."""
        return json.dumps({"heavy": {"latest": {**self.failed.to_json(), **changed}}})

    def refuses(self, text: str) -> None:
        expect(lambda: self.holding(text).latest(TestTier.HEAVY)).to(raise_error(TestRunRecordUnreadable, contain(str(self.record.path))))

    with context("with no file yet"):
        with it("should hold no run"):
            expect(self.record.latest(TestTier.HEAVY)).to(be_none)

    with context("that a run is saved to"):
        with before.each:
            self.record.save(self.failed)

        with it("should hold it as its tier's latest"):
            expect(self.record.latest(TestTier.HEAVY).run_id).to(equal(self.failed.run_id))

        with it("should leave nothing beside its file"):
            expect([file.name for file in self.folder.iterdir()]).to(equal(["test-runs.json"]))

        with context("and then another checkout's run of the same tier"):
            with before.each:
                other = TestRunRecord(self.folder, self.folder / "ticket-worktree")
                other.save(other.new_run(TestTier.HEAVY, "def456", NOON).finished(0, "1/1 files passed", None, NOON))

            with it("should keep the first checkout's latest run"):
                expect(self.record.latest(TestTier.HEAVY).state).to(equal("failed"))

            with it("should hold both among every run"):
                expect(sorted(run.commit for run in self.record.runs)).to(equal(["abc123", "def456"]))

    with context("kept before runs named their checkout"):
        with before.each:
            self.holding(self.run_json())

        with it("should read that run as this checkout's latest"):
            expect(self.record.latest(TestTier.HEAVY).state).to(equal("failed"))

        with it("should keep it as the previous run once a run is saved"):
            self.record.save(self.record.new_run(TestTier.HEAVY, "def456", NOON))
            expect(self.record.previous(TestTier.HEAVY).run_id).to(equal(self.failed.run_id))

    with context("whose file holds something that is no record"):
        with it("should refuse a file cut short, naming it"):
            self.refuses(self.run_json()[:60])

        with it("should refuse an empty file"):
            self.refuses("")

        with it("should refuse a list where its tiers belong"):
            self.refuses("[]")

        with it("should refuse text where a tier's runs belong"):
            self.refuses('{"heavy": "x"}')

        with it("should refuse an outcome no run has"):
            self.refuses(self.run_json(outcome="done"))

        with it("should refuse a start that is no time"):
            self.refuses(self.run_json(started_at="yesterday"))

        with it("should refuse a start with no UTC offset"):
            self.refuses(self.run_json(started_at="2026-11-19T10:00:00"))

        with it("should refuse a process id that is no number"):
            self.refuses(self.run_json(pid="abc"))

        with it("should carry what it could not read"):
            expect(lambda: self.holding("[]").latest(TestTier.HEAVY)).to(raise_error(TestRunRecordUnreadable, contain("'[]'")))

        with it("should refuse to save a run over it"):
            expect(lambda: self.holding("[]").save(self.failed)).to(raise_error(TestRunRecordUnreadable))

        with it("should leave the file as it is"):
            try:
                self.holding("[]").save(self.failed)
            except TestRunRecordUnreadable:
                pass
            expect(self.record.path.read_text(encoding="utf-8")).to(equal("[]"))


with description("the desktop walk question the cadence asks before a timed e2e run") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="walk-question-"))
        self.record = TestRunRecord(self.folder / "home", self.folder)
        self.runner = RunnerStub(self.record)
        self.clock = Clock(NOON)
        self.cadence = TestCadence(self.record, self.runner, GitStub(), self.clock, review=lambda checkout, run_name: [])
        self.health = ServerHealth(self.folder, cadence=self.cadence)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    def write_desktop_story_test(self) -> None:
        file = self.folder / "story_tests" / "move-work-forward-from-chat-bar" / "see-work-in-chat-bar" / "display_stage_strip_story.desktop.md"
        file.parent.mkdir(parents=True)
        file.write_text("## Story: Display Stage Strip\n", encoding="utf-8")

    with context("in a checkout with no desktop story test"):
        with it("should ask nothing"):
            self.cadence.start_due()
            expect(self.health.desktop_walk_question).to(be_none)

    with context("in a checkout with a desktop story test"):
        with before.each:
            self.write_desktop_story_test()

        with context("that starts the e2e tier on its timer"):
            with before.each:
                self.run = self.cadence.start_due()
                self.question = self.health.desktop_walk_question

            with it("should start the e2e tier without waiting for an answer"):
                expect(self.runner.started).to(equal([TestTier.E2E]))

            with it("should ask the person whether to run the desktop walk now"):
                expect(self.question.message).to(contain("The desktop walk takes over your screen and keyboard"))

            with it("should say about how long the walk takes"):
                expect(self.question.message).to(contain("about 3 minutes"))

            with it("should name the command a yes sends to the chat"):
                expect(self.question.command).to(equal("/desktop-walk"))

            with context("and the person says yes"):
                with before.each:
                    self.starts_walk = self.health.answer_desktop_walk(self.question.run_id, True)

                with it("should have the chat that asked start the walk"):
                    expect(self.starts_walk).to(be_true)

                with it("should ask no more"):
                    expect(self.health.desktop_walk_question).to(be_none)

                with it("should record on the e2e run that the person said yes"):
                    expect(self.cadence.run_now(TestTier.E2E, self.run.started_at).summary).to(contain("desktop walk: the person said yes"))

                with it("should not have a chat that answers after start a second walk"):
                    expect(self.health.answer_desktop_walk(self.question.run_id, True)).to(be_false)

            with context("and the person says no"):
                with before.each:
                    self.starts_walk = self.health.answer_desktop_walk(self.question.run_id, False)

                with it("should start no walk"):
                    expect(self.starts_walk).to(be_false)

                with it("should record on the e2e run that the walk was not run"):
                    expect(self.cadence.run_now(TestTier.E2E, self.run.started_at).summary).to(contain("desktop walk: not run, the person said no"))

            with context("and nobody answers"):
                with it("should stop asking after ten minutes"):
                    self.clock.now = NOON + timedelta(minutes=11)
                    expect(self.health.desktop_walk_question).to(be_none)

                with it("should record on the e2e run that the walk was not run"):
                    expect(self.cadence.run_now(TestTier.E2E, self.run.started_at).summary).to(contain("desktop walk: not run, nobody answered"))

                with it("should start no walk for a yes that comes after the run has ended"):
                    self.cadence.run_now(TestTier.E2E, self.run.started_at)
                    expect(self.health.answer_desktop_walk(self.question.run_id, True)).to(be_false)

        with context("that starts the heavy tier on its timer"):
            with it("should ask nothing"):
                self.record.save(TestRun(TestTier.E2E, "abc123", NOON - timedelta(minutes=30), RunOutcome.PASSED, pid=GONE))
                self.cadence.start_due()
                expect(self.health.desktop_walk_question).to(be_none)

        with context("whose e2e tier a person runs by hand"):
            with it("should ask nothing"):
                self.cadence.run_now(TestTier.E2E)
                expect(self.health.desktop_walk_question).to(be_none)

            with it("should say nothing of the desktop walk on the run"):
                expect("desktop walk" in self.cadence.run_now(TestTier.E2E).summary).to(be_false)
