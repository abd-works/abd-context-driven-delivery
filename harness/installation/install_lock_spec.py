"""One install at a time in an IDE folder: a second waits for the first, and is refused by name when the first outlasts
the wait. The lock is held by the operating system for the process that took it, so it ends with that process."""
import os
import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.installation.install_lock import InstallAlreadyRunning, InstallLock


with description("an IDE folder an install is running in") as self:
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="install-lock-")) / ".claude"
        self.lock = InstallLock(self.folder, wait_seconds=0)
        self.second = InstallLock(self.folder, wait_seconds=0)
        self.lock_file = self.folder / InstallLock.NAME

    with after.each:
        self.lock.release()
        self.second.release()
        shutil.rmtree(self.folder.parent, ignore_errors=True)

    with context("that the install has taken"):
        with before.each:
            self.lock.claim()

        with it("should name the process installing into it, for whoever waits"):
            expect(self.lock_file.read_text(encoding="ascii")).to(equal(str(os.getpid())))

        with it("should refuse a second install once its wait is over"):
            expect(self.second.claim).to(raise_error(InstallAlreadyRunning))

        with it("should name the folder, the process installing into it, and how long the second waited"):
            try:
                self.second.claim()
            except InstallAlreadyRunning as refusal:
                expect(str(refusal)).to(contain(str(self.folder), f"process {os.getpid()}", "after waiting 0 seconds"))

        with context("and a step of the same install asks for again"):
            with before.each:
                self.lock.claim()

            with it("should stay taken when the step is done, until the install itself is"):
                self.lock.release()
                expect(self.second.claim).to(raise_error(InstallAlreadyRunning))

            with it("should be free once the install itself is done"):
                self.lock.release()
                self.lock.release()
                self.second.claim()
                expect(self.second.is_held).to(equal(True))

        with context("and the install has given back"):
            with before.each:
                self.lock.release()

            with it("should let the second install in"):
                self.second.claim()
                expect(self.second.is_held).to(equal(True))

    with context("that an install was stopped in, leaving its lock file"):
        with context("naming a process that is gone"):
            with before.each:
                self.folder.mkdir(parents=True)
                self.lock_file.write_text("0", encoding="ascii")
                self.lock.claim()

            with it("should let the next install in, under its own process"):
                expect(self.lock_file.read_text(encoding="ascii")).to(equal(str(os.getpid())))

            with it("should let in only one of two installs that were waiting for it"):
                expect(self.second.claim).to(raise_error(InstallAlreadyRunning))

        with context("naming a process id another program has since been given"):
            with before.each:
                self.folder.mkdir(parents=True)
                # This spec's own process stands for the other program: it runs, and holds no lock on the folder.
                self.lock_file.write_text(str(os.getpid()), encoding="ascii")

            with it("should let the next install in, since no process holds the folder"):
                self.lock.claim()
                expect(self.lock.is_held).to(equal(True))

    with context("held for the length of one install"):
        with it("should be free again afterwards"):
            held = self.lock.held()
            held.__enter__()
            held.__exit__(None, None, None)
            self.second.claim()
            expect(self.second.is_held).to(equal(True))
