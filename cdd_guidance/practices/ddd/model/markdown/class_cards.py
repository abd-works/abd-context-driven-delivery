"""Class cards under an aggregate — the model fidelity's `####` sections in CE class notation.

Each markdown building block is its own card: a *MarkdownEntity*, *MarkdownValueObject*, *MarkdownRepository*, and the
others read and write their own `####` section, and the sketch's fence for them. Its stereotypes are the class's
`stereotypes`; its invariants are its own list."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model import marks_in
from cdd_guidance.practices.clean_engineering.model import Operation
from cdd_guidance.practices.clean_engineering.model import Property
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
_PROPERTIES = "------"
_OPERATIONS = "----"
_CALL = "->"
_NOTE = "//"
_INVARIANT = "invariant:"
_ORDER = ("Aggregate Root", "Entity", "Value Object", "Repository")
_REFERENCE = re.compile(r"^-?\s*(?:→|->)?\s*([A-Za-z][\w ·]*?)\s*\(by\s+([A-Za-z_]\w*)\s*\)")
_IDENT = re.compile(r"^[A-Za-z_]\w*$")
# A repository written inside its root's card, below the root's own lines: `**CartRepository** «Repository»`.
_REPOSITORY_IN_ROOT = re.compile(r"^\*\*([A-Za-z_]\w*)\*\*\s*(?:«|<<)\s*Repository\s*(?:»|>>)$")
_REPOSITORY_OPERATIONS = re.compile(r"[/,]")
# Lines in an entity fence that belong to the aggregate's map, not to the class: integration arcs and event lists.
_MAP_LINES = ("- ", "→", "pattern:", "crosses:", "integrat", "direction:")


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


class ClassCard(MarkdownDomainNode):
    """A building block as its `####` card: the class with its stereotypes, its members in CE class notation, and the
    invariants the card lists. Each markdown building block is a card and reads and writes its own lines."""

    def __init__(self, *args, **kwargs) -> None:
        self._made_root = False
        super().__init__(*args, **kwargs)
        self.invariants: list[str] = []
        # A repository written and drawn inside its root's card, under its own heading, rather than as a card.
        self.drawn_in_root = False

    @staticmethod
    def _named(name: str, stereotypes: list[str]) -> "ClassCard":
        """An empty card of the building block its stereotypes name; a plain class card for none."""
        marks = ordered_stereotypes(stereotypes)
        card = _CARD_OF_KIND.get(kind_named_by(marks), MarkdownClass)(name, 0)
        card.stereotypes = marks
        return card

    def take_words_from(self, earlier: "ClassCard") -> None:
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
    def from_heading(heading: str) -> "ClassCard":
        """An empty card for `Name <<Stereotype>> …`."""
        return ClassCard._named(plain_class_name(heading), marks_in(heading))

    @staticmethod
    def read(section: list[str]) -> list["ClassCard"]:
        """The cards a `####` section writes: its own, from its heading, members and invariants, then the repository
        a `**Name** «Repository»` line below them writes inside it, with the members that follow that line."""
        cards = [ClassCard.from_heading(section[0].strip()[len(CARD):])]
        body = _CardBody(cards[0])
        for line in (raw.strip() for raw in section[1:] if raw.strip()):
            in_root = _REPOSITORY_IN_ROOT.match(line)
            if in_root is None:
                body.read(line)
                continue
            cards.append(ClassCard.from_heading(f"{in_root.group(1)} <<Repository>>"))
            cards[-1].drawn_in_root = True
            body = _CardBody(cards[-1])
        return cards

    @staticmethod
    def from_code(oclass: OoadClass) -> "ClassCard":
        """The card a class read from code or a class drawing is: the building block its DDD stereotypes, or its name,
        make it, holding the class's own members, without its constructor, and its intent."""
        card = ClassCard._named(oclass.name, TacticalClass(oclass).building_block_stereotypes)
        card.sequential_order = oclass.sequential_order
        card.intent = oclass.intent
        card.properties = list(oclass.properties)
        card.operations = [item for item in oclass.operations if not item.is_constructor and item.name != oclass.name]
        card.drawn_in_root = bool(oclass.folded_into)
        return card

    @staticmethod
    def from_sketch(heading: str, lines: list[str]) -> list["ClassCard"]:
        """A sketch entity fence as cards: the entity itself, then its repository when the fence names `repo:`."""
        card = ClassCard.from_heading(heading)
        return [card] + _SketchFence(card, lines).read()

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

    def add_member(self, line: str, as_operation: bool) -> Property | Operation | None:
        """Read one `+ name: Type` or `+ name(parameters): Type` line onto the card's class."""
        operation = _OPERATION.match(line)
        if operation and (as_operation or "(" in line.split(":", 1)[0]):
            return self._add_operation(operation)
        prop = _PROPERTY.match(line)
        return self._add_property(prop) if prop else None


    def lines(self) -> list[str]:
        heading = f"**{self.name}** «Repository»" if self.drawn_in_root else f"{CARD}{self.heading}"
        written = [heading, "", _PROPERTIES]
        written.extend(self._property_lines())
        operations = self._operation_lines()
        if operations:
            written.extend([_OPERATIONS, *operations])
        if self.invariants:
            written.extend(["", "**Invariants**", ""])
            written.extend(f"- {item}" for item in self.invariants)
        written.append("")
        return written

    def _property_lines(self) -> list[str]:
        written: list[str] = []
        for prop in self.plain_properties:
            access = "-" if prop.access == "private" else "+"
            kind = f"<< {prop.stereotype} >> " if prop.stereotype else ""
            typed = f": {prop.type_hint}" if prop.type_hint else ""
            written.append(f"{access} {kind}{prop.name}{typed}")
            if prop.description:
                written.append(f"\t{_NOTE} {prop.description}")
        return written

    def _operation_lines(self) -> list[str]:
        written: list[str] = []
        for operation in self.operations:
            access = "-" if getattr(operation, "access", "") == "private" else "+"
            parameters = ", ".join(item.save() for item in operation.parameters)
            returned = f": {operation.return_type}" if operation.return_type else ""
            written.append(f"{access} {operation.name}({parameters}){returned}")
            written.extend(f"\t{_CALL} {callee}" for callee in operation.callees)
            if operation.description:
                written.append(f"\t{_NOTE} {operation.description}")
        return written

    def sketch_lines(self) -> list[str]:
        """The card in a sketch's entity fence: its members, its operations with their calls, then its invariants."""
        invariants = [f"{_INVARIANT} {item}" for item in self.invariants]
        return self._property_lines() + self._operation_lines() + invariants

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

    def _add_operation(self, written: re.Match[str]) -> Operation:
        """The operation a `+ name(parameters): Type` line writes."""
        access, _kind, name, parameters, returned = written.groups()
        found = Operation(name, len(self.operations) + 1, return_type=(returned or "").strip())
        found.take_parameters([item.strip() for item in parameters.split(",") if item.strip()])
        found.access = "private" if access == "-" else "public"
        self.operations.append(found)
        return found

    def _add_property(self, written: re.Match[str]) -> Property:
        """The property a `+ << kind >> name: Type` line writes."""
        access, kind, name, type_hint = written.groups()
        found = Property(name, len(self.properties) + 1, (type_hint or "").strip())
        found.stereotype = (kind or "").lower()
        found.access = "private" if access == "-" else "both"
        self.properties.append(found)
        return found



