"""The server health report's part in the test cadence: reading it starts the overdue tier, and it holds the desktop
walk question the cadence asks before a timed e2e run."""
import shutil
import tempfile
from datetime import timedelta
from pathlib import Path

from expects import be_false, be_none, be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.diagnostics.server_health import ServerHealth
from harness.release.test_run_examples import NOON, Clock, GitStub, RunnerStub
from harness.release.test_runs import RunOutcome, TestCadence, TestRun, TestRunRecord, TestTier

# A process id that is never running.
GONE = 2 ** 22 + 7


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
