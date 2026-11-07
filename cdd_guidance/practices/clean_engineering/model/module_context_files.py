"""The module card (`.context/module-context.md`) of a code folder, and the facts its text gives the graph."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

_MODULES_HEADING = re.compile(r"^\s*#{1,6}\s+Modules\b", re.MULTILINE | re.IGNORECASE)
_SIX_DASHES = re.compile(r"^------\s*$", re.MULTILINE)
_SOURCES = re.compile(r"^\s*\*\*Sources\s*/\s*context:\*\*", re.MULTILINE | re.IGNORECASE)
_LIVE_INSTANCE = re.compile(r"Live instance:", re.IGNORECASE)
_MODEL_BLOCKS = (
    (_SIX_DASHES, "typed `------` member dump"),
    (_SOURCES, "**Sources / context** that lists this folder's own files"),
    (_LIVE_INSTANCE, "'Live instance:' name inventory"),
)
_CARD_NAME = "module-context.md"


class ModuleContext:
    """The module card of one code folder."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        # The folder's module card: `module-context.md` in its `.context`.
        self.path = folder / ".context" / _CARD_NAME

    def exists(self) -> bool:
        return self.path.is_file()

    def read(self) -> str:
        """The card's text; empty when the folder has no card."""
        if not self.exists():
            return ""
        return self.path.read_text(encoding="utf-8")

    def has_modules_heading(self) -> bool:
        """True when the card has a `Modules` heading; the opening lines of each card already say what it is."""
        return bool(_MODULES_HEADING.search(self.read()))

    def model_blocks(self) -> List[str]:
        """Model-fidelity detail written into a modules-fidelity card, one description per kind found."""
        content = self.read()
        return [
            f"Module '{self.folder.name}' module-context has {detail}"
            for pattern, detail in _MODEL_BLOCKS
            if pattern.search(content)
        ]
