"""What a board read costs most to work out for one session, kept in its folder between reads."""
from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Callable, TypeVar

from harness.installation.json_file import JsonFile, JsonFileUnreadable

logger = logging.getLogger(__name__)

PROGRESS_CACHE_FILE = "progress-cache.json"
# The questions it keeps answers to for each fidelity.
HAS_OUTPUT = "has_output"
VIOLATION_COUNT = "violation_count"
# How long after its first new answer the file is written: one board read works out many answers, and they go into one
# write rather than one each, which Windows refuses when it comes too fast.
SAVE_SECONDS = 1.0

Kept = TypeVar("Kept", bool, int)


class ProgressCache:
    """*ProgressCache* holds, for each fidelity a session works on, the answers that make reading the board slow:
    whether a file the fidelity declares is already there, which walks the session's folders, and how many violations
    its latest report names, which opens the graph saved beside the report. The board reads every session every two
    seconds, so working these out on each read made the board take over ten seconds to show a move.

    Each answer is kept with the key it was worked out from, and worked out again only when its key changes. The keys
    are what Generate and Validate change: the log lines naming the fidelity, the paths the session declares for it,
    and the latest report with its saved graph. A move changes none of them, so moving a ticket never works them out
    again.

    The session holds one for its folder, as ``progress-cache.json`` there, so a closed session takes it along; the session
    lasts as long as the cdd server, so its answers are held between reads and the file serves the next server. It is a
    cache: a missing or unreadable file, or one another reader holds open while it is written, only means the answers
    are worked out again."""

    def __init__(self, folder: Path | None, save_seconds: float = SAVE_SECONDS) -> None:
        # A session with no folder yet, such as a project's main before anything is saved in it, keeps its answers only
        # while it is held.
        self._file = JsonFile(folder / PROGRESS_CACHE_FILE) if folder is not None else None
        self._held: dict | None = None
        # Board reads run on several threads at once, and each can work out an answer for the same session.
        self._lock = threading.Lock()
        # The write of the new answers, waiting for the read that works them out to finish; none while all are saved.
        self._saving: threading.Timer | None = None
        # How long the write waits for the read that works the answers out; a spec that reads once waits less.
        self._save_seconds = save_seconds

    def answer(self, fidelity: str, question: str, key: str, work_out: Callable[[], Kept]) -> Kept:
        """The answer to question on fidelity, worked out with work_out only when it was last kept under another key,
        and then kept under key for the next read."""
        with self._lock:
            kept = self._read().get(fidelity, {}).get(question)
        if kept is not None and kept.get("key") == key:
            return kept["value"]
        value = work_out()
        with self._lock:
            self._read().setdefault(fidelity, {})[question] = {"key": key, "value": value}
            self._save_soon()
        return value

    def _save_soon(self) -> None:
        if self._file is None or self._saving is not None:
            return
        self._saving = threading.Timer(self._save_seconds, self._save)
        self._saving.daemon = True
        self._saving.start()

    def _save(self) -> None:
        with self._lock:
            self._saving = None
            self._write(dict(self._read()))

    def _read(self) -> dict:
        if self._held is None:
            self._held = self._from_file()
        return self._held

    def _from_file(self) -> dict:
        if self._file is None:
            return {}
        try:
            return self._file.read()
        except JsonFileUnreadable as unreadable:
            logger.warning("%s; its answers are worked out again", unreadable)
            return {}

    def _write(self, held: dict) -> None:
        if self._file is None or not self._file.path.parent.is_dir():
            return
        try:
            self._file.write(held)
        except PermissionError as held_open:
            # Windows refuses to replace a file another process, such as a virus scanner, still has open.
            logger.warning("%s was not saved (%s); it is saved after the next answer worked out", self._file.path, held_open)
