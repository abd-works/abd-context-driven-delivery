"""Specs for stopping a process by its id, as the hook daemon and the cdd server stop an older copy of themselves."""
import os
import subprocess
import sys
import threading
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import after, before, context, description, it

from harness.process.running_process import RunningProcess
from harness.process.stoppable_process import StoppableProcess

WAIT_SECONDS = 5


def _sleeping_child() -> subprocess.Popen:
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    # Reap the child as soon as it ends, so elsewhere than Windows it does not linger as a zombie that looks alive.
    threading.Thread(target=child.wait, daemon=True).start()
    return child


with description("a stoppable process") as self:
    with before.each:
        self.signalled = []
        self._kill = os.kill

    with after.each:
        os.kill = self._kill

    def _record_signals(self) -> None:
        os.kill = lambda pid, sig: self.signalled.append(pid)

    with context("that is running"):
        with it("should end when stopped"):
            child = _sleeping_child()
            try:
                StoppableProcess(child.pid).stop(WAIT_SECONDS)
                expect(RunningProcess(child.pid).alive).to(equal(False))
            finally:
                child.kill()

    with context("that has already exited"):
        with it("should stop without complaint"):
            child = subprocess.Popen([sys.executable, "-c", "pass"])
            child.wait()
            StoppableProcess(child.pid).stop(WAIT_SECONDS)
            expect(RunningProcess(child.pid).alive).to(equal(False))

    with context("that is this process"):
        with it("should not be signalled"):
            self._record_signals()
            StoppableProcess(os.getpid()).stop(WAIT_SECONDS)
            expect(self.signalled).to(equal([]))

    with context("that an address file names with no id"):
        with it("should not be signalled"):
            self._record_signals()
            StoppableProcess(0).stop(WAIT_SECONDS)
            expect(self.signalled).to(equal([]))
