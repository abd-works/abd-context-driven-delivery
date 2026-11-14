"""Specs for stopping a process by its id that has already exited. Heavy: starts a Python process and waits for it to
end."""
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.process.process import RunningProcess, StoppableProcess

WAIT_SECONDS = 5


with description("a stoppable process"):
    with context("that has already exited"):
        with it("should stop without complaint"):
            child = subprocess.Popen([sys.executable, "-c", "pass"])
            child.wait()
            StoppableProcess(child.pid).stop(WAIT_SECONDS)
            expect(RunningProcess(child.pid).alive).to(equal(False))
