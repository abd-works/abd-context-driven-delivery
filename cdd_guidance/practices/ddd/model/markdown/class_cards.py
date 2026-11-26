"""Class cards under an aggregate — the model fidelity's `####` sections in the one class-card notation.

Each building block is a card (*DomainClass*); *CardSection* reads a `####` section into the cards it writes and writes
a card back as its section. A card's members are read and written in Clean Engineering's class-card notation
(*ClassCard*), with DDD's own options: no constructor line, the stereotypes in their order, a repository drawn inside
its root's card, and the **Invariants** a card lists."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.markdown.class_card import ClassCard
from cdd_guidance.practices.ddd.model.building_blocks import DomainClass

CARD = "#### "
# A repository written inside its root's card, below the root's own lines: `**CartRepository** «Repository»`.
_REPOSITORY_IN_ROOT = re.compile(r"^\*\*([A-Za-z_]\w*)\*\*\s*(?:«|<<)\s*Repository\s*(?:»|>>)$")
# A building block's card writes no constructor line: its members start at the properties.
_MEMBERS = ClassCard([], writes_constructor=False)


class CardSection:
    """A building block's `####` section: its heading with its stereotypes, its members, and the invariants it lists;
    a repository drawn inside its root's card is a `**Name** «Repository»` line below the root's members."""

    def __init__(self, card: DomainClass) -> None:
        self._card = card

    @staticmethod
    def read(section: list[str]) -> list[DomainClass]:
        """The cards a `####` section writes: its own, from its heading, members and invariants, then the repository
        a `**Name** «Repository»` line below them writes inside it, with the members that follow that line."""
        cards = [DomainClass.from_heading(section[0].strip()[len(CARD):])]
        bodies: list[list[str]] = [[]]
        for line in (raw.strip() for raw in section[1:] if raw.strip()):
            in_root = _REPOSITORY_IN_ROOT.match(line)
            if in_root is None:
                bodies[-1].append(line)
                continue
            cards.append(DomainClass.from_heading(f"{in_root.group(1)} <<Repository>>"))
            cards[-1].written_in_root = True
            bodies.append([])
        for card, body in zip(cards, bodies):
            CardSection(card).read_body(body)
        return cards

    def read_body(self, body: list[str]) -> None:
        """Read the card's lines in the class-card notation: its members, then the invariants its **Invariants**
        lists."""
        ClassCard(body, writes_constructor=False).read_into(self._card)

    def lines(self) -> list[str]:
        card = self._card
        heading = f"**{card.name}** «Repository»" if card.written_in_root else f"{CARD}{card.heading}"
        return [heading, "", *_MEMBERS.lines_of(card, card.plain_properties), ""]
