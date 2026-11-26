"""ClassCard and SketchFence. The one class-card notation Clean Engineering and DDD both read and write: a class's
members under its heading, read onto a class and written from one.

    + Cart(customer: Customer)          the constructor line, which a card that writes none leaves out
    ------                              properties below
    + << composition >> lines: Line[]   a property, with the relationship its mark names
    	// a note on the property
    ----                                operations below
    + addLine(book: Book): Line
    	-> Line.create                  a call the operation makes
    	// an invariant the operation keeps
    - recalculate()                     a private operation, read as `_recalculate`
    ---<<runs>>--> Git                  a dependency on another class

A sketch writes a class's members more loosely, in a fence under its heading (*SketchFence*).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Tuple

from cdd_guidance.practices.clean_engineering.model.base_class_model import is_interface_name
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marks_in, without_marks
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.source_code import parse_arrow_line

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass

PROPERTIES = "------"
OPERATIONS = "----"
CALL = "->"
NOTE = "//"
_RELATIONSHIP_KINDS = {"composition", "aggregation", "association"}


def _property_in(line: str) -> Optional[Property]:
    """The property a member line of a class card writes; none for an operation, or for a mark that names no
    relationship. An optional property may be written `name?: Type` or `name: Type | null`."""
    bare, kind = _without_access(line)
    if ("<<" in line and kind is None) or not bare or re.match(r"^_?\w+\s*\(", bare):
        return None
    prop = Property.from_signature(bare)
    if prop is None:
        return Property(name=bare) if re.match(r"^\w+$", bare) else None
    if kind:
        prop.stereotype = kind
    return prop


def _operation_in(line: str) -> Optional[Operation]:
    """The operation a member line of a class card writes; a `- ` line is private, so its name gets a leading
    underscore."""
    private = line.startswith("- ")
    body, _kind = _without_access(line[2:].strip() if private else line)
    operation = Operation.from_signature(body)
    if operation is not None and private and not operation.name.startswith("_"):
        operation.name = f"_{operation.name}"
    return operation


# The bold line a card lists the invariants no single member governs under, one `- ` bullet each.
INVARIANTS_LIST = "**Invariants**"


class ClassCard:
    """The members of one class card in the class-card notation: its intent and constructor above ``------``, its
    properties between ``------`` and ``----``, its operations below, each with the calls and notes written under it,
    the dependencies it names, and, under **Invariants**, the invariants no single member governs. A card that writes no constructor line (``writes_constructor``), as a DDD building
    block's, starts at ``------``."""

    def __init__(self, body_lines: List[str], writes_constructor: bool = True) -> None:
        self._lines = list(body_lines)
        self._writes_constructor = writes_constructor

    ## reading

    def read_into(self, oclass: OoadClass) -> None:
        """Read the card onto oclass: its intent, its constructor, its properties and operations, the dependencies it
        names, and the invariants its **Invariants** list names."""
        at = next((index for index, line in enumerate(self._lines) if line.strip().lower().startswith(INVARIANTS_LIST.lower())), len(self._lines))
        oclass.invariants = [line.strip()[2:].strip() for line in self._lines[at + 1:] if line.strip().startswith("- ")]
        text_lines, dependencies = Relationship.split_off(self._lines[:at])
        head, members = _split_once(r"(?m)^-{6}\s*$", "\n".join(text_lines))
        props_text, ops_text = _split_once(r"(?m)^-{4}\s*$", members)
        intent, constructor_line, constructor_notes = self._read_head(head)
        oclass.intent = intent
        oclass.properties = self._read_properties(props_text)
        for prop in oclass.properties:
            prop.arrow.derive()
        oclass.operations = self._constructors(constructor_line, constructor_notes) + self._read_operations(ops_text)
        for relationship in dependencies:
            oclass.arrows.place(relationship)

    def _read_head(self, head: str) -> Tuple[str, str, List[str]]:
        """The card's intent, its constructor line, and the notes under the constructor, from the part above
        ``------``. The intent is the class's language: its definition and the bullets of the terms it owns, which a
        model card writes above the constructor, so a ``-`` bullet there is language, not a private member."""
        intent_lines: List[str] = []
        notes: List[str] = []
        constructor_line = ""
        seen_signature = False
        for line in head.splitlines():
            stripped = line.strip()
            if stripped.startswith(NOTE) and seen_signature:
                notes.append(stripped[2:].strip())
            if not stripped and not seen_signature:
                intent_lines.append("")
            if not stripped or stripped.startswith(NOTE):
                continue
            if _SIGNATURE.match(stripped):
                seen_signature = True
                constructor_line = stripped
            elif not seen_signature:
                intent_lines.append(stripped)
        return _paragraphs(intent_lines), constructor_line, notes

    def _constructors(self, constructor_line: str, notes: List[str]) -> List[Operation]:
        constructors = self._read_operations(constructor_line) if constructor_line else []
        for constructor in constructors:
            for note in notes:
                constructor.add_invariant(note)
        return constructors

    def _read_properties(self, text: str) -> List[Property]:
        props: List[Property] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith((NOTE, CALL)):
                _note_on_property(props[-1] if props else None, stripped)
                continue
            prop = _property_in(stripped)
            if prop is not None:
                props.append(prop)
        return props

    def _read_operations(self, text: str) -> List[Operation]:
        ops: List[Operation] = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith((NOTE, CALL, "→")):
                _note_on_operation(ops[-1] if ops else None, stripped)
                continue
            operation = _operation_in(stripped)
            if operation is not None:
                ops.append(operation)
        return ops

    ## writing

    def lines_of(self, oclass: OoadClass, properties: Optional[List[Property]] = None) -> List[str]:
        """oclass's members as the card writes them: properties, every one of oclass's when none are given."""
        constructors = [operation for operation in oclass.operations if _builds(oclass, operation)]
        lines: List[str] = []
        if self._writes_constructor:
            lines.append(_public_line(_constructor_line(oclass, constructors)))
            for operation in constructors:
                lines.extend(_notes_under(operation.callees, operation.invariant_lines()))
        lines.append(PROPERTIES)
        lines.extend(self.property_lines(oclass.properties if properties is None else properties))
        lines.append(OPERATIONS)
        lines.extend(self.operation_lines(oclass))
        lines.extend(line for item in oclass.dependencies for line in item.lines())
        if oclass.invariants:
            lines.extend(["", INVARIANTS_LIST, ""])
            lines.extend(f"- {item}" for item in oclass.invariants)
        return lines

    def property_lines(self, properties: List[Property]) -> List[str]:
        """Each property's line, with the calls and notes under it."""
        return [line for prop in properties for line in (property_line(prop), *_notes_under(prop.callees, prop.notes()))]

    def operation_lines(self, oclass: OoadClass) -> List[str]:
        """Each of oclass's operations but its constructor, with the calls and invariants under it; an interface's
        private operations are no part of it."""
        lines: List[str] = []
        for operation in oclass.operations:
            if _builds(oclass, operation) or (is_interface_name(oclass.name) and operation.name.startswith("_")):
                continue
            lines.append(_public_line(operation.save()))
            lines.extend(_notes_under(operation.callees, operation.invariant_lines()))
        return lines


