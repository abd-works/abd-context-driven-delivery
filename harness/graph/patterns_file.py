"""The patterns a folder's content was generated with, kept in `.context/patterns.md` at the folder's root."""

from __future__ import annotations

import re
from pathlib import Path

_ENTRY = re.compile(r"^-\s*`?([\w-]+)`?\s*(?::\s*(.*))?$")
_HEADER = (
    "# Patterns\n\n"
    "The patterns this folder's content was generated with. Validate judges the content against them. A pattern whose "
    "layers sit in several folders names the roles this folder holds after it.\n\n"
)


class PatternsFile:
    """`.context/patterns.md` in a folder: each pattern its content was generated with, and the roles of the pattern
    the folder holds when the pattern's layers sit in several folders. Generate writes it; validate reads it, so the
    patterns content is judged with are the ones it was made with, whatever the session overlays now. A missing file
    names no patterns."""

    def __init__(self, folder: Path) -> None:
        self.folder = Path(folder)

    @property
    def path(self) -> Path:
        return self.folder / ".context" / "patterns.md"

    @classmethod
    def nearest(cls, path: Path, root: Path) -> PatternsFile | None:
        """The patterns file of the closest folder holding path, from path up to root; none when no folder has one."""
        root = Path(root).resolve()
        folder = Path(path).resolve()
        folder = folder if folder.is_dir() else folder.parent
        while True:
            if folder.name == ".context":
                folder = folder.parent
            found = cls(folder)
            if found.path.is_file():
                return found
            if folder == root or root not in folder.parents:
                return None
            folder = folder.parent

    @property
    def roles(self) -> dict[str, list[str]]:
        """Each pattern it names, with the roles this folder holds of it; no roles when the folder holds the whole pattern."""
        if not self.path.is_file():
            return {}
        entries: dict[str, list[str]] = {}
        for line in self.path.read_text(encoding="utf-8").splitlines():
            entry = _ENTRY.match(line.strip())
            if entry:
                entries[entry.group(1)] = [role.strip() for role in (entry.group(2) or "").split(",") if role.strip()]
        return entries

    @property
    def patterns(self) -> list[str]:
        return list(self.roles)

    def record(self, patterns: list[str]) -> None:
        """Add the patterns it does not name yet, keeping those it names and their roles."""
        entries = self.roles
        added = [pattern for pattern in patterns if pattern not in entries]
        if not added and self.path.is_file():
            return
        entries.update({pattern: [] for pattern in added})
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"- {pattern}" + (f": {', '.join(roles)}" if roles else "") for pattern, roles in entries.items()]
        self.path.write_text(_HEADER + "\n".join(lines) + "\n", encoding="utf-8")
