"""A lock file claimed by two real processes: the operating system keeps it for one of them at a time, names that one,
and gives it back when that process is killed, however it ends. lock_file_spec.py holds the same within one process."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from expects import be_false, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.process.lock_file import LockFile, LockFileHeld
from harness.process.process import RunningProcess

REPOSITORY = Path(__file__).resolve().parents[2]
# Another process that claims the lock file it is given, says so, and holds it until it is killed.
HOLDER = """import os, sys, time
from harness.process.lock_file import LockFile
lock = LockFile(sys.argv[1], wait_seconds=30)
lock.claim()
print(os.getpid(), flush=True)
time.sleep(600)
"""
# How long the killed holder's process has to end.
ENDED_SECONDS = 15
# How long this process's claim waits for the lock of a killed holder, which Windows gives back a moment after the
# process ends.
FREED_SECONDS = 10


with description("a lock file two processes claim") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="lock-file-heavy-"))
        self.path = self.folder / "test-runs.claim"
        self.holder = subprocess.Popen([sys.executable, "-c", HOLDER, str(self.path)], stdin=subprocess.DEVNULL,
                                       stdout=subprocess.PIPE, text=True, env={**os.environ, "PYTHONPATH": str(REPOSITORY)})
        # The process that holds the lock, which a virtual environment's launcher starts as a child of its own.
        self.holding = RunningProcess(int(self.holder.stdout.readline()))
        self.lock = LockFile(self.path, wait_seconds=0)

    with after.each:
        self.holding.stop(ENDED_SECONDS)
        self.holder.wait(ENDED_SECONDS)
        self.lock.release()
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("that the other process holds"):
        with it("should refuse this process, naming the other"):
            expect(self.lock.claim).to(raise_error(LockFileHeld, contain(f"process {self.holding.pid}")))

        with it("should not be taken by this process trying it at once"):
            expect(self.lock.try_claim()).to(be_false)

    with context("whose holder is killed"):
        with before.each:
            self.holding.stop(ENDED_SECONDS)

        with it("should be taken by this process, which it then names"):
            self.lock = LockFile(self.path, wait_seconds=FREED_SECONDS)
            self.lock.claim()
            expect(self.lock.holder).to(equal(os.getpid()))

        with it("should be free though the file it named the killed process in is still there"):
            self.lock = LockFile(self.path, wait_seconds=FREED_SECONDS)
            self.lock.claim()
            expect((self.path.is_file(), self.lock.is_held)).to(equal((True, True)))
