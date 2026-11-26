"""Specs for asking whether a process is still running, of a process that has exited. Heavy: starts a Python process and
waits for it to end."""
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.process.process import RunningProcess

# A process id Windows and Linux never give out.
NO_PROCESS = 2 ** 22 + 7


with description("a running process"):
    with context("that has exited"):
        with it("should not be alive"):
            child = subprocess.Popen([sys.executable, "-c", "pass"])
            child.wait()
            expect(RunningProcess(child.pid).alive).to(equal(False))

    with context("that no process has the id of"):
        with it("should have no start time"):
            expect(RunningProcess(NO_PROCESS).started_at).to(equal(None))

    with context("that is running"):
        with it("should say the same start time each time it is asked"):
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            try:
                expect(RunningProcess(child.pid).started_at).to(equal(RunningProcess(child.pid).started_at))
            finally:
                child.kill()

        with it("should have started within the last minute"):
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
            try:
                expect(datetime.now(timezone.utc) - RunningProcess(child.pid).started_at < timedelta(minutes=1)).to(equal(True))
            finally:
                child.kill()
