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
# `- **Seam (terms):** Cart, Order`: the public names other modules use.
_SEAM = re.compile(r"\*\*Seam(?:\s*\(terms\))?:\*\*", re.IGNORECASE)
# A `## Constraint` heading, or a `**Constraint:**` line: what callers must or must not do.
_CONSTRAINT = re.compile(r"^\s*#{1,6}\s+Constraints?\b|\*\*Constraints?:\*\*", re.MULTILINE | re.IGNORECASE)
# `*is a type of*`: an inheritance line a modules-fidelity card writes in prose.
_IS_A = re.compile(r"\*is a type of\*", re.I)
# `## Child : Parent`: a heading that writes a class with its base.
_CHILD_PARENT = re.compile(r"^\s*#{1,6}\s+\S.+\s+:\s+\S", re.MULTILINE)


class ModuleContext:
    """The module card of one code folder. It reads its card once, the first time it is asked, and answers every
    question about the card from that text."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        # The folder's module card: `module-context.md` in its `.context`.
        self.path = folder / ".context" / _CARD_NAME
        self._text: str | None = None

    def exists(self) -> bool:
        return self.path.is_file()

    def read(self) -> str:
        """The card's text; empty when the folder has no card."""
        if self._text is None:
            self._text = self.path.read_text(encoding="utf-8") if self.exists() else ""
        return self._text

    def has_modules_heading(self) -> bool:
        """True when the card has a `Modules` heading; the opening lines of each card already say what it is."""
        return bool(_MODULES_HEADING.search(self.read()))

    def names_seam(self) -> bool:
        """True when the card names the module's seam, `**Seam (terms):**`."""
        return bool(_SEAM.search(self.read()))

    def names_constraint(self) -> bool:
        """True when the card says what callers must or must not do: a `Constraint` heading or line."""
        return bool(_CONSTRAINT.search(self.read()))

    def says_is_a_type_of(self) -> bool:
        """True when the card writes inheritance in prose, `*is a type of*`."""
        return bool(_IS_A.search(self.read()))

    def writes_child_parent_headings(self) -> bool:
        """True when a heading of the card writes a class with its base, `## Child : Parent`."""
        return bool(_CHILD_PARENT.search(self.read()))

    def model_blocks(self) -> List[str]:
        """Model-fidelity detail written into a modules-fidelity card, one description per kind found."""
        content = self.read()
        return [
            f"Module '{self.folder.name}' module-context has {detail}"
            for pattern, detail in _MODEL_BLOCKS
            if pattern.search(content)
        ]
