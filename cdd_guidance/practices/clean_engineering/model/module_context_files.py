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


def listed_terms(raw: str) -> List[str]:
    """The terms a bullet lists, separated by commas or semicolons, without their backticks and bold; none for
    `*(none)*`."""
    text = re.sub(r"^\*\(?none\)?\*$", "", raw.strip(), flags=re.IGNORECASE).strip()
    if text.lower() in {"*(none)*", "(none)", "none", "-"}:
        return []
    found = (re.sub(r"^\*\*?|\*\*?$", "", part.strip().strip("`").strip()).strip() for part in re.split(r"[,;]", text))
    return [term for term in found if term]


class ModuleMeta:
    """<<Value Object>> The Purpose, Seam, and Dependencies bullets of a modules-fidelity block, and the prose left
    beside them."""

    _PURPOSE = re.compile(r"^-?\s*\*\*Purpose:\*\*\s*(.+)$", re.IGNORECASE)
    _SEAM = re.compile(r"^-?\s*\*\*Seam(?:\s*\(terms\))?:\*\*\s*(.+)$", re.IGNORECASE)
    _DEPENDENCIES = re.compile(r"^-?\s*\*\*Dependencies(?:\s*\(one-way\))?:\*\*\s*(.+)$", re.IGNORECASE)
    # Lines that frame the bullets and say nothing of the module: a build order, a nested module's or the block's heading.
    _FRAMING = re.compile(r"^-?\s*\*\*Build order:\*\*|^###\s+Module\s+|^##\s+Modules fidelity", re.IGNORECASE)

    def __init__(self, text: str) -> None:
        self.purpose = ""
        self.seam_terms: List[str] = []
        self.dependencies: List[str] = []
        leftover: List[str] = []
        for line in text.splitlines():
            if not self._take_bullet(line.strip()):
                leftover.append(line)
        self.leftover = "\n".join(leftover).strip()
        # The prose beside a Purpose bullet is the card's language; with no bullet the prose is the purpose itself.
        self.language = self.leftover if self.purpose else ""
        # A nested "### Module `path`" block often puts its purpose only in its prose.
        prose = [line.strip() for line in self.leftover.splitlines() if line.strip() and not line.strip().startswith("- **")]
        self.purpose = self.purpose or (prose[0] if prose else "")

    def _take_bullet(self, stripped: str) -> bool:
        """Keep the bullet this line is; true when the line is a bullet or framing, false for prose."""
        purpose, seam, dependencies = (pattern.match(stripped) for pattern in (self._PURPOSE, self._SEAM, self._DEPENDENCIES))
        if purpose:
            self.purpose = purpose.group(1).strip()
        elif seam:
            self.seam_terms = listed_terms(seam.group(1))
        elif dependencies:
            self.dependencies = listed_terms(dependencies.group(1))
        return bool(purpose or seam or dependencies or self._FRAMING.match(stripped))


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

    def bullets(self) -> ModuleMeta:
        """What the card's Purpose, Seam, and Dependencies bullets say."""
        return ModuleMeta(self.read())

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
        card and a bounded context, and what its card says, the seam terms and dependencies it names among them."""
        bullets = self.bullets()
        return {
            "has_module_context": self.exists(),
            "card_seam_terms": bullets.seam_terms,
            "card_dependencies": bullets.dependencies,
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
