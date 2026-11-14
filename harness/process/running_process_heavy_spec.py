"""Specs for asking whether a process is still running, of a process that has exited. Heavy: starts a Python process and
waits for it to end."""
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.process.process import RunningProcess


with description("a running process"):
    with context("that has exited"):
        with it("should not be alive"):
            child = subprocess.Popen([sys.executable, "-c", "pass"])
            child.wait()
            expect(RunningProcess(child.pid).alive).to(equal(False))