class _CardBody:
    """One read of a card's body onto its card: its members under `------` and `----`, the notes and calls under each,
    and the invariants it lists. It keeps which list it is in and the member read last, which a note below belongs
    to."""

    def __init__(self, card: ClassCard) -> None:
        self._card = card
        self._in_operations = False
        self._in_invariants = False
        self._last: Property | Operation | None = None

    def read(self, line: str) -> None:
        if line in (_PROPERTIES, _OPERATIONS):
            self._in_operations = line == _OPERATIONS
            return
        if line.lower().startswith("**invariants**"):
            self._in_invariants = True
            return
        if self._in_invariants and line.startswith("- "):
            self._card.invariants.append(line[2:].strip())
            return
        if not self._reads_note(line) and line.startswith(("+", "-")):
            self._last = self._card.add_member(line, self._in_operations)

    def _reads_note(self, line: str) -> bool:
        """A `-> call` under an operation or a `// description` under a member belongs to that member."""
        if line.startswith(_CALL) and isinstance(self._last, Operation):
            self._last.callees.append(line[len(_CALL):].strip())
            return True
        if line.startswith(_NOTE) and self._last is not None:
            self._last.description = line[len(_NOTE):].strip()
            return True
        return False


class _SketchFence:
    """The sketch fence under a card's heading, read line by line onto the card the way the clean-engineering sketch
    reads one: `invariant:` lines are its invariants; `refs:` entries other aggregates it holds by identity; `repo:` the
    repository card that keeps it, with the collection operations the line below lists; a `-> call` under an operation
    one of its calls; a `+ name(parameters): Type` line a member as on a card; anything else a sketch member."""

    def __init__(self, card: ClassCard, lines: list[str]) -> None:
        self._card = card
        self._lines = [self._without_note(raw) for raw in lines]
        self._index = 0
        # The member the last line added, which a `-> call` below it belongs to.
        self._last: Property | Operation | None = None
        self._repositories: list[ClassCard] = []

    def read(self) -> list[ClassCard]:
        """Read every line onto the card; answers the repository cards the fence's `repo:` lines name."""
        while self._index < len(self._lines):
            line = self._lines[self._index]
            self._index += 1
            if line and not line.startswith("```"):
                self._read_line(line)
        return self._repositories

    def _read_line(self, line: str) -> None:
        lower = line.lower()
        if lower.startswith(_INVARIANT):
            self._card.invariants.append(line.split(":", 1)[1].strip())
            return
        if lower.startswith("refs:"):
            self._read_references()
            return
        if lower.startswith("repo:"):
            self._repositories.append(self._repository_named(line.split(":", 1)[1].strip()))
            return
        if line.startswith(_CALL) and isinstance(self._last, Operation):
            self._last.callees.append(line[len(_CALL):].strip())
            return
        if line.endswith(":") or line.startswith(_MAP_LINES):
            return
        if line.startswith(("+", "-")):
            self._last = self._card.add_member(line, "(" in line)
            return
        self._last = None
        self._add_sketch_member(line, self._calls_below())

    def _add_sketch_member(self, line: str, calls: list[str]) -> None:
        """One sketch line that names a member, the way the clean-engineering sketch reads one: `Name <<Stereotype>>`
        is an owned member; a line with calls under it, or with parameters, is an operation; a single word a property."""
        tokens = plain_class_name(line).replace("()", " ").split()
        if not tokens:
            return
        if marks_in(line):
            self._add_owned(tokens[0])
            return
        if calls or len(tokens) > 1 or "(" in line:
            self._add_sketch_operation(tokens, calls)
            return
        self._card.properties.append(Property(tokens[0], len(self._card.properties) + 1))

    def _add_owned(self, member: str) -> None:
        """A member the class composes, held under its own name in lower camel case."""
        owned = Property(member[0].lower() + member[1:], len(self._card.properties) + 1, member)
        owned.stereotype = "composition"
        self._card.properties.append(owned)

    def _add_sketch_operation(self, tokens: list[str], calls: list[str]) -> None:
        """An operation named by the first token, its parameters the identifiers after it, calling calls."""
        operation = Operation(tokens[0].split("(", 1)[0], len(self._card.operations) + 1)
        operation.take_parameters([token for token in tokens[1:] if _IDENT.match(token)])
        operation.callees.extend(calls)
        self._card.operations.append(operation)

    def _read_references(self) -> None:
        """The `refs:` entries below: each another aggregate the card's class holds by its identity."""
        while self._index < len(self._lines) and _REFERENCE.match(self._lines[self._index]):
            target, identity = _REFERENCE.match(self._lines[self._index]).groups()
            held = Property(identity, len(self._card.properties) + 1, target.split("·")[-1].strip())
            held.stereotype = "association"
            self._card.properties.append(held)
            self._index += 1

    def _repository_named(self, named: str) -> ClassCard:
        """The repository card a `repo:` line names, with the collection operations the line below lists."""
        repository = ClassCard.from_heading(named if "<<" in named else f"{named} <<Repository>>")
        following = self._lines[self._index] if self._index < len(self._lines) else ""
        if not following or following.endswith(":"):
            return repository
        self._index += 1
        for name in (part.strip().rstrip("()") for part in _REPOSITORY_OPERATIONS.split(following)):
            if _IDENT.match(name):
                repository.operations.append(Operation(name, len(repository.operations) + 1))
        return repository

    def _calls_below(self) -> list[str]:
        """The `-> call` lines below a sketch member: the calls of the operation it names."""
        calls: list[str] = []
        while self._index < len(self._lines) and self._lines[self._index].startswith(_CALL):
            calls.append(self._lines[self._index][len(_CALL):].strip())
            self._index += 1
        return calls

    def _without_note(self, raw: str) -> str:
        stripped = raw.strip()
        return "" if stripped.startswith(_NOTE) else stripped.split(_NOTE, 1)[0].strip()


