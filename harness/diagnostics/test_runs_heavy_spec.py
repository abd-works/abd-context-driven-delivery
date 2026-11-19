"""A tier run and its record over their real boundaries: real git in a throwaway repository, PowerShell running a
stand-in scripts/test.ps1 the repository commits, real processes started and killed, and two processes on one
test-runs.json. test_runs_spec.py holds the stubbed twins.

Each run is started as a person or the cadence starts it, `python -m harness.diagnostics.test_runs <tier> <checkout>
<record folder>`, and the record is read as the file holds it."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect
from mamba import after, before, context, description, it

from harness.diagnostics.test_runs import RunOutcome, TestCadence, TestRun, TestRunRecord, TestTier
from harness.git.git import Git
from harness.process.process import RunningProcess

REPOSITORY = Path(__file__).resolve().parents[2]
# The stand-in tier: it names its own process and folder, works for as long as the spec asks, and ends as test.ps1 does.
STAND_IN_TEST_SCRIPT = """param([string]$Suite)
if ($env:RUN_PID_FILE) { Set-Content -Path $env:RUN_PID_FILE -Value $PID }
Start-Sleep -Seconds ([int]$env:RUN_SECONDS)
Write-Host "HEAD $(git -C $PSScriptRoot rev-parse HEAD)"
Write-Host "moved $(Test-Path (Join-Path $PSScriptRoot '..\\moved.txt'))"
Write-Host "packages $(Test-Path (Join-Path $PSScriptRoot '..\\app\\node_modules\\installed.txt'))"
if ($env:RUN_CAPTURES -eq "1") {
    $captures = Join-Path $PSScriptRoot '..\\.sessions\\scheduled\\e2e-test-results\\run-1'
    New-Item -ItemType Directory -Force $captures | Out-Null
    Set-Content -Path (Join-Path $captures 'step.txt') -Value 'a captured screen'
}
if ($env:RUN_EXIT -eq "1") { Write-Host "0/1 files passed"; exit 1 }
Write-Host "1/1 files passed"
exit 0
"""
# How long a started run has to record itself, and a stand-in tier of no seconds to end.
SOON_SECONDS = 60
# How long Windows has to end a killed run's processes.
ENDED_SECONDS = 15


def git(folder: Path, *args: str) -> str:
    return Git(folder).run(*args)


def until(holds, seconds: float) -> bool:
    """Whether holds came true within seconds."""
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if holds():
            return True
        time.sleep(0.2)
    return bool(holds())


with description("a tier run") as self:
    with before.each:
        self.started = []
        self.root = Path(tempfile.mkdtemp(prefix="test-runs-heavy-"))
        self.checkout = self.repository("checkout")
        self.home = self.root / "home"
        self.home.mkdir()
        self.file = self.home / "test-runs.json"

    with after.each:
        for process in self.started:
            if process.poll() is None:
                process.kill()
        shutil.rmtree(self.root, ignore_errors=True)

    def repository(self, name: str) -> Path:
        """A repository on main that commits the stand-in scripts/test.ps1 and an app's package.json, with the app's
        packages installed beside it as npm leaves them, kept out of git."""
        folder = self.root / name
        subprocess.run(["git", "init", "-q", "-b", "main", str(folder)], check=True)
        for setting in (("user.name", "Spec"), ("user.email", "spec@example.invalid"), ("commit.gpgsign", "false")):
            git(folder, "config", *setting)
        (folder / "scripts").mkdir()
        (folder / "scripts" / "test.ps1").write_text(STAND_IN_TEST_SCRIPT, encoding="utf-8")
        (folder / "app" / "node_modules").mkdir(parents=True)
        (folder / "app" / "package.json").write_text("{}", encoding="utf-8")
        (folder / ".gitignore").write_text("node_modules/\n", encoding="utf-8")
        git(folder, "add", "scripts", "app/package.json", ".gitignore")
        git(folder, "commit", "-q", "-m", "The stand-in tier")
        (folder / "app" / "node_modules" / "installed.txt").write_text("a package npm installed", encoding="utf-8")
        return folder

    def start(self, seconds: int = 0, checkout: Path | None = None, exit_code: int = 0, captures: bool = False) -> subprocess.Popen:
        """A run of the heavy tier started by hand, its stand-in tier working for seconds."""
        self.pid_file = self.root / f"tier-{len(self.started)}.pid"
        env = {**os.environ, "PYTHONPATH": str(REPOSITORY), "PYTHONIOENCODING": "utf-8", "RUN_SECONDS": str(seconds),
               "RUN_EXIT": str(exit_code), "RUN_PID_FILE": str(self.pid_file), "RUN_CAPTURES": str(int(captures))}
        process = subprocess.Popen([sys.executable, "-m", "harness.diagnostics.test_runs", "heavy", str(checkout or self.checkout), str(self.home)],
                                   cwd=self.root, env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, encoding="utf-8", errors="replace")
        self.started.append(process)
        return process

    def ended(self, process: subprocess.Popen, seconds: float = SOON_SECONDS) -> str:
        """What process printed by its end; it is killed when it has not ended within seconds."""
        try:
            return process.communicate(timeout=seconds)[0]
        except subprocess.TimeoutExpired:
            process.kill()
            return "NOT ENDED: " + process.communicate()[0]

    def recorded(self, which: str = "latest") -> dict:
        """The heavy run the file holds, as written; empty before one is."""
        try:
            runs = json.loads(self.file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return next((held.get(which) or {} for key, held in runs.items() if key.split("@")[0] == "heavy"), {})

    def tier_process(self) -> RunningProcess:
        """The PowerShell process the latest started run's stand-in tier runs in."""
        until(lambda: self.pid_file.is_file() and self.pid_file.read_text(encoding="utf-8").strip(), SOON_SECONDS)
        return RunningProcess(int(self.pid_file.read_text(encoding="utf-8").strip()))

    def killed_while_its_tier_works(self) -> RunningProcess:
        """A run killed as stopping its command in a chat kills it, by the process id it recorded; answers its tier's process."""
        first = self.start(seconds=40)
        tier = self.tier_process()
        subprocess.run(["taskkill", "/F", "/PID", str(self.recorded()["pid"])], capture_output=True, check=False)
        first.kill()
        return tier

    with context("that is recorded as running under a process id another program now has"):
        with before.each:
            self.other_program = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(120)"], stdin=subprocess.DEVNULL)
            self.started.append(self.other_program)
            nine_days_ago = (datetime.now(timezone.utc) - timedelta(days=9)).isoformat()
            self.file.write_text(json.dumps({"heavy": {"latest": {"tier": "heavy", "outcome": "running", "pid": self.other_program.pid,
                                                                    "commit": "z", "started_at": nine_days_ago}}}), encoding="utf-8")

        with it("should not keep a run by hand waiting"):
            expect(self.ended(self.start())).to(contain("heavy passed on"))

    with context("that is killed while its tier works"):
        with it("should end its test.ps1 with it"):
            tier = self.killed_while_its_tier_works()
            expect(until(lambda: not tier.alive, ENDED_SECONDS)).to(be_true)

        with context("and run again on the same commit"):
            with before.each:
                self.killed_while_its_tier_works()
                self.again = self.start(seconds=6)
                self.tier_process()

            with it("should record the process that runs it now"):
                expect(RunningProcess(self.recorded()["pid"]).alive).to(be_true)

            with it("should read as running to the cadence while it runs"):
                cadence = TestCadence(TestRunRecord(self.home, self.checkout))
                expect([run.state for run in cadence.latest_runs]).to(equal(["running"]))

    with context("that the cadence starts in the background, after a run that failed"):
        with before.each:
            self.two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
            record = TestRunRecord(self.home, self.checkout)
            record.save(TestRun(TestTier.E2E, "old", datetime.now(timezone.utc), RunOutcome.PASSED))
            record.save(TestRun(TestTier.HEAVY, "old", self.two_hours_ago, RunOutcome.FAILED))
            os.environ.update({"RUN_SECONDS": "0", "RUN_EXIT": "1", "RUN_PID_FILE": ""})
            TestCadence(record).start_due()
            until(lambda: self.recorded().get("outcome") == "failed", SOON_SECONDS)

        with after.each:
            for name in ("RUN_SECONDS", "RUN_EXIT", "RUN_PID_FILE"):
                os.environ.pop(name, None)

        with it("should be recorded as one run, the failed run still the one before it"):
            expect(self.recorded("previous").get("started_at")).to(equal(self.two_hours_ago.isoformat()))

        with it("should not be a new failure"):
            expect(self.recorded().get("is_new_failure")).to(be_false)

    with context("whose checkout takes a commit while its tier works"):
        with before.each:
            self.head = git(self.checkout, "rev-parse", "HEAD")
            run = self.start(seconds=6)
            self.tier_process()
            (self.checkout / "moved.txt").write_text("moved during the run", encoding="utf-8")
            git(self.checkout, "add", "moved.txt")
            git(self.checkout, "commit", "-q", "-m", "Moved during the run")
            self.output = self.ended(run)

        with it("should run the files of the commit it records"):
            expect(self.output).to(contain(f"HEAD {self.head}", "moved False", f"heavy passed on {self.head[:9]}"))

        with it("should leave the repository with its own folder alone once it ends"):
            expect(git(self.checkout, "worktree", "list", "--porcelain").count("worktree ")).to(equal(1))

    with context("whose checkout has packages npm installed, which git does not keep"):
        with before.each:
            self.output = self.ended(self.start())

        with it("should run with those packages"):
            expect(self.output).to(contain("packages True"))

        with it("should leave them in the checkout once it ends"):
            expect((self.checkout / "app" / "node_modules" / "installed.txt").is_file()).to(be_true)

    with context("whose tier captures screens under the scheduled release"):
        with it("should bring them back to the checkout, where they are reviewed"):
            self.ended(self.start(captures=True))
            captured = self.checkout / ".sessions" / "scheduled" / "e2e-test-results" / "run-1" / "step.txt"
            expect(captured.is_file()).to(be_true)

    with context("on another checkout than the one whose run failed"):
        with before.each:
            self.ended(self.start(exit_code=1))
            self.other = self.repository("other")
            self.ended(self.start(checkout=self.other))

        with it("should leave the first checkout's result as it was"):
            expect(TestRunRecord(self.home, self.checkout).latest(TestTier.HEAVY).state).to(equal("failed"))

        with it("should keep its own result under its own checkout"):
            expect(TestRunRecord(self.home, self.other).latest(TestTier.HEAVY).state).to(equal("passed"))