def _paragraphs(lines: List[str]) -> str:
    """lines as one text, each run of blank lines between them kept as one paragraph break, none at either end."""
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return text.strip("\n")


def property_line(prop: Property) -> str:
    """A property as a card writes it, with the << composition|aggregation|association >> written or drawn on it; a
    property nobody marked is written plain."""
    kind = (prop.stereotype or "").lower()
    mark = f"<< {kind} >> " if kind in _RELATIONSHIP_KINDS else ""
    return _public_line(f"{mark}{prop.save()}")


def _builds(oclass: OoadClass, operation: Operation) -> bool:
    """Whether operation is the class's constructor, named after the class or as a code language names one."""
    return operation.name == oclass.name or operation.is_constructor


def _constructor_line(oclass: OoadClass, constructors: List[Operation]) -> str:
    """Markdown names the constructor after the class, with its parameters and no return type; a class with none is
    built from its properties."""
    if constructors:
        operation = constructors[0]
        if not operation.is_constructor:
            return operation.save()
        return f"{oclass.name}({', '.join(parameter.save() for parameter in operation.parameters)})"
    params = ", ".join(f"{prop.name}: {prop.type_hint}" if prop.type_hint else prop.name for prop in oclass.properties)
    return f"{oclass.name}({params})"


def _notes_under(callees: List[str], notes: List[str]) -> List[str]:
    """The calls and notes written under a member, indented."""
    return [f"\t{CALL} {callee}" for callee in callees] + [f"\t{NOTE} {note}" for note in notes]


