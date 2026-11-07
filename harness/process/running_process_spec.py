"""Specs for asking whether a process is still running."""
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.process.running_process import RunningProcess


with description("a running process"):
    with context("that is this process"):
        with it("should be alive"):
            expect(RunningProcess(os.getpid()).alive).to(equal(True))

    with context("that has exited"):
        with it("should not be alive"):
            child = subprocess.Popen([sys.executable, "-c", "pass"])
            child.wait()
            expect(RunningProcess(child.pid).alive).to(equal(False))

    with context("that a lock file names with no id"):
        with it("should not be alive"):
            expect(RunningProcess(0).alive).to(equal(False))

    with context("that was asked about"):
        with it("should keep running"):
            child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(5)"])
            try:
                RunningProcess(child.pid).alive
                expect(child.poll()).to(equal(None))
            finally:
                child.kill()
                child.wait()