with description("the record of test runs") as self:
    with before.each:
        self.root = Path(tempfile.mkdtemp(prefix="test-runs-record-heavy-"))
        self.home = self.root / "home"
        self.home.mkdir()
        self.file = self.home / "test-runs.json"
        self.record = TestRunRecord(self.home)

    with after.each:
        shutil.rmtree(self.root, ignore_errors=True)

    def run_by_hand(self) -> subprocess.CompletedProcess:
        env = {**os.environ, "PYTHONPATH": str(REPOSITORY), "PYTHONIOENCODING": "utf-8"}
        return subprocess.run([sys.executable, "-m", "harness.diagnostics.test_runs", "heavy", str(self.root), str(self.home)], cwd=self.root,
                              env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=SOON_SECONDS, check=False)

    with context("that another process writes again and again"):
        with before.each:
            self.record.save(TestRun(TestTier.HEAVY, "abc123", datetime.now(timezone.utc)))
            writes = ("import sys, time\nfrom datetime import datetime, timezone\n"
                      "from harness.diagnostics.test_runs import TestRun, TestRunRecord, TestTier\n"
                      "record = TestRunRecord(sys.argv[1])\nrun = record.latest(TestTier.HEAVY)\nend = time.monotonic() + 3\n"
                      "print('writing', flush=True)\n"
                      "while time.monotonic() < end:\n    record.save(run)\n")
            self.writer = subprocess.Popen([sys.executable, "-c", writes, str(self.home)], cwd=self.root, stdout=subprocess.PIPE, text=True,
                                           env={**os.environ, "PYTHONPATH": str(REPOSITORY)})
            self.writer.stdout.readline()

        with after.each:
            self.writer.kill()

        with it("should never read as holding no run"):
            reads = []
            while self.writer.poll() is None:
                reads.append(self.record.latest(TestTier.HEAVY))
            expect((len(reads) > 100, reads.count(None))).to(equal((True, 0)))

    with context("that was cut short"):
        with before.each:
            self.file.write_text('{"heavy": {"latest": {"tier": "heavy", "outcome": "fai', encoding="utf-8")
            self.answer = self.run_by_hand()

        with it("should refuse a run by hand, naming the file"):
            expect(self.answer.stdout + self.answer.stderr).to(contain(str(self.file)))

        with it("should refuse it without a traceback"):
            expect(self.answer.stdout + self.answer.stderr).not_to(contain("Traceback"))

        with it("should be left as it is"):
            expect(self.file.read_text(encoding="utf-8")).to(equal('{"heavy": {"latest": {"tier": "heavy", "outcome": "fai'))

    with context("that holds a list where its tiers belong"):
        with it("should refuse a run by hand, naming the file"):
            self.file.write_text("[]", encoding="utf-8")
            answer = self.run_by_hand()
            expect((answer.returncode, "Traceback" in answer.stderr, str(self.file) in answer.stdout + answer.stderr)).to(equal((1, False, True)))
