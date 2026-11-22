"""Class cards under an aggregate — the model fidelity's `####` sections in the one class-card notation.

Each markdown building block is its own card: a *MarkdownEntity*, *MarkdownValueObject*, *MarkdownRepository*, and the
others read and write their own `####` section, and the sketch's fence for them. Their members are read and written in
Clean Engineering's class-card notation (*ClassCard*, *SketchFence*), with DDD's own options: no constructor line, the
stereotypes in their order, a repository drawn inside its root's card, and the **Invariants** a card lists. Its
stereotypes are the class's `stereotypes`; its invariants are its own list."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model import marks_in
from cdd_guidance.practices.clean_engineering.model import Operation
from cdd_guidance.practices.clean_engineering.model import Property
from cdd_guidance.practices.clean_engineering.model.markdown.class_card import ClassCard, SketchFence
from cdd_guidance.practices.ddd.model.nodes import (
    DomainEvent,
    DomainService,
    Entity,
    Factory,
    InvariantObject,
    Repository,
    Specification,
    ValueObject,
)
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass, kind_named_by, plain_class_name

CARD = "#### "
_INVARIANT = "invariant:"
_INVARIANTS = "**invariants**"
_ORDER = ("Aggregate Root", "Entity", "Value Object", "Repository")
# A repository written inside its root's card, below the root's own lines: `**CartRepository** «Repository»`.
_REPOSITORY_IN_ROOT = re.compile(r"^\*\*([A-Za-z_]\w*)\*\*\s*(?:«|<<)\s*Repository\s*(?:»|>>)$")
# A building block's card writes no constructor line: its members start at the properties.
_MEMBERS = ClassCard([], writes_constructor=False)


class MarkdownDomainNode:
    def plain_name(self, text: str) -> str:
        name = text.replace("**", "").replace("`", "").strip()
        if "|" in name:
            name = name.split("|", 1)[0]
        return name.strip()

    def member_name(self, text: str) -> str:
        """A member line's name: every word it holds, the choices after a `|` included, since only a heading's `|`
        names an owner."""
        return text.replace("**", "").replace("`", "").strip()

    def owner_from(self, heading: str) -> str:
        if "|" not in heading:
            return ""
        return heading.split("|", 1)[1].strip()


class MarkdownInvariantObject(InvariantObject, MarkdownDomainNode):
    pass


class MarkdownBuildingBlock(MarkdownDomainNode):
    """A building block as its `####` card: the class with its stereotypes, its members in the class-card notation, and
    the invariants the card lists. Each markdown building block is a card and reads and writes its own lines."""

    def __init__(self, *args, **kwargs) -> None:
        self._made_root = False
        super().__init__(*args, **kwargs)
        self.invariants: list[str] = []
        # A repository written and drawn inside its root's card, under its own heading, rather than as a card.
        self.drawn_in_root = False

    @staticmethod
    def _named(name: str, stereotypes: list[str]) -> "MarkdownBuildingBlock":
        """An empty card of the building block its stereotypes name; a plain class card for none."""
        marks = ordered_stereotypes(stereotypes)
        card = _CARD_OF_KIND.get(kind_named_by(marks), MarkdownClass)(name, 0)
        card.stereotypes = marks
        return card

    def take_words_from(self, earlier: "MarkdownBuildingBlock") -> None:
        """Keep the invariants, intent, and member words it has, and take earlier's where it has none, as a card read
        from a drawing takes what the document it is written onto held: where that document writes its repository,
        each property's note and the relationship a drawing shows no arrow for, and each operation's note and calls."""
        self.invariants = self.invariants or list(earlier.invariants)
        self.intent = self.intent or earlier.intent
        self.drawn_in_root = earlier.drawn_in_root
        written_properties = {item.name: item for item in earlier.plain_properties}
        for prop in self.plain_properties:
            written = written_properties.get(prop.name)
            if written is not None:
                prop.description = prop.description or written.description
                if written.type_hint == prop.type_hint and not prop.stereotype:
                    prop.stereotype = written.stereotype
        written_operations = {item.name: item for item in earlier.operations}
        for operation in self.operations:
            if operation.name in written_operations:
                self._take_operation_words(written_operations[operation.name], operation)

    def _take_operation_words(self, earlier: "Operation", operation: "Operation") -> None:
        """The operation's note, and its calls as the document writes them: every call inside the card's aggregate,
        which no arrow shows, each call to another aggregate whose arrow is still drawn, then each arrow the document
        has no call for."""
        operation.description = operation.description or earlier.description
        arrows = {_called_class(callee) for callee in operation.callees}
        local = {card.name for card in self.parent.classes} if self.parent is not None else {self.name}
        kept = [callee for callee in earlier.callees if _called_class(callee) in local | {""} or _called_class(callee) in arrows]
        written = {_called_class(callee) for callee in kept}
        operation.callees = kept + [callee for callee in operation.callees if _called_class(callee) not in written]

    @staticmethod
    def from_heading(heading: str) -> "MarkdownBuildingBlock":
        """An empty card for `Name <<Stereotype>> …`."""
        return MarkdownBuildingBlock._named(plain_class_name(heading), marks_in(heading))

    @staticmethod
    def read(section: list[str]) -> list["MarkdownBuildingBlock"]:
        """The cards a `####` section writes: its own, from its heading, members and invariants, then the repository
        a `**Name** «Repository»` line below them writes inside it, with the members that follow that line."""
        cards = [MarkdownBuildingBlock.from_heading(section[0].strip()[len(CARD):])]
        bodies: list[list[str]] = [[]]
        for line in (raw.strip() for raw in section[1:] if raw.strip()):
            in_root = _REPOSITORY_IN_ROOT.match(line)
            if in_root is None:
                bodies[-1].append(line)
                continue
            cards.append(MarkdownBuildingBlock.from_heading(f"{in_root.group(1)} <<Repository>>"))
            cards[-1].drawn_in_root = True
            bodies.append([])
        for card, body in zip(cards, bodies):
            card.read_body(body)
        return cards

    def read_body(self, body: list[str]) -> None:
        """Read the card's lines: its members in the class-card notation, then the invariants its **Invariants**
        lists."""
        at = next((index for index, line in enumerate(body) if line.lower().startswith(_INVARIANTS)), len(body))
        ClassCard(body[:at], writes_constructor=False).read_into(self)
        self.invariants.extend(line[2:].strip() for line in body[at + 1:] if line.startswith("- "))

    @staticmethod
    def from_code(oclass: OoadClass) -> "MarkdownBuildingBlock":
        """The card a class read from code or a class drawing is: the building block its DDD stereotypes, or its name,
        make it, holding the class's own members, without its constructor, and its intent."""
        card = MarkdownBuildingBlock._named(oclass.name, TacticalClass(oclass).building_block_stereotypes)
        card.sequential_order = oclass.sequential_order
        card.intent = oclass.intent
        card.properties = list(oclass.properties)
        card.operations = [item for item in oclass.operations if not item.is_constructor and item.name != oclass.name]
        card.drawn_in_root = bool(oclass.folded_into)
        return card

    @staticmethod
    def from_sketch(heading: str, lines: list[str]) -> list["MarkdownBuildingBlock"]:
        """A sketch entity fence as cards: the entity itself, then its repository when the fence names `repo:`."""
        card = MarkdownBuildingBlock.from_heading(heading)
        read = SketchFence(lines).read_into(card)
        card.invariants.extend(read.invariants)
        return [card] + [MarkdownBuildingBlock._repository(named, operations) for named, operations in read.repositories]

    @staticmethod
    def _repository(named: str, operations: list[str]) -> "MarkdownBuildingBlock":
        """The repository card a sketch's `repo:` line names, with the collection operations it lists."""
        repository = MarkdownBuildingBlock.from_heading(named if "<<" in named else f"{named} <<Repository>>")
        repository.operations.extend(Operation(name, index) for index, name in enumerate(operations, start=1))
        return repository

    @property
    def is_root(self) -> bool:
        """True when the card is marked <<Aggregate Root>>, or its aggregate made it its root."""
        return self._made_root or kind_named_by(self.stereotypes) == "EntityRoot"

    @is_root.setter
    def is_root(self, value: bool) -> None:
        self._made_root = value

    @property
    def is_repository(self) -> bool:
        return kind_named_by(self.stereotypes) == "Repository"

    @property
    def heading(self) -> str:
        return f"{self.name} {' '.join(f'<<{item}>>' for item in self.stereotypes)}".rstrip()

    @property
    def plain_properties(self) -> list[Property]:
        """What the class holds — not the events or invariant objects DDD hangs on the same list."""
        return [
            item for item in self.properties
            if isinstance(item, Property) and not isinstance(item, (DomainEvent, InvariantObject))
        ]

    def lines(self) -> list[str]:
        heading = f"**{self.name}** «Repository»" if self.drawn_in_root else f"{CARD}{self.heading}"
        written = [heading, "", *_MEMBERS.lines_of(self, self.plain_properties)]
        if self.invariants:
            written.extend(["", "**Invariants**", ""])
            written.extend(f"- {item}" for item in self.invariants)
        written.append("")
        return written

    def sketch_lines(self) -> list[str]:
        """The card in a sketch's entity fence: its members, its operations with their calls, then its invariants."""
        invariants = [f"{_INVARIANT} {item}" for item in self.invariants]
        return _MEMBERS.property_lines(self.plain_properties) + _MEMBERS.operation_lines(self) + invariants

    def write_into(self, module: Module, place: list[str]) -> OoadClass:
        """Add this card to module, a module of a Clean Engineering format, as that format's own class: its
        stereotypes, its intent, its members, with the relationships their types name, and the place of its aggregate
        as its module path."""
        written = module.load_class(self)
        written.update_self(self)
        written.sequential_order = len(module.classes) + 1
        written.module_path = list(place)
        written.properties = [written.load_property(item) for item in self.plain_properties]
        written.operations = [written.load_operation(item) for item in self.operations]
        for prop in written.properties:
            prop.arrow.derive()
        module.classes.append(written)
        return written


