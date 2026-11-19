"""One install at a time in an IDE folder: a second waits for the first, and is refused by name when the first outlasts
the wait."""
import os
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.install_lock import InstallAlreadyRunning, InstallLock

# A process id no process has: the holder of a lock an install left when it was stopped.
_NO_PROCESS = 0


with description("an IDE folder an install is running in") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="install-lock-")) / ".claude"
        self.lock = InstallLock(self.folder, wait_seconds=0)
        self.lock_file = self.folder / InstallLock.NAME

    with after.each:
        shutil.rmtree(self.folder.parent, ignore_errors=True)

    with context("that the install has taken"):
        with before.each:
            self.lock.claim()
            self.second = InstallLock(self.folder, wait_seconds=0)

        with it("should refuse a second install once its wait is over"):
            expect(self.second.claim).to(raise_error(InstallAlreadyRunning))

        with it("should name the folder and the process installing into it"):
            try:
                self.second.claim()
            except InstallAlreadyRunning as refusal:
                expect(str(refusal)).to(contain(str(self.folder), str(os.getpid())))

        with context("and a step of the same install asks for again"):
            with before.each:
                self.lock.claim()

            with it("should let the step in, since the install already holds the folder"):
                expect(self.lock_file.is_file()).to(equal(True))

            with it("should stay taken when the step is done, until the install itself is"):
                self.lock.release()
                expect(self.second.claim).to(raise_error(InstallAlreadyRunning))

        with context("and the install has given back"):
            with before.each:
                self.lock.release()

            with it("should hold no lock"):
                expect(self.lock_file.exists()).to(equal(False))

            with it("should let the second install in"):
                self.second.claim()
                expect(self.lock_file.is_file()).to(equal(True))

    with context("that an install was stopped in, leaving its lock"):
        with before.each:
            self.folder.mkdir(parents=True)
            self.lock_file.write_text(str(_NO_PROCESS), encoding="ascii")
            self.lock.claim()

        with it("should let the next install in, under its own process"):
            expect(self.lock_file.read_text(encoding="ascii")).to(equal(str(os.getpid())))

    with context("held for the length of one install"):
        with it("should be free again afterwards"):
            held = InstallLock(self.folder).held()
            held.__enter__()
            held.__exit__(None, None, None)
            expect(self.lock_file.exists()).to(equal(False))
