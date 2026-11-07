"""Handoffs - the compact accounts a session keeps in its folder, so the next agent can continue its work."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from harness.guidance.guidance import REPORT_DATE_FORMAT

HANDOFF_FORMAT_FILE = Path(__file__).parent / "HANDOFF-FORMAT.md"
_HANDOFF_FILES = "handoff-*.md"


class Handoffs:
    """The handoffs in one session folder: ``handoff-{timestamp}.md`` files, whose names sort by the time they were
    written, so the newest is the last."""

    def __init__(self, folder: Path) -> None:
        self._folder = Path(folder)

    @property
    def latest(self) -> Path | None:
        """The newest handoff; none before one is written."""
        handoffs = sorted(self._folder.glob(_HANDOFF_FILES))
        return handoffs[-1] if handoffs else None

    def write(self, document: str) -> Path:
        """Write document as a new handoff, creating the session folder when it is not there yet."""
        self._folder.mkdir(parents=True, exist_ok=True)
        path = self._folder / f"handoff-{datetime.now(timezone.utc).strftime(REPORT_DATE_FORMAT)}.md"
        path.write_text(document, encoding="utf-8")
        return path.resolve()
