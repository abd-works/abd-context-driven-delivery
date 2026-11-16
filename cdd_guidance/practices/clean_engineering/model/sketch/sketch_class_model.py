"""Sketch channel — boxed class notation inside fenced sketch blocks."""

from __future__ import annotations

import re
import textwrap
from typing import List, Optional, Tuple

from cdd_guidance.practices.sketch_document.sketch_outline import SketchOutline
from harness.guidance.guidance import SketchLens
from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import marks_in
from cdd_guidance.practices.clean_engineering.model.operation import Operation, Parameter
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.type_refs import split_top_level

_NESTING_INDENT = 2
_SECTION_TITLE = "clean engineering:"
_TOP_MODULE_DEPTH = 3
_CLASS_DEPTH = 5
_DEEPEST_HEADING = 6
_MEMBER_INDENT = "  "
_FENCE = "```"
_MODULE_HEADING = re.compile(r"^([A-Za-z0-9_][\w./-]*)/$")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
_RELATIONSHIP_KINDS = frozenset({"composition", "aggregation", "association"})
# `Cart <<Aggregate Root>> : Basket, Auditable`: the name, its stereotypes, then its bases.
_CLASS = re.compile(r"^([A-Z][A-Za-z0-9]+)((?:\s*<<[^>]+>>)*)(?:\s*:\s*(.+))?$")
_BOLD_CLASS = re.compile(r"^\*\*([A-Z][A-Za-z0-9]+)\*\*$")
_MODULE = re.compile(r"Module:\**\s*`([^`]+)`", re.I)
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RETURN_TYPE = re.compile(
    r"^(void|string|number|bool|boolean|int|float|object|any|list|dict|str|None|Path)$"
    r"|^[A-Z][A-Za-z0-9]*$"
)
_PROSE_MIN_WORDS = 5
"""A line under a class this long with ordinary English words in it is prose, which ends the class's card."""
_PROSE = re.compile(
    r"\b(the|and|is|are|a|an|of|to|for|that|this|with|from|into|each|same|only|like)\b",
    re.I,
)


class SketchProperty(Property):
    """A property in the sketch notation: its name, then its notes."""

    def sketch_lines(self) -> List[str]:
        """Its name, then a `//` line for its relationship's stereotype, its origin, cardinality, and invariants."""
        stereotype = [f"<<{self.stereotype}>>"] if self.stereotype in _RELATIONSHIP_KINDS else []
        return [self.name, *(f"{_MEMBER_INDENT}// {note}" for note in stereotype + self.notes())]


class SketchOperation(Operation):
    """An operation in the sketch notation: `returnType name param param`, then its interactions and invariants."""

    def sketch_lines(self) -> List[str]:
        """Its line, then a `->` line for each interaction and a `//` line for each invariant."""
        return [
            self._signature_line(),
            *(f"{_MEMBER_INDENT}-> {callee}" for callee in self.callees),
            *(f"{_MEMBER_INDENT}// {note}" for note in self.invariant_lines()),
        ]

    def _signature_line(self) -> str:
        """`returnType name param param`; a bare name gets `()` so it is not read back as a property."""
        words = [self.return_type] if self.return_type and _is_return_type(self.return_type) else []
        words.append(self.name)
        words.extend(parameter.name for parameter in self.parameters)
        if len(words) == 1 and not self.callees:
            return f"{self.name}()"
        return " ".join(words)


