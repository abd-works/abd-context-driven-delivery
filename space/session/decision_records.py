"""DecisionRecords - the Context Decision Records a session keeps under its workpath's .context/cdr/."""
from __future__ import annotations

import re
from pathlib import Path

FORMAT_FILE = Path(__file__).parent / "CDR-FORMAT.md"
_NUMBERED_NAME = re.compile(r"^(\d{4})-")


class DecisionRecords:
    """The Context Decision Records in one folder: numbered ``{NNNN}-{slug}.md`` files, each new one numbered one past
    the highest already there, so records read in the order the decisions were made."""

    def __init__(self, folder: Path) -> None:
        self._folder = Path(folder)

    @property
    def paths(self) -> list[Path]:
        """Every record, sorted by file name; none when the folder is not there yet."""
        if not self._folder.is_dir():
            return []
        return sorted(self._folder.glob("*.md"))

    def write(self, slug: str, document: str) -> Path:
        """Write document as the next numbered record called slug, creating the folder when it is the first record."""
        target = self._folder / f"{self._next_number():04d}-{slug}.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(document.strip() + "\n", encoding="utf-8")
        return target

    def _next_number(self) -> int:
        if not self._folder.is_dir():
            return 1
        numbers = [int(match.group(1)) for path in self._folder.iterdir() if path.is_file() and (match := _NUMBERED_NAME.match(path.name))]
        return max(numbers, default=0) + 1
