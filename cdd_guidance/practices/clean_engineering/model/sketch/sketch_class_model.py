"""Sketch channel — boxed class notation inside fenced sketch blocks."""

from __future__ import annotations

import re
import textwrap
from typing import List, Optional

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
            operation = self._operation_from(tokens)
            for callee in nested.arrows:
                if callee not in operation.callees:
                    operation.callees.append(callee)
            for note in nested.notes:
                operation.add_invariant(note)
            self.operations.append(operation)
            return nested.end
        prop = self.property_type(name=tokens[0])
        for note in nested.notes:
            prop.take_note(note)
        self.properties.append(prop)
        return nested.end

    def read_uml_member(self, lines: list[str], index: int, owner: Operation | Property) -> int:
        """The `+ name(args): type` member owner, then the arrows and notes under it; the index after them."""
        if isinstance(owner, Operation):
            self.operations.append(owner)
        else:
            self.properties.append(owner)
        index += 1
        while index < len(lines):
            stripped = lines[index].strip()
            if not stripped:
                index += 1
                continue
            if _is_rule(stripped) or _BOLD_CLASS.match(stripped) or _uml_member(stripped) is not None:
                break
            if stripped.startswith("->"):
                callee = stripped[2:].strip()
                if callee and isinstance(owner, Operation) and callee not in owner.callees:
                    owner.callees.append(callee)
                index += 1
                continue
            if stripped.startswith("//"):
                owner.add_invariant(stripped[2:].strip())
                index += 1
                continue
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", stripped):
                owner.add_invariant(stripped)
                index += 1
                continue
            break
        return index

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

    def load_module(self, source: Module) -> "SketchModule":
        return SketchModule(name=source.name, sequential_order=source.sequential_order)

    def load_class(self, source: OoadClass) -> SketchOoadClass:
        return SketchOoadClass(name=source.name, sequential_order=source.sequential_order)

    def sketch_lines(self, depth: int) -> List[str]:
        lines = [f"{'#' * min(depth, _DEEPEST_HEADING)} {self.name}/", ""]
        for oclass in self.classes:
            lines.extend(oclass.sketch_lines(min(max(_CLASS_DEPTH, depth + 1), _DEEPEST_HEADING)))
        for nested in self.modules:
            lines.extend(nested.sketch_lines(depth + 1))
        return lines

    def read_classes(self, lines: List[str]) -> None:
        """The class cards written under this module's heading; a second card of a class it holds adds to it."""
        for oclass in self._classes_in(textwrap.dedent("\n".join(lines))):
            existing = next((known for known in self.classes if known.name == oclass.name), None)
            if existing is None:
                self.classes.append(oclass)
                continue
            existing.merge(oclass)

    def _classes_in(self, text: str) -> list[SketchOoadClass]:
        if any(_BOLD_CLASS.match(raw.strip()) for raw in text.splitlines()):
            return self._uml_classes(text)
        lines = [raw.strip() for raw in text.splitlines() if raw.strip() and raw.strip() != "Fidelity:"]
        classes: list[SketchOoadClass] = []
        current: SketchOoadClass | None = None
        index = 0
        while index < len(lines):
            stripped = lines[index]
            if stripped in {"----", "```"} or stripped.startswith("```"):
                current = None
                index += 1
                continue
            if stripped.startswith("//") or stripped.startswith("#"):
                index += 1
                continue
            if current is not None and _is_prose(stripped):
                current = None
                index += 1
                continue
            headed = _CLASS.match(stripped)
            if headed and (current is None or headed.group(1) != current.name):
                current = SketchOoadClass(name=headed.group(1), sequential_order=len(classes) + 1)
                current.stereotypes = marks_in(headed.group(2) or "")
                current.bases = [base.strip() for base in split_top_level(headed.group(3) or "") if base.strip()]
                classes.append(current)
                index += 1
                continue
            if current is None:
                index += 1
                continue
            index = current.read_member(lines, index)
        return classes

    def _uml_classes(self, text: str) -> list[SketchOoadClass]:
        """`### **Session**` plus `+ name(args): type` lines. Indented bold labels stay notes."""
        classes: list[SketchOoadClass] = []
        current: SketchOoadClass | None = None
        lines = text.splitlines()
        index = 0
        while index < len(lines):
            raw = lines[index]
            stripped = raw.strip()
            if not stripped or stripped.startswith(("//", "#")) or _is_rule(stripped):
                index += 1
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            heading = _BOLD_CLASS.match(stripped)
            if heading and indent == 0:
                current = SketchOoadClass(name=heading.group(1), sequential_order=len(classes) + 1)
                classes.append(current)
                index += 1
                continue
            if current is None or indent == 0:
                index += 1
                continue
            member = _uml_member(stripped)
            if member is not None:
                index = current.read_uml_member(lines, index, member)
                continue
            if current.operations and re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", stripped):
                current.operations[-1].add_invariant(stripped)
            index += 1
        return classes


