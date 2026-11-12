"""One file holding a JSON object, read and written whole by the object that owns it."""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path
from typing import Any, Mapping


class JsonFileUnreadable(ValueError):
    """A JSON file holds something other than a JSON object. Nothing is written over it, so what it holds stays for a
    person to repair. An owner whose file says more about what to do raises its own kind of this error."""

    def __init__(self, path: Path, cause: Exception) -> None:
        super().__init__(self.message(path, cause))
        self.path = path
        self.cause = cause

    def message(self, path: Path, cause: Exception) -> str:
        return f"{path} is not a readable JSON object ({cause})"


class JsonFile:
    """One file holding a JSON object, such as ``.context/config.json`` or an install's ``diagnostics.json``. A missing
    file reads as empty, and the file is written indented with a closing newline, so a person can read and compare it.
    A file holding anything but a JSON object raises the owner's kind of *JsonFileUnreadable*, so an owner never saves a
    partial object over what a person wrote. A file only programs read, such as a saved knowledge graph of several
    megabytes, is written ``compact``: on one line, without the spaces indenting would add to every value."""

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
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise self._unreadable(self.path, error) from error
        if not isinstance(data, dict):
            raise self._unreadable(self.path, TypeError(f"expected an object, found {type(data).__name__}"))
        return data

    def write(self, data: Mapping[str, Any]) -> Path:
        """Write data as the whole file, making its folder when there is none. The text is written beside the file and
        renamed over it, so a reader, or another chat's call writing the same file at once, never meets half of it."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        staged = self.path.with_name(f"{self.path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
        text = json.dumps(dict(data), separators=(",", ":")) if self._compact else json.dumps(dict(data), indent=2)
        staged.write_text(text + "\n", encoding="utf-8")
        os.replace(staged, self.path)
        return self.path


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

    def write(self, data: Mapping[str, Any]) -> Path:
        self._held = None
        return self._file.write(data)

    def _version(self) -> tuple[int, int] | None:
        try:
            status = self._file.path.stat()
        except FileNotFoundError:
            return None
        return status.st_mtime_ns, status.st_size
