"""CappedLogFile — a log file kept under a size, so a log written to on every tool call or by a server that runs for
weeks cannot grow until it fills the disk."""
from __future__ import annotations

from pathlib import Path

# The size a log reaches before its lines move to the previous file. A session's log of a week's work is well under a
# megabyte, so the cap is only reached by a log that is written far more than it is read.
LOG_SIZE_LIMIT_BYTES = 4 * 1024 * 1024
# What the previous file adds to the log's name: ``session.log`` keeps its earlier lines in ``session.log.1``.
_PREVIOUS_SUFFIX = ".1"


class CappedLogFile:
    """A log file that, once it reaches its size, moves its lines to the previous file beside it (``server.log.1``),
    replacing an older one, so the next line starts a new file. The log and its previous file together never take much
    more than twice its size, and the latest lines are always in the log itself."""

    def __init__(self, path: Path, limit_bytes: int = LOG_SIZE_LIMIT_BYTES) -> None:
        self.path = Path(path)
        self.limit_bytes = limit_bytes

    @property
    def previous(self) -> Path:
        """The file that keeps the lines written before the last roll."""
        return self.path.with_name(self.path.name + _PREVIOUS_SUFFIX)

    @property
    def is_full(self) -> bool:
        return self.path.is_file() and self.path.stat().st_size >= self.limit_bytes

    def roll_when_full(self) -> bool:
        """Move the log's lines to the previous file when it has reached its size; whether it did. A log another process
        holds open at that moment, such as a server's output while it runs or a line the other server is appending,
        cannot be moved on Windows, so it rolls at the next write or start that finds it free."""
        if not self.is_full:
            return False
        try:
            self.path.replace(self.previous)
        except PermissionError:
            return False
        return True
