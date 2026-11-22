"""Handoffs - the compact accounts a session keeps in its work folder, so the next agent can continue its work."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from harness.process.log_timestamp import REPORT_DATE_FORMAT

HANDOFF_FORMAT_FILE = Path(__file__).parent / "HANDOFF-FORMAT.md"
_HANDOFF_FILES = "handoff-*.md"
# The section of a handoff that lists what the next agent does, its end, and one numbered step in it.
_APPROACH_HEADING = re.compile(r"^##\s+Approach for Next Agent\s*$", re.IGNORECASE)
_NEXT_SECTION = re.compile(r"^##\s")
_NUMBERED_STEP = re.compile(r"^\s*\d+[.)]\s+(.*)$")


class Handoff:
    """One handoff a session wrote, ``handoff-{timestamp}.md``, read in the format ``HANDOFF-FORMAT.md`` gives it."""

    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def next_steps(self) -> list[str]:
        """The numbered steps of its Approach for Next Agent, each with the lines that continue it; none when it has no
        such section, or the file is gone."""
        text = self.path.read_text(encoding="utf-8") if self.path.is_file() else ""
        steps: list[str] = []
        is_inside = False
        for line in text.splitlines():
            if _APPROACH_HEADING.match(line):
                is_inside = True
                continue
            if not is_inside:
                continue
            if _NEXT_SECTION.match(line):
                break
            step = _NUMBERED_STEP.match(line)
            if step:
                steps.append(step.group(1).strip())
            elif steps and line.strip() and line.startswith((" ", "\t")):
                steps[-1] = f"{steps[-1]} {line.strip()}"
        return steps


class Handoffs:
    """The handoffs in one session folder: ``handoff-{timestamp}.md`` files, whose names sort by the time they were
    written, so the newest is the last."""

    def __init__(self, folder: Path) -> None:
        self._folder = Path(folder)

    @property
    def latest(self) -> Handoff | None:
        """The newest handoff; none before one is written."""
        handoffs = sorted(self._folder.glob(_HANDOFF_FILES))
        return Handoff(handoffs[-1]) if handoffs else None

    def write(self, document: str) -> Path:
        """Write document as a new handoff, creating the session folder when it is not there yet."""
        self._folder.mkdir(parents=True, exist_ok=True)
        path = self._folder / f"handoff-{datetime.now(timezone.utc).strftime(REPORT_DATE_FORMAT)}.md"
        path.write_text(document, encoding="utf-8")
        return path.resolve()
