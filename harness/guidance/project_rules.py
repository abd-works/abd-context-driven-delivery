"""Find the custom rulesets a project keeps under `.context/rules/` folders."""
from __future__ import annotations

import os
from pathlib import Path

_SKIP_DIRS = {
    ".git",
    "node_modules",
    ".codeql",
    "__pycache__",
    "dist",
    ".venv",
    "venv",
}


class ProjectRulesets:
    """*ProjectRulesets* are the `.context/rules/{practice}/` folders found anywhere under a project's working folder,
    by practice key. Walking the project is slow, so each working folder is walked once per process."""

    _found: dict[str, dict[str, list[Path]]] = {}

    def __init__(self, root: Path) -> None:
        self.root = root

    def folders_for(self, practice: str) -> list[Path]:
        """Each `.context/rules/{practice}/` folder under the working folder, the working folder's own first."""
        key = str(self.root.resolve())
        if key not in self._found:
            self._found[key] = self._walk()
        return self._found[key].get(practice, [])

    def _walk(self) -> dict[str, list[Path]]:
        found: dict[str, list[Path]] = {}
        for dirpath, dirnames, _filenames in os.walk(self.root, onerror=lambda _error: None):
            dirnames[:] = [name for name in dirnames if name not in _SKIP_DIRS and name != ".context"]
            rules_root = Path(dirpath) / ".context" / "rules"
            if not rules_root.is_dir():
                continue
            for child in rules_root.iterdir():
                if child.is_dir():
                    found.setdefault(child.name, []).append(child)
        return found
