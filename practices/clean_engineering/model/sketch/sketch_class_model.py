"""Sketch channel — boxed class notation inside fenced sketch blocks."""

from __future__ import annotations

import re

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from practices.clean_engineering.model.operation import Operation, Parameter
from practices.clean_engineering.model.property import Property, append_invariant, take_property_note

_FENCE = re.compile(r"```(?:\w*)\n(.*?)```", re.DOTALL)
_CLASS = re.compile(r"^([A-Z][A-Za-z0-9]+)(?:\s*:\s*(.+))?$")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RETURN_TYPE = re.compile(
    r"^(void|string|number|bool|boolean|int|float|object|any|list|dict|str|None|Path)$"
    r"|^[A-Z][A-Za-z0-9]*$"
)
_PROSE = re.compile(
    r"\b(the|and|is|are|a|an|of|to|for|that|this|with|from|into|each|same|only|like)\b",
    re.I,
)


class SketchCleanEngineeringModel(CleanEngineeringModel):
    @classmethod
    def parse(cls, text: str) -> "SketchCleanEngineeringModel":
        model = cls(name="KnowledgeGraph", sequential_order=1)
        module = Module(name="KnowledgeGraph", sequential_order=1)
        body = _FENCE.sub(lambda match: "\n" + match.group(1) + "\n", text)
        for oclass in _classes_in(body):
            existing = next((row for row in module.classes if row.name == oclass.name), None)
            if existing is None:
                module.classes.append(oclass)
                continue
            _merge_class(existing, oclass)
        if module.classes:
            model.modules.append(module)
        return model


def _merge_class(into: OoadClass, incoming: OoadClass) -> None:
    seen_props = {row.name for row in into.properties}
    for prop in incoming.properties:
        if prop.name not in seen_props:
            into.properties.append(prop)
            seen_props.add(prop.name)
    seen_ops = {row.name for row in into.operations}
    for operation in incoming.operations:
        if operation.name not in seen_ops:
            into.operations.append(operation)
            seen_ops.add(operation.name)
    for collaborator in incoming.collaborators:
        if collaborator not in into.collaborators:
            into.collaborators.append(collaborator)
    if incoming.intent and not into.intent:
        into.intent = incoming.intent


def _classes_in(text: str) -> list[OoadClass]:
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
            current = OoadClass(name=headed.group(1), sequential_order=len(classes) + 1)
            bases = headed.group(2) or ""
            current.collaborators = [part.strip() for part in bases.split() if part.strip()]
            if current.collaborators:
                current.intent = " : ".join(current.collaborators)
            classes.append(current)
            index += 1
            continue
        if current is None:
            index += 1
            continue
        index = _add_member(current, lines, index)
    return classes


def _add_member(oclass: OoadClass, lines: list[str], index: int) -> int:
    stripped = lines[index]
    nested = _take_nest(lines, index + 1)
    tokens = stripped.replace("()", " ").replace("-->", " ").split()
    if not tokens:
        return nested.end
    if _is_operation_line(oclass, tokens, nested.arrows):
        operation = _operation_from(oclass, tokens)
        for callee in nested.arrows:
            if callee not in operation.callees:
                operation.callees.append(callee)
        for note in nested.notes:
            append_invariant(operation, note)
        oclass.operations.append(operation)
        return nested.end
    prop = Property(name=tokens[0])
    for note in nested.notes:
        take_property_note(prop, note)
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
