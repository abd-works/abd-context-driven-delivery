"""One file holding a JSON object, read and written whole by the object that owns it."""
from __future__ import annotations

import json
import os
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Any, Iterator, Mapping

# How long a swap Windows refuses is tried again, and how long between tries.
_SWAP_SECONDS = 5.0
_SWAP_RETRY_SECONDS = 0.05
# How long a change waits for another holder of the file to let go, and how long between tries.
_HOLD_SECONDS = 30.0
_HOLD_RETRY_SECONDS = 0.01
# What follows the file's name in the name of the lock file beside it.
_LOCK_SUFFIX = ".lock"


def _takes_operating_system_lock(handle: int, locked_byte: int = 0) -> bool:
    """Whether the operating system gave this process the lock on the open file handle names, which closing the file
    gives back; it refuses at once while another process holds it. Windows locks one byte of the file, the one at
    locked_byte, so a file whose start is still read by a waiting process locks a byte past what it holds."""
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(handle, locked_byte, os.SEEK_SET)
            msvcrt.locking(handle, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


class JsonFileUnreadable(ValueError):
    """A JSON file holds something other than a JSON object. Nothing is written over it, so what it holds stays for a
    person to repair. An owner whose file says more about what to do raises its own kind of this error."""

    def __init__(self, path: Path, cause: Exception) -> None:
        super().__init__(self.message(path, cause))
        self.path = path
        self.cause = cause

    def message(self, path: Path, cause: Exception) -> str:
        return f"{path} is not a readable JSON object ({cause})"


class JsonFileBusy(TimeoutError):
    """Another holder kept a JSON file for longer than a change waits for it, so the change was not made."""

    def __init__(self, path: Path, seconds: float) -> None:
        super().__init__(f"{path} is held for a change by another caller, and was not let go in {seconds:g} seconds")
        self.path = path
        self.seconds = seconds


class JsonFile:
    """One file holding a JSON object, such as ``.context/config.json`` or an install's ``diagnostics.json``. A missing
    file reads as empty, and the file is written indented with a closing newline, so a person can read and compare it.
    A file holding anything but a JSON object raises the owner's kind of *JsonFileUnreadable*, so an owner never saves a
    partial object over what a person wrote. A file only programs read, such as a saved knowledge graph of several
    megabytes, is written ``compact``: on one line, without the spaces indenting would add to every value. A file several
    processes change, such as a chat's prompt queue, is ``held`` from each change's read to its write."""

    def __init__(self, path: Path, unreadable: type[JsonFileUnreadable] = JsonFileUnreadable, compact: bool = False) -> None:
        self.path = Path(path)
        self._unreadable = unreadable
        self._compact = compact

    def exists(self) -> bool:
        return self.path.is_file()

    def read(self) -> dict[str, Any]:
        """The object the file holds; empty when there is no file."""
        if not self.path.is_file():
            return {}
        try:
            data = json.loads(self._text())
        except (OSError, ValueError) as error:
            raise self._unreadable(self.path, error) from error
        if not isinstance(data, dict):
            raise self._unreadable(self.path, TypeError(f"expected an object, found {type(data).__name__}"))
        return data

    def write(self, json_object: Mapping[str, Any]) -> Path:
        """Write json_object as the whole file, making its folder when there is none. The text is written beside the file and
        renamed over it, so a reader, or another chat's call writing the same file at once, never meets half of it. A
        file that already holds the same text is left as it is, so nothing watching it is woken to read it again."""
        text = (json.dumps(dict(json_object), separators=(",", ":")) if self._compact else json.dumps(dict(json_object), indent=2)) + "\n"
        if self._holds(text):
            return self.path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        staged = self.path.with_name(f"{self.path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
        staged.write_text(text, encoding="utf-8")
        try:
            self._swap_in(staged)
        except OSError:
            staged.unlink(missing_ok=True)
            raise
        return self.path

    @contextmanager
    def held(self) -> Iterator[None]:
        """Hold the file for one change, from its read to its write, so a change another thread or process makes to the
        same file waits its turn and none is lost. The hold is the operating system's lock on the lock file beside the
        file, which ends when the holder lets go or its process ends, however it ends: a killed holder blocks nobody,
        and the lock file it leaves holds nothing. A wait longer than _HOLD_SECONDS raises *JsonFileBusy*."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path.with_name(f"{self.path.name}{_LOCK_SUFFIX}"), "a+b") as lock_file:
            self._take(lock_file)
            yield

    def _take(self, lock_file: IO[bytes]) -> None:
        """Take the operating system's lock on lock_file, which closing the file gives back, trying again while another
        holder has it."""
        deadline = time.monotonic() + _HOLD_SECONDS
        while not _takes_operating_system_lock(lock_file.fileno()):
            if time.monotonic() >= deadline:
                raise JsonFileBusy(self.path, _HOLD_SECONDS)
            time.sleep(_HOLD_RETRY_SECONDS)

    def _text(self) -> str:
        """The file's text, without the byte-order mark an editor may have saved at its start. Windows refuses a read
        for the moment another process swaps the file in, so a refusal is tried again until _SWAP_SECONDS pass."""
        deadline = time.monotonic() + _SWAP_SECONDS
        while True:
            try:
                return self.path.read_text(encoding="utf-8-sig")
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(_SWAP_RETRY_SECONDS)

    def _holds(self, text: str) -> bool:
        try:
            return self.path.read_text(encoding="utf-8") == text
        except OSError:
            return False

    def _swap_in(self, staged: Path) -> None:
        """Rename staged over the file. Windows refuses the rename while another process has the file open, as a watcher
        does for a moment after each write, so a refusal is tried again until _SWAP_SECONDS pass, then raised."""
        deadline = time.monotonic() + _SWAP_SECONDS
        while True:
            try:
                os.replace(staged, self.path)
                return
            except PermissionError:
                if time.monotonic() >= deadline:
                    raise
                time.sleep(_SWAP_RETRY_SECONDS)


class HeldJsonFile:
    """A *JsonFile* that many reads ask in quick succession, such as a session's ``session.json``, which one board read
    asks thousands of times. It holds what it read and reads the file again only once the file's last-written time or
    size changes, so a change another process writes is still seen, at the cost of one ``stat`` per read."""

    def __init__(self, file: JsonFile) -> None:
        self._file = file
        # What the file held, and the time and size it had when it was read.
        self._held: tuple[tuple[int, int], dict[str, Any]] | None = None

    @property
    def path(self) -> Path:
        return self._file.path

    def read(self) -> dict[str, Any]:
        """A copy of the object the file holds, so a caller changing it changes nothing held; empty when there is no file."""
        version = self._version()
        held = self._held
        if version is None:
            return {}
        if held is None or held[0] != version:
            held = (version, self._file.read())
            self._held = held
        return dict(held[1])

    def write(self, json_object: Mapping[str, Any]) -> Path:
        self._held = None
        return self._file.write(json_object)

    def _version(self) -> tuple[int, int] | None:
        try:
            status = self._file.path.stat()
        except FileNotFoundError:
            return None
        return status.st_mtime_ns, status.st_size