class MarkdownClass(MarkdownBuildingBlock, OoadClass):
    """A card whose stereotypes name no building block: a plain class."""


class MarkdownEntity(MarkdownBuildingBlock, Entity):
    """An entity in markdown: a card at model fidelity, or at bounded-context fidelity the root an aggregate's lines
    name, with the member lines under it that it reads as its invariant objects."""

    def __init__(self, name: str = "", sequential_order: int = 0, member_lines: list[str] | None = None, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self._member_lines = list(member_lines or [])

    def load_invariant_objects(self) -> None:
        """Read each member line under the root as one of its invariant objects, once."""
        for line in self._member_lines:
            self.invariant_objects.append(MarkdownInvariantObject(self.member_name(line), len(self.invariant_objects)))
        self._member_lines = []


class MarkdownValueObject(MarkdownBuildingBlock, ValueObject):
    pass


class MarkdownRepository(MarkdownBuildingBlock, Repository):
    pass


class MarkdownDomainService(MarkdownBuildingBlock, DomainService):
    pass


class MarkdownSpecification(MarkdownBuildingBlock, Specification):
    pass


class MarkdownFactory(MarkdownBuildingBlock, Factory):
    pass


# The card class of each building block a card's stereotypes name (`stereotypes.KIND_OF_STEREOTYPE`); a card that names
# none is a plain class.
_CARD_OF_KIND: dict[str | None, type[MarkdownBuildingBlock]] = {
    "EntityRoot": MarkdownEntity,
    "Entity": MarkdownEntity,
    "ValueObject": MarkdownValueObject,
    "Repository": MarkdownRepository,
    "DomainService": MarkdownDomainService,
    "Specification": MarkdownSpecification,
    "Factory": MarkdownFactory,
}


def ordered_stereotypes(found: list[str]) -> list[str]:
    known = [item for item in _ORDER if any(item.lower() == mark.lower() for mark in found)]
    return known + [item for item in found if item.lower() not in {mark.lower() for mark in known}]


def _called_class(callee: str) -> str:
    """The class a call names before its operation: `BookRepository` of `BookRepository.load(bookId)`; none for a call
    that names only an operation."""
    named = callee.strip().partition(".")[0].partition("(")[0].strip()
    return named if named[:1].isupper() else ""
