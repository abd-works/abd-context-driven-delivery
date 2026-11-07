"""Class cards under an aggregate — the model fidelity's `####` sections in CE class notation."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.ddd.model.nodes import DomainEvent, InvariantObject, building_block_type
from cdd_guidance.practices.ddd.model.stereotypes import plain_class_name, stereotypes_in

_CARD = "#### "
_PROPERTIES = "------"
_OPERATIONS = "----"
_CALL = "->"
_NOTE = "//"
_INVARIANT = "invariant:"
_LEAVES_CARD = ("integrations:", "emits events:", "consumes events:", "### ")
_OPERATION = re.compile(r"^([+-])\s*(?:<<\s*(\w+)\s*>>\s*)?(\w+)\((.*?)\)\s*(?::\s*(.+))?$")
_PROPERTY = re.compile(r"^([+-])\s*(?:<<\s*(\w+)\s*>>\s*)?(\w+)\s*(?::\s*(.+))?$")
_ROOT = "aggregate root"
_REPOSITORY = "repository"
_ORDER = ("Aggregate Root", "Entity", "Value Object", "Repository")


class ClassCard:
    """One `####` card: a classified class with its stereotypes and the lines it was read from."""

    def __init__(self, node: OoadClass, stereotypes: list[str]) -> None:
        self.node = node
        self.stereotypes = stereotypes
        self.invariants: list[str] = []

    @classmethod
    def from_heading(cls, heading: str) -> "ClassCard":
        """An empty card for `Name <<Stereotype>> …`."""
        return cls.from_name(plain_class_name(heading), stereotypes_in(heading))

    @classmethod
    def from_name(cls, name: str, stereotypes: list[str]) -> "ClassCard":
        """An empty card, its class typed by the building block its stereotypes name."""
        marks = ordered_stereotypes(stereotypes)
        return cls(building_block_type(marks)(name, 0), marks)

    @property
    def is_root(self) -> bool:
        return any(item.lower() == _ROOT for item in self.stereotypes)

    @property
    def is_repository(self) -> bool:
        return any(item.lower() == _REPOSITORY for item in self.stereotypes)

    @property
    def heading(self) -> str:
        return f"{self.node.name} {' '.join(f'<<{item}>>' for item in self.stereotypes)}".rstrip()

    def add_member(self, line: str, as_operation: bool) -> Property | Operation | None:
        """Read one `+ name: Type` or `+ name(parameters): Type` line onto the card's class."""
        operation = _OPERATION.match(line)
        if operation and (as_operation or "(" in line.split(":", 1)[0]):
            return self._add_operation(*operation.groups())
        prop = _PROPERTY.match(line)
        if prop:
            return self._add_property(*prop.groups())
        return None

    def lines(self) -> list[str]:
        written = [f"{_CARD}{self.heading}", "", _PROPERTIES]
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
        for prop in plain_properties(self.node):
            access = "-" if prop.access == "private" else "+"
            kind = f"<< {prop.stereotype} >> " if prop.stereotype else ""
            typed = f": {prop.type_hint}" if prop.type_hint else ""
            written.append(f"{access} {kind}{prop.name}{typed}")
            if prop.description:
                written.append(f"\t{_NOTE} {prop.description}")
        return written

    def operation_lines(self) -> list[str]:
        written: list[str] = []
        for operation in self.node.operations:
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

    def _add_operation(self, access: str, _kind: str, name: str, parameters: str, returned: str) -> Operation:
        found = Operation(
            name,
            len(self.node.operations) + 1,
            return_type=(returned or "").strip(),
            parameters=[item.strip() for item in parameters.split(",") if item.strip()],
        )
        found.access = "private" if access == "-" else "public"
        self.node.operations.append(found)
        return found

    def _add_property(self, access: str, kind: str, name: str, type_hint: str) -> Property:
        found = Property(name, len(self.node.properties) + 1, (type_hint or "").strip())
        found.stereotype = (kind or "").lower()
        found.access = "private" if access == "-" else "both"
        self.node.properties.append(found)
        return found


def plain_properties(node: OoadClass) -> list[Property]:
    """What the class holds — not the events or invariant objects DDD hangs on the same list."""
    return [
        item for item in node.properties
        if isinstance(item, Property) and not isinstance(item, (DomainEvent, InvariantObject))
    ]


def ordered_stereotypes(found: list[str]) -> list[str]:
    known = [item for item in _ORDER if any(item.lower() == mark.lower() for mark in found)]
    return known + [item for item in found if item.lower() not in {mark.lower() for mark in known}]


def split_cards(body: list[str]) -> tuple[list[list[str]], list[str]]:
    """Separate `####` card sections from the aggregate's map lines (root line, integrations, events)."""
    cards: list[list[str]] = []
    rest: list[str] = []
    current: list[str] | None = None
    for raw in body:
        line = raw.strip()
        if line.startswith(_CARD):
            current = [raw]
            cards.append(current)
            continue
        if current is not None and not raw.startswith((" ", "\t")) and line.lower().startswith(_LEAVES_CARD):
            current = None
        if current is None:
            rest.append(raw)
        else:
            current.append(raw)
    return cards, rest


