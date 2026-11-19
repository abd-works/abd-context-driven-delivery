"""InstallLock - one install or clean at a time in an IDE folder."""
from __future__ import annotations

import contextlib
import os
import time
from pathlib import Path
from typing import Iterator

from harness.process.process import RunningProcess

# How long an install waits for another one in the same folder, which takes about a minute in full, and how often it
# looks again.
WAIT_SECONDS = 180.0
_LOOK_AGAIN_SECONDS = 0.1


class InstallAlreadyRunning(RuntimeError):
    """Another process is still installing into, or cleaning, the same IDE folder after the wait. Two at once remove
    and write the same files, so one would fail on a file the other had just removed."""

    def __init__(self, folder: Path, holder: int) -> None:
        super().__init__(f"another install (process {holder}) is still running in {folder}; run this again when it is done")
        self.folder = folder
        self.holder = holder


class InstallLock:
    """The file ``.install-lock`` in an IDE folder, naming the process that installs into it or cleans it. A second
    install waits for the first to finish, then runs; one that outlasts the wait refuses the second with
    *InstallAlreadyRunning*. A lock whose process has gone, as a stopped install leaves, is taken over. The steps of
    one install share its lock: an install cleans the last one while it holds the folder."""

    NAME = ".install-lock"

    def __init__(self, folder: Path, wait_seconds: float = WAIT_SECONDS) -> None:
        self.folder = folder
        self._path = folder / self.NAME
        self._wait_seconds = wait_seconds
        self._depth = 0

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
        """Give back one step; the folder is free once the install's first claim is given back."""
        self._depth -= 1
        if self._depth == 0:
            self._path.unlink(missing_ok=True)

    def _wait_until_claimed(self) -> None:
        deadline = time.monotonic() + self._wait_seconds
        while not self._claimed():
            if time.monotonic() >= deadline:
                raise InstallAlreadyRunning(self.folder, self._holder())
            time.sleep(_LOOK_AGAIN_SECONDS)

    def _claimed(self) -> bool:
        self.folder.mkdir(parents=True, exist_ok=True)
        self._free_if_holder_has_gone()
        try:
            handle = os.open(str(self._path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (FileExistsError, PermissionError):
            return False
        try:
            os.write(handle, str(os.getpid()).encode("ascii"))
        finally:
            os.close(handle)
        return True

    def _free_if_holder_has_gone(self) -> None:
        """Remove a lock that names a process no longer running. A lock that names none yet is one its holder is still
        writing, and is left."""
        named = self._named()
        if named.isdigit() and not RunningProcess(int(named)).alive:
            self._path.unlink(missing_ok=True)

    def _holder(self) -> int:
        named = self._named()
        return int(named) if named.isdigit() else 0

    def _named(self) -> str:
        """What the lock file holds: its holder's process id, or nothing while it is being written or is gone again."""
        try:
            return self._path.read_text(encoding="ascii").strip()
        except OSError:
            return ""