def _public_line(body: str) -> str:
    """Public members lead with +. A leading - is already the private mark."""
    return body if body.startswith(("+", "-")) else f"+ {body}"


def _without_access(line: str) -> Tuple[str, Optional[str]]:
    """A member line without its leading `+` and its `<< composition >>` mark, and the relationship kind that mark
    names: composition, aggregation, association, or none."""
    if line.startswith("+"):
        line = line[1:].strip()
    marked = re.match(r"^<<\s*(\w+)\s*>>\s*", line)
    if marked is None:
        return line, None
    kind = marked.group(1).lower()
    return line[marked.end():].strip(), kind if kind in _RELATIONSHIP_KINDS else None


def _note_on_property(prop: Optional[Property], stripped: str) -> None:
    """A `//` note or `->` call written under the property above it."""
    if prop is None:
        return
    if stripped.startswith(NOTE):
        prop.take_note(stripped[2:])
    else:
        prop.callees.append(stripped[2:].strip())


def _note_on_operation(operation: Optional[Operation], stripped: str) -> None:
    """A `//` invariant or `->` call written under the operation above it."""
    if operation is None:
        return
    if stripped.startswith(NOTE):
        operation.add_invariant(stripped[2:])
        return
    arrow = parse_arrow_line(stripped)
    callee = arrow[1] if arrow else stripped[2:].strip()
    if callee and callee not in operation.callees:
        operation.callees.append(callee)


def _split_once(separator: str, text: str) -> Tuple[str, str]:
    """The text before the first separator line and the text after it; all of it before when there is none."""
    parts = re.split(separator, text, maxsplit=1)
    return parts[0], parts[1] if len(parts) > 1 else ""


# A constructor or member signature above ``------``: a ``+`` line, a ``-`` private member named straight before its
# parentheses (``- _build(…)``), or a bare call ``Name(…)`` / ``new Name(…)``. A ``- `` bullet of prose, such as a
# term's language, is none of these.
_SIGNATURE = re.compile(r"^(?:\+|-\s*_?\w+\(|(?:new\s+)?\w+\()")
_REFERENCE = re.compile(r"^-?\s*(?:→|->)?\s*([A-Za-z][\w ·]*?)\s*\(by\s+([A-Za-z_]\w*)\s*\)")
_IDENT = re.compile(r"^[A-Za-z_]\w*$")
_REPOSITORY_OPERATIONS = re.compile(r"[/,]")
# Lines in a fence that belong to a map, not to the class: integration arcs and event lists.
_MAP_LINES = ("- ", "→", "pattern:", "crosses:", "integrat", "direction:")
_INVARIANT = "invariant:"


@dataclass
class FenceRead:
    """What a sketch fence says beyond the class's members: the invariants it lists, and each repository it names
    with the collection operations the line below lists."""

    invariants: List[str] = field(default_factory=list)
    repositories: List[Tuple[str, List[str]]] = field(default_factory=list)


