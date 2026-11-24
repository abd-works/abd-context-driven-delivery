"""A file the operating system locks for one holder at a time, naming that holder's process: a second claim waits, then
is refused; a holder that claims again keeps the file until its first claim is given back."""
import os
import shutil
import tempfile
from pathlib import Path

from expects import be_false, be_true, contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.process.lock_file import LockFile, LockFileHeld


with description("a lock file") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="lock-file-"))
        self.path = self.folder / "start.lock"
        self.lock = LockFile(self.path, wait_seconds=0)
        self.second = LockFile(self.path, wait_seconds=0)

    with after.each:
        self.lock.release()
        self.second.release()
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("that one holder has claimed"):
        with before.each:
            self.lock.claim()

        with it("should name the holder's process"):
            expect(self.second.holder).to(equal(os.getpid()))

        with it("should refuse a second holder once its wait is over, naming the file and the holder"):
            expect(self.second.claim).to(raise_error(LockFileHeld, contain(str(self.path), f"process {os.getpid()}")))

        with context("and claims again"):
            with before.each:
                self.lock.claim()

            with it("should stay held when the second claim is given back"):
                self.lock.release()
                expect(self.second.claim).to(raise_error(LockFileHeld))

            with it("should be free once the first claim is given back"):
                self.lock.release()
                self.lock.release()
                self.second.claim()
                expect(self.second.is_held).to(be_true)

        with it("should answer that a second holder trying it at once did not take it"):
            expect(self.second.try_claim()).to(be_false)

        with context("and tries it again"):
            with it("should take one more step of the work that holds it"):
                expect(self.lock.try_claim()).to(be_true)

    with context("that no holder has claimed"):
        with it("should be taken by a holder trying it at once"):
            expect(self.lock.try_claim()).to(be_true)

    with context("held for one piece of work"):
        with it("should be free again afterwards"):
            held = self.lock.held()
            held.__enter__()
            held.__exit__(None, None, None)
            self.second.claim()
            expect(self.second.is_held).to(be_true)

    with context("left by a holder that was stopped, naming a process that is gone"):
        with before.each:
            self.path.write_text("0", encoding="ascii")

        with it("should let the next holder in, under its own process"):
            self.lock.claim()
            expect(self.lock.holder).to(equal(os.getpid()))