class SketchOoadClass(OoadClass):
    """A class in the sketch notation: its heading, then a fence of its members. It reads its own member lines and
    writes them back; each member spells its own lines."""

    property_type = SketchProperty
    operation_type = SketchOperation

    def sketch_lines(self, depth: int) -> List[str]:
        marks = "".join(f" <<{item}>>" for item in self.stereotypes)
        bases = f" : {', '.join(self.bases)}" if self.bases else ""
        lines = [f"{'#' * depth} {self.name}{marks}{bases}", ""]
        members = [line for member in [*self.properties, *self.operations] for line in member.sketch_lines()]
        if members:
            lines.extend([_FENCE, *members, _FENCE, ""])
        return lines

    def merge(self, incoming: OoadClass) -> None:
        """Take what a second card of the same class adds: members, bases, and stereotypes it does not have yet."""
        seen_props = {member.name for member in self.properties}
        for prop in incoming.properties:
            if prop.name not in seen_props:
                self.properties.append(prop)
                seen_props.add(prop.name)
        seen_ops = {member.name for member in self.operations}
        for operation in incoming.operations:
            if operation.name not in seen_ops:
                self.operations.append(operation)
                seen_ops.add(operation.name)
        self.bases.extend(base for base in incoming.bases if base not in self.bases)
        self.stereotypes.extend(stereotype for stereotype in incoming.stereotypes if stereotype not in self.stereotypes)
        if incoming.intent and not self.intent:
            self.intent = incoming.intent

    def read_member(self, lines: list[str], index: int) -> int:
        """The member written at lines[index] in the boxed notation, with the arrows and notes under it; the index
        after them."""
        stripped = lines[index]
        nested = _Nest.taken(lines, index + 1)
        tokens = stripped.replace("()", " ").replace("-->", " ").split()
        if not tokens:
            return nested.end
        if stripped.endswith("()") or self._is_operation_line(tokens, nested.arrows):
            self.operations.append(self._operation_under(tokens, nested))
        else:
            self.properties.append(self._property_under(tokens, nested))
        return nested.end

    def _operation_under(self, tokens: list[str], nested: "_Nest") -> Operation:
        """The operation a member line writes, calling each arrow under it and holding each note as an invariant."""
        operation = self._operation_from(tokens)
        for callee in nested.arrows:
            if callee not in operation.callees:
                operation.callees.append(callee)
        for note in nested.notes:
            operation.add_invariant(note)
        return operation

    def _property_under(self, tokens: list[str], nested: "_Nest") -> Property:
        prop = self.property_type(name=tokens[0])
        for note in nested.notes:
            prop.take_note(note)
        return prop

    def read_uml_member(self, lines: list[str], index: int, owner: Operation | Property) -> int:
        """The `+ name(args): type` member owner, then the arrows and notes under it; the index after them."""
        (self.operations if isinstance(owner, Operation) else self.properties).append(owner)
        index += 1
        while index < len(lines):
            stripped = lines[index].strip()
            if stripped and (self._ends_uml_member(stripped) or not self._take_uml_note(stripped, owner)):
                break
            index += 1
        return index

    def _ends_uml_member(self, stripped: str) -> bool:
        """A rule, the next class's bold name, or the next member line ends the lines under a member."""
        return _is_rule(stripped) or bool(_BOLD_CLASS.match(stripped)) or _uml_member(stripped) is not None

    def _take_uml_note(self, stripped: str, owner: Operation | Property) -> bool:
        """Take a `->` call, a `//` note, or a bare invariant name written under owner; false for any other line."""
        if stripped.startswith("->"):
            callee = stripped[2:].strip()
            if callee and isinstance(owner, Operation) and callee not in owner.callees:
                owner.callees.append(callee)
            return True
        if stripped.startswith("//"):
            owner.add_invariant(stripped[2:].strip())
            return True
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", stripped):
            owner.add_invariant(stripped)
            return True
        return False

    def _is_operation_line(self, tokens: list[str], arrows: list[str]) -> bool:
        if arrows:
            return True
        if tokens[0] == self.name:
            return True
        return len(tokens) > 1

    def _operation_from(self, tokens: list[str]) -> Operation:
        if tokens[0] == self.name:
            name, rest, return_type = tokens[0], tokens[1:], ""
        elif len(tokens) >= 2 and _is_return_type(tokens[0]):
            return_type, name, rest = tokens[0], tokens[1], tokens[2:]
        else:
            name, rest, return_type = tokens[0], tokens[1:], ""
        operation = self.operation_type(name=name, return_type=return_type)
        for order, token in enumerate(rest, start=1):
            if _IDENT.match(token):
                operation.parameters.append(Parameter(name=token, sequential_order=order))
        return operation


class SketchModule(Module):
    """A module in the sketch notation: a `name/` heading, its own classes, then its nested modules, so each class
    is read back under its module. It reads the class cards written under its heading."""

    class_type = SketchOoadClass

    def sketch_lines(self, depth: int) -> List[str]:
        lines = [f"{'#' * min(depth, _DEEPEST_HEADING)} {self.name}/", ""]
        for oclass in self.classes:
            lines.extend(oclass.sketch_lines(min(max(_CLASS_DEPTH, depth + 1), _DEEPEST_HEADING)))
        for nested in self.modules:
            lines.extend(nested.sketch_lines(depth + 1))
        return lines

    def read_classes(self, lines: List[str]) -> None:
        """The class cards written under this module's heading; a second card of a class it holds adds to it."""
        for oclass in _SketchCards(textwrap.dedent("\n".join(lines))).classes():
            existing = next((known for known in self.classes if known.name == oclass.name), None)
            if existing is None:
                self.classes.append(oclass)
                continue
            existing.merge(oclass)



