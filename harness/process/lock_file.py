"""LockFile - a file the operating system locks for the one process that holds it, naming that process."""
from __future__ import annotations

import contextlib
import os
import time
from pathlib import Path
from typing import Iterator

# How often a claim that found the file held asks the operating system again.
_LOOK_AGAIN_SECONDS = 0.02
# The byte of the lock file the operating system locks: far past the process id written at its start, so a waiting
# process can still read who holds the file.
_LOCKED_BYTE = 1024


def _takes_operating_system_lock(handle: int) -> bool:
    """Whether the operating system gave this process the lock on the open file handle names, which closing the file
    gives back; it refuses at once while another holder has it. Windows locks one byte of the file, _LOCKED_BYTE, past
    the process id at its start, so a waiting process can still read that id."""
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(handle, _LOCKED_BYTE, os.SEEK_SET)
            msvcrt.locking(handle, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


class LockFileHeld(TimeoutError):
    """Another holder kept a lock file for longer than a claim waits for it."""

    def __init__(self, path: Path, holder: int, waited_seconds: float) -> None:
        self.path = path
        self.holder = holder
        self.waited_seconds = waited_seconds
        super().__init__(self.message())

    def message(self) -> str:
        """What the refusal says; a lock that names its file in other words says its own."""
        return f"{self.path} is held by process {self.holder}, and was not let go in {self.waited_seconds:g} seconds"


class LockFile:
    """A file locked by the operating system for the one holder that claimed it, such as the lock that lets one install
    write into an IDE folder at a time, the lock beside a JSON file several processes change, the lock that lets one
    command start a server while the others wait for it, or the claim on the record of test runs that lets one process
    at a time look at which tier is due. Claiming it is one step of the operating system, so of any number of claims
    made at the same moment exactly one gets it. The operating system gives the lock back when its holder closes it or
    its process ends, however it ends, so a killed holder leaves the file but never a held lock, and a process id
    another program was given later holds nothing. The holder writes its process id at the file's start (`holder`), so a
    claim that waits can say for whom. A claim waits up to its wait while another holder has the file, then refuses
    (*LockFileHeld*); `try_claim` does not wait, and answers whether it took the file. One holder may claim again while
    it holds the file, as the steps of one install do; the file is free once its first claim is given back. Each holder
    makes its own *LockFile*: two threads sharing one would both pass as its one holder."""

    def __init__(self, path: Path, wait_seconds: float) -> None:
        self.path = Path(path)
        self.wait_seconds = wait_seconds
        self._depth = 0
        self._handle: int | None = None

    @property
    def is_held(self) -> bool:
        """Whether this holder has the file now."""
        return self._handle is not None

    @property
    def holder(self) -> int:
        """The process the file names; 0 when it names none, as while its holder is writing it."""
        try:
            named = self.path.read_text(encoding="ascii", errors="replace").strip()
        except OSError:
            return 0
        return int(named) if named.isdigit() else 0

    @contextlib.contextmanager
    def held(self) -> Iterator[None]:
        """Hold the file for one piece of work, waiting for another holder."""
        self.claim()
        try:
            yield
        finally:
            self.release()

    def claim(self) -> None:
        """Take the file, or one more step of the work that already holds it; wait while another holder has it, and
        refuse once the wait is over."""
        if self._depth == 0:
            self._wait_until_claimed()
        self._depth += 1

    def try_claim(self) -> bool:
        """Take the file, or one more step of the work that already holds it, at once; False, without waiting, while
        another holder has it, as for a look that is skipped rather than kept waiting."""
        if self._depth == 0 and not self._claimed():
            return False
        self._depth += 1
        return True

    def release(self) -> None:
        """Give back one step; the file is free once the first claim is given back. The file stays, since removing it
        could take it from under a holder that has just opened it."""
        if self._depth == 0:
            return
        self._depth -= 1
        if self._depth == 0 and self._handle is not None:
            os.close(self._handle)
            self._handle = None

    def _refused(self) -> Exception:
        """The error a claim raises once its wait is over; a lock that names its file in other words gives its own."""
        return LockFileHeld(self.path, self.holder, self.wait_seconds)

    def _tell_what_it_waits_for(self) -> None:
        """Say, once, that a claim waits for another holder; a plain lock waits without a word."""

    def _wait_until_claimed(self) -> None:
        deadline = time.monotonic() + self.wait_seconds
        told = False
        while not self._claimed():
            if time.monotonic() >= deadline:
                raise self._refused()
            if not told:
                self._tell_what_it_waits_for()
                told = True
            time.sleep(_LOOK_AGAIN_SECONDS)

    def _claimed(self) -> bool:
        """Open the file and ask the operating system for its lock; on getting it, name this process in the file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        handle = os.open(str(self.path), os.O_CREAT | os.O_RDWR)
        if not _takes_operating_system_lock(handle):
            os.close(handle)
            return False
        os.ftruncate(handle, 0)
        os.lseek(handle, 0, os.SEEK_SET)
        os.write(handle, str(os.getpid()).encode("ascii"))
        self._handle = handle
        return True
