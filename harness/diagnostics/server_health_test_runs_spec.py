"""The server health report's part in the test cadence: reading it starts the overdue tier."""
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.diagnostics.server_health import ServerHealth
from harness.release.test_run_examples import NOON, Clock, GitStub, RunnerStub
from harness.release.test_runs import TestCadence, TestRunRecord, TestTier


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