class MarkdownClass(ClassCard, OoadClass):
    """A card whose stereotypes name no building block: a plain class."""


class MarkdownEntity(ClassCard, Entity):
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


class MarkdownValueObject(ClassCard, ValueObject):
    pass


class MarkdownRepository(ClassCard, Repository):
    pass


class MarkdownDomainService(ClassCard, DomainService):
    pass


class MarkdownSpecification(ClassCard, Specification):
    pass


class MarkdownFactory(ClassCard, Factory):
    pass


# The card class of each building block a card's stereotypes name (`stereotypes.KIND_OF_STEREOTYPE`); a card that names
# none is a plain class.
_CARD_OF_KIND: dict[str | None, type[ClassCard]] = {
    "EntityRoot": MarkdownEntity,
    "Entity": MarkdownEntity,
    "ValueObject": MarkdownValueObject,
    "Repository": MarkdownRepository,
    "DomainService": MarkdownDomainService,
    "Specification": MarkdownSpecification,
    "Factory": MarkdownFactory,
}
_OPERATION = re.compile(r"^([+-])\s*(?:<<\s*(\w+)\s*>>\s*)?(\w+)\((.*?)\)\s*(?::\s*(.+))?$")
_PROPERTY = re.compile(r"^([+-])\s*(?:<<\s*(\w+)\s*>>\s*)?(\w+)\s*(?::\s*(.+))?$")


def ordered_stereotypes(found: list[str]) -> list[str]:
    known = [item for item in _ORDER if any(item.lower() == mark.lower() for mark in found)]
    return known + [item for item in found if item.lower() not in {mark.lower() for mark in known}]


def _called_class(callee: str) -> str:
    """The class a call names before its operation: `BookRepository` of `BookRepository.load(bookId)`; none for a call
    that names only an operation."""
    named = callee.strip().partition(".")[0].partition("(")[0].strip()
    return named if named[:1].isupper() else ""
