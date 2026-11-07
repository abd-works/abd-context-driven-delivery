"""Sketch channel — boxed class notation inside fenced sketch blocks."""

from __future__ import annotations

import re
import textwrap
from typing import List, Optional

from cdd_guidance.actions.sketch.sketch_outline import SketchLens, SketchOutline
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
# The Clean Engineering section of a sketch, opened by either of its headings; the practice declares these titles.
_LENS = SketchLens(("ce:", _SECTION_TITLE))
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
_UML_OP = re.compile(r"^[+\-]\s*([A-Za-z_][A-Za-z0-9_]*)\((.*)\)\s*(?::\s*(.+))?$")
_UML_PROP = re.compile(r"^[+\-]\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.+)$")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RETURN_TYPE = re.compile(
    r"^(void|string|number|bool|boolean|int|float|object|any|list|dict|str|None|Path)$"
    r"|^[A-Z][A-Za-z0-9]*$"
)
_PROSE = re.compile(
    r"\b(the|and|is|are|a|an|of|to|for|that|this|with|from|into|each|same|only|like)\b",
    re.I,
)


class SketchOoadClass(OoadClass):
    """A class in the sketch notation: its heading, then a fence of its members."""

    def sketch_lines(self, depth: int) -> List[str]:
        marks = "".join(f" <<{item}>>" for item in self.stereotypes)
        bases = f" : {', '.join(self.bases)}" if self.bases else ""
        lines = [f"{'#' * depth} {self.name}{marks}{bases}", ""]
        members: List[str] = []
        for prop in self.properties:
            members.append(prop.name)
            members.extend(f"{_MEMBER_INDENT}// {note}" for note in _property_notes(prop))
        for operation in self.operations:
            members.append(_operation_line(operation))
            members.extend(f"{_MEMBER_INDENT}-> {callee}" for callee in operation.callees)
            members.extend(f"{_MEMBER_INDENT}// {note}" for note in operation.invariant_lines())
        if members:
            lines.extend([_FENCE, *members, _FENCE, ""])
        return lines


class SketchModule(Module):
    """A module in the sketch notation: a `name/` heading, its own classes, then its nested modules, so each class
    is read back under its module."""

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


class SketchCleanEngineeringModel(CleanEngineeringModel):
    lens = _LENS

    def load_module(self, source: Module) -> SketchModule:
        return SketchModule(name=source.name, sequential_order=source.sequential_order)

    def parse(self, text: str) -> "SketchCleanEngineeringModel":
        """Read the sketch's clean engineering section into this model's own modules, and return it."""
        declared = _MODULE.search(text)
        self.name = declared.group(1) if declared else "KnowledgeGraph"
        body = SketchOutline(text, _NESTING_INDENT).body_for(self.lens)
        self.modules = _modules_in(body, self.name)
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


def _property_notes(prop: Property) -> List[str]:
    stereotype = [f"<<{prop.stereotype}>>"] if prop.stereotype in _RELATIONSHIP_KINDS else []
    return stereotype + prop.notes()


def _operation_line(operation: Operation) -> str:
    """`returnType name param param`; a bare name gets `()` so it is not read back as a property."""
    words = [operation.return_type] if operation.return_type and _is_return_type(operation.return_type) else []
    words.append(operation.name)
    words.extend(parameter.name for parameter in operation.parameters)
    if len(words) == 1 and not operation.callees:
        return f"{operation.name}()"
    return " ".join(words)


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
    lens = _LENS
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


def _modules_in(body: str, loose_name: str) -> List[Module]:
    """Each `name/` line opens a module, nested under the one above it when written further in.
    Classes written before any module line belong to a module named after the sketch."""
    loose = SketchModule(name=loose_name, sequential_order=1)
    top: List[Module] = []
    open_modules: List[tuple] = []
    owner = loose
    section: List[str] = []
    for raw in body.splitlines():
        heading = _MODULE_HEADING.match(raw.strip())
        if heading is None:
            section.append(raw)
            continue
        _add_classes(owner, section)
        section = []
        indent = len(raw) - len(raw.lstrip(" "))
        while open_modules and open_modules[-1][0] >= indent:
            open_modules.pop()
        siblings = open_modules[-1][1].modules if open_modules else top
        owner = SketchModule(name=heading.group(1), sequential_order=len(siblings) + 1)
        siblings.append(owner)
        open_modules.append((indent, owner))
    _add_classes(owner, section)
    return ([loose] if loose.classes else []) + top


def _add_classes(module: Module, lines: List[str]) -> None:
    for oclass in _classes_in(textwrap.dedent("\n".join(lines))):
        existing = next((known for known in module.classes if known.name == oclass.name), None)
        if existing is None:
            module.classes.append(oclass)
            continue
        _merge_class(existing, oclass)