class _SketchCards:
    """The class cards one module's text writes, read in order, each line adding to the card being read: UML cards,
    `**Session**` with indented `+ name(args): type` lines, when any line is such a heading; else plain cards, a
    `Cart <<Aggregate Root>> : Basket` heading and its member lines."""

    def __init__(self, text: str) -> None:
        written = text.splitlines()
        self._uml = any(_BOLD_CLASS.match(line.strip()) for line in written)
        self._lines = written if self._uml else [line.strip() for line in written if line.strip() and line.strip() != "Fidelity:"]
        self._classes: list[SketchOoadClass] = []
        self._current: SketchOoadClass | None = None

    def classes(self) -> list[SketchOoadClass]:
        """Every card the text writes, in order."""
        read_line = self._read_uml_line if self._uml else self._read_card_line
        index = 0
        while index < len(self._lines):
            index = read_line(index)
        return self._classes

    def _read_card_line(self, index: int) -> int:
        """Read the line at index into the cards, and answer the index of the next line to read."""
        stripped = self._lines[index]
        if self._closes_card(stripped):
            self._current = None
            return index + 1
        if stripped.startswith(("//", "#")):
            return index + 1
        headed = _CLASS.match(stripped)
        if headed and (self._current is None or headed.group(1) != self._current.name):
            self._start_card(self._class_headed(headed))
            return index + 1
        if self._current is not None:
            return self._current.read_member(self._lines, index)
        return index + 1

    def _read_uml_line(self, index: int) -> int:
        """Read the UML card line at index into the cards, and answer the index of the next line to read."""
        line = self._lines[index]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if not stripped or stripped.startswith(("//", "#")) or _is_rule(stripped):
            return index + 1
        heading = _BOLD_CLASS.match(stripped) if indent == 0 else None
        if heading:
            self._start_card(SketchOoadClass(name=heading.group(1), sequential_order=len(self._classes) + 1))
            return index + 1
        if self._current is None or indent == 0:
            return index + 1
        member = _uml_member(stripped)
        if member is not None:
            return self._current.read_uml_member(self._lines, index, member)
        if self._current.operations and re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", stripped):
            self._current.operations[-1].add_invariant(stripped)
        return index + 1

    def _start_card(self, oclass: SketchOoadClass) -> None:
        self._current = oclass
        self._classes.append(oclass)

    def _closes_card(self, stripped: str) -> bool:
        """A fence or a `----` rule ends the card being read, and so does a line of prose under it."""
        if stripped == "----" or stripped.startswith(_FENCE):
            return True
        return self._current is not None and not stripped.startswith(("//", "#")) and self._is_prose(stripped)

    def _class_headed(self, headed: re.Match) -> SketchOoadClass:
        """The class a `Cart <<Aggregate Root>> : Basket` heading names, with its stereotypes and bases."""
        oclass = SketchOoadClass(name=headed.group(1), sequential_order=len(self._classes) + 1)
        oclass.stereotypes = marks_in(headed.group(2) or "")
        oclass.bases = [base.strip() for base in split_top_level(headed.group(3) or "") if base.strip()]
        return oclass

    def _is_prose(self, stripped: str) -> bool:
        if stripped.startswith("->") or "-->" in stripped:
            return False
        if _CLASS.match(stripped):
            return False
        tokens = stripped.split()
        if tokens and all(_IDENT.match(token) for token in tokens):
            return False
        return bool(_PROSE.search(stripped)) and len(tokens) >= _PROSE_MIN_WORDS


