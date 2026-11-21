"""Where a markdown model document writes each class card: the heading that names the class, the lines up to the next
heading of its level or above, and the line under it that declares each member. A markdown class model reads a card's
text, not its lines, so a graph that holds a class read from a document places it here, and a reader of the graph opens
the card's lines in the document as it opens a class's lines in code."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.class_stereotypes import without_marks

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# The name a heading gives: its first word once its stereotypes and bold or code marks are gone.
_HEADING_NAME = re.compile(r"[A-Za-z_$][\w$]*")
# A member line: its visibility, any stereotypes, then the member's name.
_MEMBER_LINE = r"^\s*[+\-#~]\s*(?:<<[^>]*>>\s*)*{name}\b"


class CardLines:
    """The lines of one markdown model document, which place each class it describes at its card: the class at the
    heading that names it, through the line before the next heading of its level or above; and each operation and
    property at the line in that card that declares it."""

    def __init__(self, text: str) -> None:
        self._lines = text.splitlines()
        # Each heading: its line number, counted from 1, its level, and its text without stereotypes or marks.
        self._headings = [
            (number, len(found.group(1)), self._plain(found.group(2)))
            for number, found in ((index, _HEADING.match(line)) for index, line in enumerate(self._lines, start=1))
            if found
        ]

    def place(self, oclass: OoadClass) -> None:
        """Put the class at its card's lines, and each of its members at the line that declares it; a class no heading
        names stays where its parser left it. The class keeps the card's lines as its source, so the facts its source
        gives read the card."""
        card = self.card_of(oclass.name)
        if card is None:
            return
        oclass.line, oclass.end_line = card
        for member in [*oclass.public_properties, *oclass.operations]:
            line = self._member_line(member.name, card)
            member.line = line
            member.end_line = line
        for operation in oclass.operations:
            operation.line_count = 1
        oclass.source_facts.take_lines(self._lines)

    def card_of(self, name: str) -> tuple[int, int] | None:
        """The first and last line of the class card called name: the deepest heading whose first word is name, as a
        card sits under the module or aggregate that may share its name; none when no heading names it."""
        named = [(number, level) for number, level, text in self._headings if self._first_word(text) == name]
        return self._lines_under(max(named, key=lambda found: (found[1], -found[0]))) if named else None

    def section_of(self, name: str) -> tuple[int, int] | None:
        """The first and last line of the section whose heading reads name, such as an aggregate's: the shallowest such
        heading, as the cards inside it may share its name; none when no heading reads it."""
        named = [(number, level) for number, level, text in self._headings if text == name]
        return self._lines_under(min(named, key=lambda found: (found[1], found[0]))) if named else None

    def _lines_under(self, heading: tuple[int, int]) -> tuple[int, int]:
        """The heading's line, through the last line with text before the next heading of its level or above."""
        number, level = heading
        following = (other for other, other_level, _name in self._headings if other > number and other_level <= level)
        end = next(following, len(self._lines) + 1) - 1
        while end > number and not self._lines[end - 1].strip():
            end -= 1
        return number, end

    def _member_line(self, name: str, card: tuple[int, int]) -> int:
        """The line in the card that declares the member called name; the card's heading when none does."""
        pattern = re.compile(_MEMBER_LINE.format(name=re.escape(name)))
        first, last = card
        return next((number for number in range(first + 1, last + 1) if pattern.match(self._lines[number - 1])), first)

    def _plain(self, heading: str) -> str:
        return without_marks(heading).replace("*", "").replace("`", "").strip()

    def _first_word(self, text: str) -> str:
        found = _HEADING_NAME.search(text)
        return found.group(0) if found else ""