class SketchFence:
    """The sketch fence under a class's heading, read line by line onto the class: `invariant:` lines are its
    invariants; `refs:` entries other classes it holds by identity; `repo:` a repository that keeps it, with the
    collection operations the line below lists; a `-> call` under an operation one of its calls; a member line in the
    class-card notation a member as on a card; anything else a sketch member: `Name <<Stereotype>>` an owned member, a
    line with calls under it or with parameters an operation, a single word a property."""

    def __init__(self, lines: List[str]) -> None:
        self._lines = [self._without_note(raw) for raw in lines]
        self._index = 0
        self._last: Property | Operation | None = None

    def read_into(self, oclass: OoadClass) -> FenceRead:
        """Read every line onto oclass; answer the invariants and repositories the fence names."""
        read = FenceRead()
        while self._index < len(self._lines):
            line = self._lines[self._index]
            self._index += 1
            if line and not line.startswith("```"):
                self._read_line(oclass, line, read)
        return read

    def _read_line(self, oclass: OoadClass, line: str, read: FenceRead) -> None:
        lower = line.lower()
        if lower.startswith(_INVARIANT):
            read.invariants.append(line.split(":", 1)[1].strip())
            return
        if lower.startswith("refs:"):
            self._read_references(oclass)
            return
        if lower.startswith("repo:"):
            read.repositories.append(self._repository(line.split(":", 1)[1].strip()))
            return
        if line.startswith(CALL) and isinstance(self._last, Operation):
            self._last.callees.append(line[len(CALL):].strip())
            return
        if line.endswith(":") or line.startswith(_MAP_LINES):
            return
        if line.startswith(("+", "-")):
            self._last = self._member(oclass, line)
            return
        self._last = None
        self._add_sketch_member(oclass, line, self._calls_below())

    def _member(self, oclass: OoadClass, line: str) -> Property | Operation | None:
        """A member line in the class-card notation, added to oclass: an operation when it has parameters."""
        if "(" in line:
            operation = _operation_in(line)
            if operation is not None:
                operation.sequential_order = len(oclass.operations) + 1
                oclass.operations.append(operation)
            return operation
        prop = _property_in(line)
        if prop is not None:
            prop.sequential_order = len(oclass.properties) + 1
            oclass.properties.append(prop)
        return prop

    def _add_sketch_member(self, oclass: OoadClass, line: str, calls: List[str]) -> None:
        tokens = without_marks(line.replace("**", "").replace("`", "")).replace("()", " ").split()
        if not tokens:
            return
        if marks_in(line):
            owned = Property(tokens[0][0].lower() + tokens[0][1:], len(oclass.properties) + 1, tokens[0])
            owned.stereotype = "composition"
            oclass.properties.append(owned)
            return
        if calls or len(tokens) > 1 or "(" in line:
            operation = Operation(tokens[0].split("(", 1)[0], len(oclass.operations) + 1)
            operation.take_parameters([token for token in tokens[1:] if _IDENT.match(token)])
            operation.callees.extend(calls)
            oclass.operations.append(operation)
            return
        oclass.properties.append(Property(tokens[0], len(oclass.properties) + 1))

    def _read_references(self, oclass: OoadClass) -> None:
        """The `refs:` entries below: each another class oclass holds by its identity."""
        while self._index < len(self._lines) and _REFERENCE.match(self._lines[self._index]):
            target, identity = _REFERENCE.match(self._lines[self._index]).groups()
            held = Property(identity, len(oclass.properties) + 1, target.split("·")[-1].strip())
            held.stereotype = "association"
            oclass.properties.append(held)
            self._index += 1

    def _repository(self, named: str) -> Tuple[str, List[str]]:
        """The repository a `repo:` line names, with the collection operations the line below lists."""
        following = self._lines[self._index] if self._index < len(self._lines) else ""
        if not following or following.endswith(":"):
            return named, []
        self._index += 1
        names = (part.strip().rstrip("()") for part in _REPOSITORY_OPERATIONS.split(following))
        return named, [name for name in names if _IDENT.match(name)]

    def _calls_below(self) -> List[str]:
        calls: List[str] = []
        while self._index < len(self._lines) and self._lines[self._index].startswith(CALL):
            calls.append(self._lines[self._index][len(CALL):].strip())
            self._index += 1
        return calls

    def _without_note(self, raw: str) -> str:
        stripped = raw.strip()
        return "" if stripped.startswith(NOTE) else stripped.split(NOTE, 1)[0].strip()
