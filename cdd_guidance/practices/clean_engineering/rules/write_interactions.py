"""write-interactions — reuse sketch interaction notation in markdown artifacts."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_BOLD_INTERACTION = re.compile(r"\*\*Interaction:\*\*", re.I)
_BOLD_INVARIANT_BULLET = re.compile(r"^\s*[-*]\s+\*\*Invariant:\*\*", re.I | re.M)
_L_TAG = re.compile(r"<!--\s*L\s*-->", re.I)
_LANGUAGE_HEADING = re.compile(r"^#{1,3}\s+Language\b", re.I)
_ANY_HEADING = re.compile(r"^#{1,6}\s+")
_META = re.compile(
    r"do\s+\*\*not\*\*\s+invent|do not invent|never invent|parallel symbol|as collaboration markers",
    re.I,
)


class WriteInteractions(PracticeGraphRule):
    slug = "write-interactions"
    node_types = ("Operation", "Property", "Invariant", "OoadClass")

    def check(self, node, context) -> list[str]:
        text = context.span(node) or context.text(node)
        if not text.strip() or not text.lstrip().startswith("#"):
            return []
        return _markdown_violations(text)


def _markdown_violations(text: str) -> list[str]:
    hits: list[str] = []
    in_language = False
    for lineno, line in enumerate(text.splitlines(), start=1):
        if _LANGUAGE_HEADING.match(line):
            in_language = True
        elif _ANY_HEADING.match(line) and not _LANGUAGE_HEADING.match(line):
            in_language = False
        if _META.search(line):
            continue
        if _BOLD_INTERACTION.search(line):
            hits.append(
                f"Line {lineno}: use `-> collaborator.operation` sketch notation, not bold **Interaction:** bullets."
            )
        if _BOLD_INVARIANT_BULLET.search(line) and not (in_language or _L_TAG.search(line)):
            hits.append(
                f"Line {lineno}: use `//` under the operation for invariants, not bold **Invariant:** bullets."
            )
    return hits[:2]