def read_card(section: list[str]) -> ClassCard:
    card = ClassCard.from_heading(section[0].strip()[len(_CARD):])
    in_operations = False
    in_invariants = False
    last: Property | Operation | None = None
    for raw in section[1:]:
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
            card.invariants.append(line[2:].strip())
            continue
        if not _reads_note(line, last) and line.startswith(("+", "-")):
            last = card.add_member(line, in_operations)
    return card


def _reads_note(line: str, last: Property | Operation | None) -> bool:
    """A `-> call` under an operation or a `// description` under a member belongs to that member."""
    if line.startswith(_CALL) and isinstance(last, Operation):
        last.callees.append(line[len(_CALL):].strip())
        return True
    if line.startswith(_NOTE) and last is not None:
        last.description = line[len(_NOTE):].strip()
        return True
    return False


_REFERENCE = re.compile(r"^-?\s*(?:→|->)?\s*([A-Za-z][\w ·]*?)\s*\(by\s+([A-Za-z_]\w*)\s*\)")
_IDENT = re.compile(r"^[A-Za-z_]\w*$")
_REPOSITORY_OPERATIONS = re.compile(r"[/,]")
# Lines in an entity fence that belong to the aggregate's map, not to the class: integration arcs and event lists.
_MAP_LINES = ("- ", "→", "pattern:", "crosses:", "integrat", "direction:")


def card_from_sketch(heading: str, lines: list[str]) -> list[ClassCard]:
    """A sketch entity fence as cards: the entity itself, plus its repository when the fence names `repo:`.

    Same reading as the clean-engineering sketch: a line with an `->` under it, or with parameters, is an
    operation; a single word is a property; `Name <<Stereotype>>` is an owned member; `refs:` entries are
    other aggregates held by identity; `repo:` names the repository and its collection operations; a
    `+ name(parameters): Type` line is read as on a card, with the `->` calls under it."""
    return _SketchFence(heading, lines).cards()


class _SketchFence:
    """Reads one entity fence of a sketch, a line at a time, into the entity's card and its repository's."""

    def __init__(self, heading: str, lines: list[str]) -> None:
        self.card = ClassCard.from_heading(heading)
        self.found = [self.card]
        self.lines = [_without_note(raw) for raw in lines]
        self.index = 0
        self.last: Property | Operation | None = None

    def cards(self) -> list[ClassCard]:
        while self.index < len(self.lines):
            line = self.lines[self.index]
            self.index += 1
            if line and not line.startswith("```"):
                self._read(line)
        return self.found

    def _read(self, line: str) -> None:
        lower = line.lower()
        if lower.startswith(_INVARIANT):
            self.card.invariants.append(line.split(":", 1)[1].strip())
        elif lower.startswith("refs:"):
            self._read_references()
        elif lower.startswith("repo:"):
            self._read_repository(line.split(":", 1)[1].strip())
        elif line.startswith(_CALL) and isinstance(self.last, Operation):
            self.last.callees.append(line[len(_CALL):].strip())
        elif line.endswith(":") or line.startswith(_MAP_LINES):
            return
        elif line.startswith(("+", "-")):
            self.last = self.card.add_member(line, "(" in line)
        else:
            self.last = None
            _read_sketch_member(line, self.card.node, self._calls_below())

    def _read_references(self) -> None:
        while self.index < len(self.lines) and _REFERENCE.match(self.lines[self.index]):
            target, identity = _REFERENCE.match(self.lines[self.index]).groups()
            held = Property(identity, len(self.card.node.properties) + 1, target.split("·")[-1].strip())
            held.stereotype = "association"
            self.card.node.properties.append(held)
            self.index += 1

    def _read_repository(self, named: str) -> None:
        repository = ClassCard.from_heading(named if "<<" in named else f"{named} <<Repository>>")
        following = self.lines[self.index] if self.index < len(self.lines) else ""
        if following and not following.endswith(":"):
            for name in _REPOSITORY_OPERATIONS.split(following):
                name = name.strip().rstrip("()")
                if _IDENT.match(name):
                    repository.node.operations.append(Operation(name, len(repository.node.operations) + 1))
            self.index += 1
        self.found.append(repository)

    def _calls_below(self) -> list[str]:
        calls: list[str] = []
        while self.index < len(self.lines) and self.lines[self.index].startswith(_CALL):
            calls.append(self.lines[self.index][len(_CALL):].strip())
            self.index += 1
        return calls


def _without_note(raw: str) -> str:
    stripped = raw.strip()
    return "" if stripped.startswith(_NOTE) else stripped.split(_NOTE, 1)[0].strip()


def _read_sketch_member(line: str, node: OoadClass, arrows: list[str]) -> None:
    marks = stereotypes_in(line)
    tokens = plain_class_name(line).replace("()", " ").split()
    if not tokens:
        return
    if marks:
        member = tokens[0]
        owned = Property(member[0].lower() + member[1:], len(node.properties) + 1, member)
        owned.stereotype = "composition"
        node.properties.append(owned)
        return
    if arrows or len(tokens) > 1 or "(" in line:
        operation = Operation(
            tokens[0].split("(", 1)[0],
            len(node.operations) + 1,
            parameters=[token for token in tokens[1:] if _IDENT.match(token)],
        )
        operation.callees.extend(arrows)
        node.operations.append(operation)
        return
    node.properties.append(Property(tokens[0], len(node.properties) + 1))
