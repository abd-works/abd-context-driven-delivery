"""The module card (`.context/module-context.md`) of a code folder, and the facts its text gives the graph."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List

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
# A section heading a public source file's documentation gives its internal design.
_INTERNAL_MARKDOWN = re.compile(r"^##\s+Internal\b", re.MULTILINE | re.IGNORECASE)
# An HTML comment, such as the guidance a card copied from the template keeps: it is no part of what the card says.
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


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
        """The card's text, without the comments it carries, which say how to write a card and are not what this one
        says; empty when the folder has no card."""
        if self._text is None:
            self._text = _COMMENT.sub("", self.path.read_text(encoding="utf-8")) if self.exists() else ""
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

    def folder_facts(self) -> Dict[str, object]:
        """The facts the folder's context files give the graph, each read from the card once: whether it has a module
        card and a bounded context, and what its card says."""
        return {
            "has_module_context": self.exists(),
            "has_bounded_context": (self.folder / ".context" / "bounded-context.md").is_file(),
            "modules_heading": self.has_modules_heading(),
            "names_seam": self.names_seam(),
            "names_constraint": self.names_constraint(),
            "model_blocks": self.model_blocks(),
            "is_a_in_context": self.says_is_a_type_of(),
            "child_parent_in_context": self.writes_child_parent_headings(),
        }


class PublicSources:
    """<<Value Object>> The documentation of a folder's public source files, each file's doc strings and comments."""

    def __init__(self, documentation: List[str]) -> None:
        self._documentation = documentation

    @property
    def count(self) -> int:
        return len(self._documentation)

    def internal_notes(self) -> str:
        """Whether the documentation carries internal design notes: 'heading' for an internal-design section heading,
        'mixed' for internal notes inline, else ''."""
        text = "\n".join(self._documentation)
        if _INTERNAL_MARKDOWN.search(text):
            return "heading"
        if "## Internal" in text or "_ holds " in text:
            return "mixed"
        return ""