def _merge_class(into: OoadClass, incoming: OoadClass) -> None:
    seen_props = {member.name for member in into.properties}
    for prop in incoming.properties:
        if prop.name not in seen_props:
            into.properties.append(prop)
            seen_props.add(prop.name)
    seen_ops = {member.name for member in into.operations}
    for operation in incoming.operations:
        if operation.name not in seen_ops:
            into.operations.append(operation)
            seen_ops.add(operation.name)
    for base in incoming.bases:
        if base not in into.bases:
            into.bases.append(base)
    for stereotype in incoming.stereotypes:
        if stereotype not in into.stereotypes:
            into.stereotypes.append(stereotype)
    if incoming.intent and not into.intent:
        into.intent = incoming.intent


def _classes_in(text: str) -> list[OoadClass]:
    if any(_BOLD_CLASS.match(raw.strip()) for raw in text.splitlines()):
        return _uml_classes(text)
    lines = [raw.strip() for raw in text.splitlines() if raw.strip() and raw.strip() != "Fidelity:"]
    classes: list[OoadClass] = []
    current: OoadClass | None = None
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
        index = _add_member(current, lines, index)
    return classes


def _is_rule(stripped: str) -> bool:
    return len(stripped) >= 4 and set(stripped) <= {"-"}


def _uml_classes(text: str) -> list[OoadClass]:
    """`### **Session**` plus `+ name(args): type` lines. Indented bold labels stay notes."""
    classes: list[OoadClass] = []
    current: OoadClass | None = None
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped or stripped.startswith(("//", "#")):
            index += 1
            continue
        if _is_rule(stripped):
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
        operation = _UML_OP.match(stripped)
        prop = None if operation else _UML_PROP.match(stripped)
        if operation or prop:
            index = _add_uml_member(current, lines, index, operation, prop)
            continue
        if current.operations and re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", stripped):
            current.operations[-1].add_invariant(stripped)
        index += 1
    return classes


def _add_uml_member(oclass, lines, index, operation_match, prop_match) -> int:
    if operation_match:
        operation = Operation(name=operation_match.group(1), return_type=operation_match.group(3) or "")
        for order, part in enumerate(split_top_level(operation_match.group(2) or ""), start=1):
            name, _, hint = part.partition(":")
            hint = hint.split("=")[0].strip()
            operation.parameters.append(Parameter(name=name.strip(), sequential_order=order, type_hint=hint))
        oclass.operations.append(operation)
        owner = operation
    else:
        owner = Property(name=prop_match.group(1), type_hint=prop_match.group(2).strip())
        oclass.properties.append(owner)
    index += 1
    while index < len(lines):
        stripped = lines[index].strip()
        if not stripped:
            index += 1
            continue
        if _is_rule(stripped) or _BOLD_CLASS.match(stripped) or _UML_OP.match(stripped) or _UML_PROP.match(stripped):
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


def _add_member(oclass: OoadClass, lines: list[str], index: int) -> int:
    stripped = lines[index]
    nested = _take_nest(lines, index + 1)
    tokens = stripped.replace("()", " ").replace("-->", " ").split()
    if not tokens:
        return nested.end
    if stripped.endswith("()") or _is_operation_line(oclass, tokens, nested.arrows):
        operation = _operation_from(oclass, tokens)
        for callee in nested.arrows:
            if callee not in operation.callees:
                operation.callees.append(callee)
        for note in nested.notes:
            operation.add_invariant(note)
        oclass.operations.append(operation)
        return nested.end
    prop = Property(name=tokens[0])
    for note in nested.notes:
        prop.take_note(note)
    oclass.properties.append(prop)
    return nested.end


class _Nest:
    def __init__(self, end: int, arrows: list[str], notes: list[str]) -> None:
        self.end = end
        self.arrows = arrows
        self.notes = notes


def _take_nest(lines: list[str], start: int) -> _Nest:
    arrows: list[str] = []
    notes: list[str] = []
    index = start
    while index < len(lines):
        stripped = lines[index]
        if stripped in {"----", "```"} or stripped.startswith("```"):
            break
        if stripped.startswith("->"):
            callee = stripped[2:].strip()
            if callee:
                arrows.append(callee)
            index += 1
            continue
        if stripped.startswith("//"):
            notes.append(stripped[2:].strip())
            index += 1
            continue
        if stripped.startswith("#") or _is_prose(stripped) or _CLASS.match(stripped):
            break
        break
    return _Nest(index, arrows, notes)


def _is_operation_line(oclass: OoadClass, tokens: list[str], arrows: list[str]) -> bool:
    if arrows:
        return True
    if tokens[0] == oclass.name:
        return True
    return len(tokens) > 1


def _operation_from(oclass: OoadClass, tokens: list[str]) -> Operation:
    if tokens[0] == oclass.name:
        name = tokens[0]
        rest = tokens[1:]
        return_type = ""
    elif len(tokens) >= 2 and _is_return_type(tokens[0]):
        return_type = tokens[0]
        name = tokens[1]
        rest = tokens[2:]
    else:
        return_type = ""
        name = tokens[0]
        rest = tokens[1:]
    operation = Operation(name=name, return_type=return_type)
    for order, token in enumerate(rest, start=1):
        if _IDENT.match(token):
            operation.parameters.append(Parameter(name=token, sequential_order=order))
    return operation


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
