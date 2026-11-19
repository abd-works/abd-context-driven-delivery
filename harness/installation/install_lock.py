"""InstallLock - one install or clean at a time in a folder installs write into."""
from __future__ import annotations

import contextlib
import os
import sys
import time
from pathlib import Path
from typing import Iterator

# How long an install waits for another one in the same folder, which takes about a minute in full, and how often it
# looks again.
WAIT_SECONDS = 180.0
_LOOK_AGAIN_SECONDS = 0.1
# The byte of the lock file the operating system locks: far past the process id written at its start, so a waiting
# process can still read who holds the folder.
_LOCKED_BYTE = 1024


class InstallAlreadyRunning(RuntimeError):
    """Another process is still installing into, or cleaning, the same folder after the wait. Two at once remove and
    write the same files, so one would fail on a file the other had just removed."""

    def __init__(self, folder: Path, holder: int, waited_seconds: float) -> None:
        super().__init__(
            f"another install (process {holder}) is still running in {folder} after waiting {waited_seconds:g} seconds; "
            "run this again when it is done"
        )
        self.folder = folder
        self.holder = holder
        self.waited_seconds = waited_seconds


class InstallLock:
    """The file ``.install-lock`` in a folder installs write into, locked by the operating system for the process that
    installs into it or cleans it, and naming that process. Taking it is one step of the operating system, so of any
    number of installs that ask at the same moment exactly one gets the folder. The operating system gives the lock
    back when its process ends, however it ends, so a stopped install leaves the file but never a held folder, and a
    process id another program was given later holds nothing. A second install says what it waits for and how long,
    waits for the first to finish, then runs; one that outlasts the wait refuses the second with
    *InstallAlreadyRunning*. The steps of one install share its lock: an install cleans the last one while it holds the
    folder."""

    NAME = ".install-lock"

    def __init__(self, folder: Path, wait_seconds: float = WAIT_SECONDS) -> None:
        self.folder = folder
        self._path = folder / self.NAME
        self._wait_seconds = wait_seconds
        self._depth = 0
        self._handle: int | None = None

    @property
    def is_held(self) -> bool:
        """Whether this install holds the folder now."""
        return self._handle is not None

    @contextlib.contextmanager
    def held(self) -> Iterator[None]:
        """Hold the folder for one install or clean, waiting for another process that holds it."""
        self.claim()
        try:
            yield
        finally:
            self.release()

    def claim(self) -> None:
        """Take the folder, or one more step of the install that already holds it; wait while another process holds
        it, and refuse once the wait is over."""
        if self._depth == 0:
            self._wait_until_claimed()
        self._depth += 1

    def release(self) -> None:
        """Give back one step; the folder is free once the install's first claim is given back. The file stays, since
        removing it could take it from under an install that has just opened it."""
        if self._depth == 0:
            return
        self._depth -= 1
        if self._depth == 0 and self._handle is not None:
            os.close(self._handle)
            self._handle = None

    def _wait_until_claimed(self) -> None:
        deadline = time.monotonic() + self._wait_seconds
        told = False
        while not self._claimed():
            if time.monotonic() >= deadline:
                raise InstallAlreadyRunning(self.folder, self._holder(), self._wait_seconds)
            if not told:
                self._tell_what_it_waits_for()
                told = True
            time.sleep(_LOOK_AGAIN_SECONDS)

    def _tell_what_it_waits_for(self) -> None:
        print(
            f"waiting up to {self._wait_seconds:g} seconds for the install process {self._holder()} is running in {self.folder}",
            file=sys.stderr,
            flush=True,
        )

    def _claimed(self) -> bool:
        """Open the lock file and ask the operating system for its lock; on getting it, name this process in the file."""
        self.folder.mkdir(parents=True, exist_ok=True)
        handle = os.open(str(self._path), os.O_CREAT | os.O_RDWR)
        if not self._locked(handle):
            os.close(handle)
            return False
        os.ftruncate(handle, 0)
        os.lseek(handle, 0, os.SEEK_SET)
        os.write(handle, str(os.getpid()).encode("ascii"))
        self._handle = handle
        return True

    def _locked(self, handle: int) -> bool:
        """Whether the operating system gave this process the file's lock; it refuses at once while another holds it."""
        try:
            if sys.platform == "win32":
                import msvcrt

                os.lseek(handle, _LOCKED_BYTE, os.SEEK_SET)
                msvcrt.locking(handle, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return False
        return True

    def _holder(self) -> int:
        """The process the lock file names; none while its holder is writing it."""
        try:
            named = self._path.read_text(encoding="ascii").strip()
        except OSError:
            return 0
        return int(named) if named.isdigit() else 0