class SketchCleanEngineeringModel(CleanEngineeringModel):
    module_type = SketchModule
    # The Clean Engineering section of a sketch, opened by either of its headings; the practice holds this lens.
    lens = SketchLens(("ce:", _SECTION_TITLE))

    def parse(self, text: str) -> "SketchCleanEngineeringModel":
        """Read the sketch's clean engineering section into this model's own modules, and return it."""
        declared = _MODULE.search(text)
        self.name = declared.group(1) if declared else "KnowledgeGraph"
        self.modules = self._modules_in(SketchOutline(text, _NESTING_INDENT).body_for(self.lens))
        return self

    def render(self, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        """The `clean engineering:` section of a sketch; in previous, it replaces the section already there."""
        if canonical is not self:
            self.translate_from(canonical)
        section = self.section_lines()
        if not previous:
            return "\n".join(section) + "\n"
        return self._with_section_replaced(previous, section)

    def section_lines(self) -> List[str]:
        lines = [f"## {_SECTION_TITLE}", "", f"**Module:** `{self.name}`", ""]
        for module in self.modules:
            lines.extend(module.sketch_lines(_TOP_MODULE_DEPTH))
        return lines

    def _modules_in(self, body: str) -> List[Module]:
        """Each `name/` line opens a module, nested under the one above it when written further in. Classes written
        before any module line belong to a module named after the sketch."""
        loose = SketchModule(name=self.name, sequential_order=1)
        opened = _OpenModules()
        owner = loose
        section: List[str] = []
        for raw in body.splitlines():
            heading = _MODULE_HEADING.match(raw.strip())
            if heading is None:
                section.append(raw)
                continue
            owner.read_classes(section)
            section = []
            owner = opened.open(heading.group(1), len(raw) - len(raw.lstrip(" ")))
        owner.read_classes(section)
        return ([loose] if loose.classes else []) + opened.top

    def _with_section_replaced(self, previous: str, section: List[str]) -> str:
        """previous with its clean engineering section swapped for section, or with section added at the end."""
        lines = previous.splitlines()
        span = self._section_span(lines)
        if span is None:
            return previous.rstrip("\n") + "\n\n" + "\n".join(section) + "\n"
        first, last = span
        return "\n".join(lines[:first] + section + lines[last:]).rstrip("\n") + "\n"

    def _section_span(self, lines: List[str]) -> Optional[Tuple[int, int]]:
        """Where the clean engineering section starts in a sketch and the line where the next peer heading ends it."""
        first: Optional[int] = None
        depth = 0
        fenced = False
        for index, raw in enumerate(lines):
            if raw.strip().startswith(_FENCE):
                fenced = not fenced
                continue
            heading = None if fenced else _HEADING.match(raw.strip())
            if heading is None:
                continue
            if first is None and self.lens.opens(heading.group(2)):
                first, depth = index, len(heading.group(1))
            elif first is not None and len(heading.group(1)) <= depth:
                return first, index
        return (first, len(lines)) if first is not None else None


class _OpenModules:
    """The modules a sketch's `name/` lines have opened so far: the top ones, and the chain of modules, by indent,
    that the next line nests under."""

    def __init__(self) -> None:
        self.top: List[Module] = []
        self._chain: List[Tuple[int, SketchModule]] = []

    def open(self, name: str, indent: int) -> SketchModule:
        """A module named on a line written indent spaces in, nested in the nearest module written further out."""
        while self._chain and self._chain[-1][0] >= indent:
            self._chain.pop()
        siblings = self._chain[-1][1].modules if self._chain else self.top
        module = SketchModule(name=name, sequential_order=len(siblings) + 1)
        siblings.append(module)
        self._chain.append((indent, module))
        return module


def _is_rule(stripped: str) -> bool:
    return len(stripped) >= 4 and set(stripped) <= {"-"}


def _uml_member(line: str) -> Operation | Property | None:
    """The operation or typed property a `+` or `-` member line writes; none for any other line."""
    if not line.startswith(("+", "-")):
        return None
    signature = line[1:].strip()
    return SketchOperation.from_signature(signature) or SketchProperty.from_signature(signature)


class _Nest:
    """The `->` arrows and `//` notes written under one member, and the line after them."""

    def __init__(self, end: int, arrows: list[str], notes: list[str]) -> None:
        self.end = end
        self.arrows = arrows
        self.notes = notes

    @classmethod
    def taken(cls, lines: list[str], start: int) -> "_Nest":
        arrows: list[str] = []
        notes: list[str] = []
        index = start
        while index < len(lines):
            stripped = lines[index]
            if stripped.startswith("->"):
                callee = stripped[2:].strip()
                if callee:
                    arrows.append(callee)
            elif stripped.startswith("//"):
                notes.append(stripped[2:].strip())
            else:
                break
            index += 1
        return cls(index, arrows, notes)


def _is_return_type(token: str) -> bool:
    return bool(_RETURN_TYPE.match(token))
