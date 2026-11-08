"""Class cards under an aggregate — the model fidelity's `####` sections in CE class notation.

Each markdown building block is its own card: a *MarkdownEntity*, *MarkdownValueObject*, *MarkdownRepository*, and the
others read and write their own `####` section, and the sketch's fence for them. Its stereotypes are the class's
`stereotypes`; its invariants are its own list."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.base_class_model import Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marks_in
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
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
_ROOT = "aggregate root"
_REPOSITORY = "repository"
_ORDER = ("Aggregate Root", "Entity", "Value Object", "Repository")
_REFERENCE = re.compile(r"^-?\s*(?:→|->)?\s*([A-Za-z][\w ·]*?)\s*\(by\s+([A-Za-z_]\w*)\s*\)")
_IDENT = re.compile(r"^[A-Za-z_]\w*$")
_REPOSITORY_OPERATIONS = re.compile(r"[/,]")
# Lines in an entity fence that belong to the aggregate's map, not to the class: integration arcs and event lists.
_MAP_LINES = ("- ", "→", "pattern:", "crosses:", "integrat", "direction:")


class MarkdownDomainNode:
    def plain_name(self, text: str) -> str:
        name = text.replace("**", "").replace("`", "").strip()
        if "|" in name:
            name = name.split("|", 1)[0]
        return name.strip()

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

    @staticmethod
    def named(name: str, stereotypes: list[str]) -> "ClassCard":
        """An empty card of the building block its stereotypes name; a plain class card for none."""
        marks = ordered_stereotypes(stereotypes)
        card = _CARD_OF_KIND.get(kind_named_by(marks), MarkdownClass)(name, 0)
        card.stereotypes = marks
        return card

    @staticmethod
    def from_heading(heading: str) -> "ClassCard":
        """An empty card for `Name <<Stereotype>> …`."""
        return ClassCard.named(plain_class_name(heading), marks_in(heading))

    @staticmethod
    def read(section: list[str]) -> "ClassCard":
        """The card a `####` section writes: its heading, then its members and invariants."""
        card = ClassCard.from_heading(section[0].strip()[len(CARD):])
        card.read_lines(section[1:])
        return card

    @staticmethod
    def from_code(oclass: OoadClass, intent: str) -> "ClassCard":
        """The card a class read from code or a class drawing is: the building block its DDD stereotypes, or its name,
        make it, holding the class's own members, without its constructor, and intent."""
        card = ClassCard.named(oclass.name, TacticalClass(oclass).building_block_stereotypes)
        card.sequential_order = oclass.sequential_order
        card.intent = intent
        card.properties = list(oclass.properties)
        card.operations = [item for item in oclass.operations if not item.is_constructor and item.name != oclass.name]
        return card

    @staticmethod
    def from_sketch(heading: str, lines: list[str]) -> list["ClassCard"]:
        """A sketch entity fence as cards: the entity itself, then its repository when the fence names `repo:`."""
        card = ClassCard.from_heading(heading)
        return [card] + card.read_sketch_lines(lines)

    @property
    def is_root(self) -> bool:
        """True when the card is marked <<Aggregate Root>>, or its aggregate made it its root."""
        return self._made_root or any(item.lower() == _ROOT for item in self.stereotypes)

    @is_root.setter
    def is_root(self, value: bool) -> None:
        self._made_root = value

    @property
    def is_repository(self) -> bool:
        return any(item.lower() == _REPOSITORY for item in self.stereotypes)

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
            return self._add_operation(*operation.groups())
        prop = _PROPERTY.match(line)
        if prop:
            return self._add_property(*prop.groups())
        return None

    def read_lines(self, lines: list[str]) -> None:
        """Read the card's body: its members under `------` and `----`, the notes and calls under each, and the
        invariants it lists."""
        in_operations = False
        in_invariants = False
        last: Property | Operation | None = None
        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            if line in (_PROPERTIES, _OPERATIONS):
                in_operations = line == _OPERATIONS
                continue
            if line.lower().startswith("**invariants**"):
                in_invariants = True
                continue
            if in_invariants and line.startswith("- "):
                self.invariants.append(line[2:].strip())
                continue
            if not _reads_note(line, last) and line.startswith(("+", "-")):
                last = self.add_member(line, in_operations)

    def read_sketch_lines(self, lines: list[str]) -> list["ClassCard"]:
        """Read the sketch fence under this card's heading, the way the clean-engineering sketch reads one: a line with
        an `->` under it, or with parameters, is an operation; a single word is a property; `Name <<Stereotype>>` is an
        owned member; `refs:` entries are other aggregates held by identity; a `+ name(parameters): Type` line is read
        as on a card. Answers the repository card the fence's `repo:` names, when it names one."""
        cleaned = [_without_note(raw) for raw in lines]
        found: list[ClassCard] = []
        last: Property | Operation | None = None
        index = 0
        while index < len(cleaned):
            line = cleaned[index]
            index += 1
            lower = line.lower()
            if not line or line.startswith("```"):
                continue
            if lower.startswith(_INVARIANT):
                self.invariants.append(line.split(":", 1)[1].strip())
            elif lower.startswith("refs:"):
                index = self._read_references(cleaned, index)
            elif lower.startswith("repo:"):
                repository, index = _repository_named(line.split(":", 1)[1].strip(), cleaned, index)
                found.append(repository)
            elif line.startswith(_CALL) and isinstance(last, Operation):
                last.callees.append(line[len(_CALL):].strip())
            elif line.endswith(":") or line.startswith(_MAP_LINES):
                continue
            elif line.startswith(("+", "-")):
                last = self.add_member(line, "(" in line)
            else:
                last = None
                calls, index = _calls_below(cleaned, index)
                self._read_sketch_member(line, calls)
        return found

    def lines(self) -> list[str]:
        written = [f"{CARD}{self.heading}", "", _PROPERTIES]
        written.extend(self.property_lines())
        written.append(_OPERATIONS)
        written.extend(self.operation_lines())
        if self.invariants:
            written.extend(["", "**Invariants**", ""])
            written.extend(f"- {item}" for item in self.invariants)
        written.append("")
        return written

    def property_lines(self) -> list[str]:
        written: list[str] = []
        for prop in self.plain_properties:
            access = "-" if prop.access == "private" else "+"
            kind = f"<< {prop.stereotype} >> " if prop.stereotype else ""
            typed = f": {prop.type_hint}" if prop.type_hint else ""
            written.append(f"{access} {kind}{prop.name}{typed}")
            if prop.description:
                written.append(f"\t{_NOTE} {prop.description}")
        return written

    def operation_lines(self) -> list[str]:
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
        return self.property_lines() + self.operation_lines() + invariants

    def write_into(self, module: Module, intent: str) -> OoadClass:
        """Add this card to module, a module of a Clean Engineering format, as that format's own class: its
        stereotypes, its members, with the relationships their types name, and intent."""
        written = module.load_class(self)
        written.update_self(self)
        written.sequential_order = len(module.classes) + 1
        written.intent = intent
        written.properties = [written.load_property(item) for item in self.plain_properties]
        written.operations = [written.load_operation(item) for item in self.operations]
        for prop in written.properties:
            prop.derive_relationship()
        module.classes.append(written)
        return written

    def _add_operation(self, access: str, _kind: str, name: str, parameters: str, returned: str) -> Operation:
        found = Operation(
            name,
            len(self.operations) + 1,
            return_type=(returned or "").strip(),
            parameters=[item.strip() for item in parameters.split(",") if item.strip()],
        )
        found.access = "private" if access == "-" else "public"
        self.operations.append(found)
        return found

    def _add_property(self, access: str, kind: str, name: str, type_hint: str) -> Property:
        found = Property(name, len(self.properties) + 1, (type_hint or "").strip())
        found.stereotype = (kind or "").lower()
        found.access = "private" if access == "-" else "both"
        self.properties.append(found)
        return found

    def _read_references(self, lines: list[str], index: int) -> int:
        """The `refs:` entries below: each another aggregate this class holds by its identity."""
        while index < len(lines) and _REFERENCE.match(lines[index]):
            target, identity = _REFERENCE.match(lines[index]).groups()
            held = Property(identity, len(self.properties) + 1, target.split("·")[-1].strip())
            held.stereotype = "association"
            self.properties.append(held)
            index += 1
        return index

    def _read_sketch_member(self, line: str, arrows: list[str]) -> None:
        marks = marks_in(line)
        tokens = plain_class_name(line).replace("()", " ").split()
        if not tokens:
            return
        if marks:
            member = tokens[0]
            owned = Property(member[0].lower() + member[1:], len(self.properties) + 1, member)
            owned.stereotype = "composition"
            self.properties.append(owned)
            return
        if arrows or len(tokens) > 1 or "(" in line:
            operation = Operation(
                tokens[0].split("(", 1)[0],
                len(self.operations) + 1,
                parameters=[token for token in tokens[1:] if _IDENT.match(token)],
            )
            operation.callees.extend(arrows)
            self.operations.append(operation)
            return
        self.properties.append(Property(tokens[0], len(self.properties) + 1))


