"""Class cards under an aggregate — the model fidelity's `####` sections in CE class notation."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

_CARD = "#### "
_PROPERTIES = "------"
_OPERATIONS = "----"
_LEAVES_CARD = ("integrations:", "emits events:", "consumes events:", "### ")
_STEREOTYPE = re.compile(r"<<\s*([^>]+?)\s*>>")
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

    @property
    def is_root(self) -> bool:
        return any(item.lower() == _ROOT for item in self.stereotypes)

    @property
    def is_repository(self) -> bool:
        return any(item.lower() == _REPOSITORY for item in self.stereotypes)

    def lines(self) -> list[str]:
        written = [f"{_CARD}{self.node.name} {' '.join(f'<<{item}>>' for item in self.stereotypes)}".rstrip(), ""]
        written.append(_PROPERTIES)
        for prop in plain_properties(self.node):
            access = "-" if prop.access == "private" else "+"
            kind = f"<< {prop.stereotype} >> " if prop.stereotype else ""
            typed = f": {prop.type_hint}" if prop.type_hint else ""
            written.append(f"{access} {kind}{prop.name}{typed}")
            if prop.description:
                written.append(f"\t// {prop.description}")
        written.append(_OPERATIONS)
        for operation in self.node.operations:
            access = "-" if getattr(operation, "access", "") == "private" else "+"
            parameters = ", ".join(item.save() for item in operation.parameters)
            returned = f": {operation.return_type}" if operation.return_type else ""
            written.append(f"{access} {operation.name}({parameters}){returned}")
            for callee in operation.callees:
                written.append(f"\t-> {callee}")
            if operation.description:
                written.append(f"\t// {operation.description}")
        if self.invariants:
            written.extend(["", "**Invariants**", ""])
            written.extend(f"- {item}" for item in self.invariants)
        written.append("")
        return written


def plain_properties(node: OoadClass) -> list[Property]:
    """What the class holds — not the events or invariant objects DDD hangs on the same list."""
    from cdd_guidance.practices.ddd.model.nodes import DomainEvent, InvariantObject

    return [
        item for item in node.properties
        if isinstance(item, Property) and not isinstance(item, (DomainEvent, InvariantObject))
    ]


def stereotypes_in(text: str) -> list[str]:
    return [item.strip() for item in _STEREOTYPE.findall(text)]


def plain_class_name(text: str) -> str:
    return _STEREOTYPE.sub("", text).replace("**", "").replace("`", "").strip()


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


def read_card(section: list[str], node_type_for) -> ClassCard:
    heading = section[0].strip()[len(_CARD):]
    marks = stereotypes_in(heading)
    node_type = node_type_for(heading)
    if not isinstance(node_type, type) or not issubclass(node_type, OoadClass):
        node_type = OoadClass
    node = node_type(plain_class_name(heading), 0)
    card = ClassCard(node, ordered_stereotypes(marks))
    in_operations = False
    in_invariants = False
    last: Property | Operation | None = None
    for raw in section[1:]:
        line = raw.strip()
        if not line:
            continue
        if line == _PROPERTIES:
            in_operations = False
            continue
        if line == _OPERATIONS:
            in_operations = True
            continue
        if line.lower().startswith("**invariants**"):
            in_invariants = True
            continue
        if in_invariants and line.startswith("- "):
            card.invariants.append(line[2:].strip())
            continue
        if line.startswith("->") and isinstance(last, Operation):
            last.callees.append(line[2:].strip())
            continue
        if line.startswith("//") and last is not None:
            last.description = line[2:].strip()
            continue
        if not line.startswith(("+", "-")):
            continue
        last = _read_member(line, node, in_operations)
    return card


def _read_member(line: str, node: OoadClass, in_operations: bool) -> Property | Operation | None:
    operation = _OPERATION.match(line)
    if operation and (in_operations or "(" in line.split(":", 1)[0]):
        access, _kind, name, parameters, returned = operation.groups()
        found = Operation(
            name,
            len(node.operations) + 1,
            return_type=(returned or "").strip(),
            parameters=[item.strip() for item in parameters.split(",") if item.strip()],
        )
        found.access = "private" if access == "-" else "public"
        node.operations.append(found)
        return found
    prop = _PROPERTY.match(line)
    if prop:
        access, kind, name, type_hint = prop.groups()
        found = Property(name, len(node.properties) + 1, (type_hint or "").strip())
        found.stereotype = (kind or "").lower()
        found.access = "private" if access == "-" else "both"
        node.properties.append(found)
        return found
    return None


_REFERENCE = re.compile(r"^-?\s*(?:→|->)?\s*([A-Za-z][\w ·]*?)\s*\(by\s+([A-Za-z_]\w*)\s*\)")
_IDENT = re.compile(r"^[A-Za-z_]\w*$")
_REPOSITORY_OPERATIONS = re.compile(r"[/,]")


def card_from_sketch(heading: str, lines: list[str], node_type_for) -> list[ClassCard]:
    """A sketch entity fence as cards: the entity itself, plus its repository when the fence names `repo:`.

    Same reading as the clean-engineering sketch: a line with an `->` under it, or with parameters, is an
    operation; a single word is a property; `Name <<Stereotype>>` is an owned member; `refs:` entries are
    other aggregates held by identity; `repo:` names the repository and its collection operations."""
    card = read_card([f"{_CARD}{heading}"], node_type_for)
    node = card.node
    cards = [card]
    stripped = [raw.strip() for raw in lines]
    index = 0
    while index < len(stripped):
        line = stripped[index].split("//", 1)[0].strip() if not stripped[index].startswith("//") else ""
        index += 1
        if not line or line.startswith("```"):
            continue
        lower = line.lower()
        if lower.startswith("invariant:"):
            card.invariants.append(line.split(":", 1)[1].strip())
            continue
        if lower.startswith("refs:"):
            while index < len(stripped) and _REFERENCE.match(stripped[index]):
                target, identity = _REFERENCE.match(stripped[index]).groups()
                held = Property(identity, len(node.properties) + 1, target.split("·")[-1].strip())
                held.stereotype = "association"
                node.properties.append(held)
                index += 1
            continue
        if lower.startswith("repo:"):
            named = line.split(":", 1)[1].strip()
            repository = read_card([f"{_CARD}{named if '<<' in named else named + ' <<Repository>>'}"], node_type_for)
            if index < len(stripped) and stripped[index] and not stripped[index].endswith(":"):
                for name in _REPOSITORY_OPERATIONS.split(stripped[index]):
                    name = name.strip().rstrip("()")
                    if _IDENT.match(name):
                        repository.node.operations.append(Operation(name, len(repository.node.operations) + 1))
                index += 1
            cards.append(repository)
            continue
        if line.endswith(":") or line.startswith(("- ", "→", "pattern:", "crosses:", "integrat", "direction:")):
            continue
        if line.startswith(("+", "-")):
            _read_member(line, node, "(" in line)
            continue
        arrows: list[str] = []
        while index < len(stripped) and stripped[index].startswith("->"):
            arrows.append(stripped[index][2:].strip())
            index += 1
        _read_sketch_member(line, node, arrows)
    return cards


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
