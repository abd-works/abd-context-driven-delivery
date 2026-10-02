"""Sketch channel — boxed class notation inside fenced sketch blocks."""

from __future__ import annotations

import re

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from practices.clean_engineering.model.operation import Operation, Parameter
from practices.clean_engineering.model.property import Property

_FENCE = re.compile(r"```(?:\w*)\n(.*?)```", re.DOTALL)
_CLASS = re.compile(r"^([A-Z][A-Za-z0-9]+)(?:\s*:\s*(.+))?$")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


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
    lines = [
        raw.strip()
        for raw in text.splitlines()
        if raw.strip() and not raw.strip().startswith(("//", "#", "Fidelity:"))
    ]
    classes: list[OoadClass] = []
    current: OoadClass | None = None
    pending_op: Operation | None = None
    index = 0
    while index < len(lines):
        stripped = lines[index]
        following = lines[index + 1] if index + 1 < len(lines) else ""
        if stripped in {"----", "```"} or stripped.startswith("```"):
            current = None
            pending_op = None
            index += 1
            continue
        if current is not None and _is_prose(stripped):
            current = None
            pending_op = None
            index += 1
            continue
        if stripped.startswith("->"):
            if pending_op is not None:
                callee = stripped[2:].strip()
                if callee and callee not in pending_op.callees:
                    pending_op.callees.append(callee)
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
            pending_op = None
            index += 1
            continue
        if current is None:
            index += 1
            continue
        pending_op = _add_member(current, stripped, following.startswith("->"))
        index += 1
    return classes


def _add_member(oclass: OoadClass, stripped: str, has_callees: bool) -> Operation | None:
    tokens = stripped.replace("()", " ").replace("-->", " ").split()
    if not tokens:
        return None
    name = tokens[0]
    if has_callees or name == oclass.name or len(tokens) > 1 or not _IDENT.match(name):
        operation = Operation(name=name)
        for index, token in enumerate(tokens[1:], start=1):
            if _IDENT.match(token):
                operation.parameters.append(Parameter(name=token, sequential_order=index))
        oclass.operations.append(operation)
        return operation
    oclass.properties.append(Property(name=name))
    return None


_PROSE = re.compile(r"\b(the|and|is|are|a|an|of|to|for|that|this|with|from|into|each|same|only|like)\b", re.I)


def _is_prose(stripped: str) -> bool:
    if stripped.startswith("->") or "-->" in stripped:
        return False
    if _CLASS.match(stripped):
        return False
    tokens = stripped.split()
    if tokens and all(_IDENT.match(token) for token in tokens):
        return False
    return bool(_PROSE.search(stripped)) and len(tokens) >= 5