class MarkdownClass(ClassCard, OoadClass):
    """A card whose stereotypes name no building block: a plain class."""


class MarkdownEntity(ClassCard, Entity):
    """An entity in markdown: a card at model fidelity, or at bounded-context fidelity the root an aggregate's lines
    name, with the member lines under it that it reads as its invariant objects."""

    def __init__(self, name: str = "", sequential_order: int = 0, member_lines: list[str] | None = None, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self._member_lines = list(member_lines or [])
        self._member_index = 0
        self.invariant_object_type = MarkdownInvariantObject

    def has_more_invariant_object(self) -> bool:
        return self._member_index < len(self._member_lines)

    def get_next_invariant_object_from_file(self) -> InvariantObject:
        line = self._member_lines[self._member_index].strip()
        self._member_index += 1
        return MarkdownInvariantObject(self.plain_name(line), len(self.invariant_objects))


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


def _reads_note(line: str, last: Property | Operation | None) -> bool:
    """A `-> call` under an operation or a `// description` under a member belongs to that member."""
    if line.startswith(_CALL) and isinstance(last, Operation):
        last.callees.append(line[len(_CALL):].strip())
        return True
    if line.startswith(_NOTE) and last is not None:
        last.description = line[len(_NOTE):].strip()
        return True
    return False


def _repository_named(named: str, lines: list[str], index: int) -> tuple[ClassCard, int]:
    """The repository card a `repo:` line names, with the collection operations the line below lists."""
    repository = ClassCard.from_heading(named if "<<" in named else f"{named} <<Repository>>")
    following = lines[index] if index < len(lines) else ""
    if following and not following.endswith(":"):
        for name in _REPOSITORY_OPERATIONS.split(following):
            name = name.strip().rstrip("()")
            if _IDENT.match(name):
                repository.operations.append(Operation(name, len(repository.operations) + 1))
        index += 1
    return repository, index


def _calls_below(lines: list[str], index: int) -> tuple[list[str], int]:
    calls: list[str] = []
    while index < len(lines) and lines[index].startswith(_CALL):
        calls.append(lines[index][len(_CALL):].strip())
        index += 1
    return calls, index


def _without_note(raw: str) -> str:
    stripped = raw.strip()
    return "" if stripped.startswith(_NOTE) else stripped.split(_NOTE, 1)[0].strip()
