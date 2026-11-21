"""InstallLock - one install or clean at a time in a folder installs write into."""
from __future__ import annotations

import sys
from pathlib import Path

from harness.process.lock_file import LockFile, LockFileHeld

# How long an install waits for another one in the same folder, which takes about a minute in full.
WAIT_SECONDS = 180.0


class InstallAlreadyRunning(LockFileHeld):
    """Another process is still installing into, or cleaning, the same folder after the wait. Two at once remove and
    write the same files, so one would fail on a file the other had just removed."""

    def __init__(self, folder: Path, holder: int, waited_seconds: float) -> None:
        self.folder = folder
        super().__init__(folder / InstallLock.NAME, holder, waited_seconds)

    def message(self) -> str:
        return (
            f"another install (process {self.holder}) is still running in {self.folder} after waiting "
            f"{self.waited_seconds:g} seconds; run this again when it is done"
        )


class InstallLock(LockFile):
    """The *LockFile* ``.install-lock`` in a folder installs write into, held for the process that installs into it or
    cleans it. A second install says what it waits for and how long, waits for the first to finish, then runs; one that
    outlasts the wait refuses the second with *InstallAlreadyRunning*. The steps of one install share its lock: an
    install cleans the last one while it holds the folder."""

    NAME = ".install-lock"

    def __init__(self, folder: Path, wait_seconds: float = WAIT_SECONDS) -> None:
        super().__init__(folder / self.NAME, wait_seconds)
        self.folder = folder

    def _refused(self) -> Exception:
        return InstallAlreadyRunning(self.folder, self.holder, self.wait_seconds)

    def _tell_what_it_waits_for(self) -> None:
        print(
            f"waiting up to {self.wait_seconds:g} seconds for the install process {self.holder} is running in {self.folder}",
            file=sys.stderr,
            flush=True,
        )