class SketchCleanEngineeringModel(CleanEngineeringModel):
    # The Clean Engineering section of a sketch, opened by either of its headings; the practice holds this lens.
    lens = SketchLens(("ce:", _SECTION_TITLE))

    def load_module(self, source: Module) -> SketchModule:
        return SketchModule(name=source.name, sequential_order=source.sequential_order)

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
        return _with_section_replaced(previous, section)

    def section_lines(self) -> List[str]:
        lines = [f"## {_SECTION_TITLE}", "", f"**Module:** `{self.name}`", ""]
        for module in self.modules:
            lines.extend(module.sketch_lines(_TOP_MODULE_DEPTH))
        return lines

    def _modules_in(self, body: str) -> List[Module]:
        """Each `name/` line opens a module, nested under the one above it when written further in. Classes written
        before any module line belong to a module named after the sketch."""
        loose = SketchModule(name=self.name, sequential_order=1)
        top: List[Module] = []
        open_modules: List[tuple] = []
        owner = loose
        section: List[str] = []
        for raw in body.splitlines():
            heading = _MODULE_HEADING.match(raw.strip())
            if heading is None:
                section.append(raw)
                continue
            owner.read_classes(section)
            section = []
            indent = len(raw) - len(raw.lstrip(" "))
            while open_modules and open_modules[-1][0] >= indent:
                open_modules.pop()
            siblings = open_modules[-1][1].modules if open_modules else top
            owner = SketchModule(name=heading.group(1), sequential_order=len(siblings) + 1)
            siblings.append(owner)
            open_modules.append((indent, owner))
        owner.read_classes(section)
        return ([loose] if loose.classes else []) + top


def _with_section_replaced(previous: str, section: List[str]) -> str:
    """previous with its clean engineering section swapped for section, or with section added at the end."""
    lines = previous.splitlines()
    span = _section_span(lines)
    if span is None:
        return previous.rstrip("\n") + "\n\n" + "\n".join(section) + "\n"
    first, last = span
    return "\n".join(lines[:first] + section + lines[last:]).rstrip("\n") + "\n"


def _section_span(lines: List[str]) -> Optional[tuple]:
    """Where the clean engineering section starts in a sketch and the line where the next peer heading ends it."""
    lens = SketchCleanEngineeringModel.lens
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
        if first is None and lens.opens(heading.group(2)):
            first, depth = index, len(heading.group(1))
        elif first is not None and len(heading.group(1)) <= depth:
            return first, index
    return (first, len(lines)) if first is not None else None


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


def _is_prose(stripped: str) -> bool:
    if stripped.startswith("->") or "-->" in stripped:
        return False
    if _CLASS.match(stripped):
        return False
    tokens = stripped.split()
    if tokens and all(_IDENT.match(token) for token in tokens):
        return False
    return bool(_PROSE.search(stripped)) and len(tokens) >= 5
