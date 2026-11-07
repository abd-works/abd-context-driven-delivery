"""Type-name helpers shared by CE tree sync and the practice graph."""

from __future__ import annotations

import re
from typing import List


def is_primitive_type(type_name: str) -> bool:
    if not type_name:
        return True
    lowered = type_name.lower().strip()
    if lowered in {
        "void",
        "none",
        "null",
        "string",
        "str",
        "number",
        "int",
        "integer",
        "float",
        "double",
        "boolean",
        "bool",
        "any",
        "unknown",
        "object",
    }:
        return True
    return type_name[0].islower()


_OPENING_BRACKETS = "<([{"
_CLOSING_BRACKETS = ">)]}"


def split_top_level(text: str) -> List[str]:
    """The comma-separated parts of a parameter list, keeping commas inside brackets or generics; blanks dropped."""
    parts: List[str] = []
    depth = 0
    start = 0
    for index, char in enumerate(text):
        if char in _OPENING_BRACKETS:
            depth += 1
        elif char in _CLOSING_BRACKETS:
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return [part.strip() for part in parts if part.strip()]


def parse_parameter(name_and_type: str) -> tuple[str, str]:
    raw = name_and_type.strip()
    if ":" in raw:
        name, type_hint = raw.split(":", 1)
        return name.strip(), type_hint.strip()
    return raw, ""


_THIRD_PARTY_TYPES = frozenset({
    "String", "Number", "Boolean", "Void", "Any", "Unknown", "Object",
    "Record", "Array", "Promise", "Partial", "Omit", "Pick", "RegExp",
    "Date", "Error", "Map", "Set", "Readonly", "Required", "NonNullable",
    "Collection", "List", "Iterable", "Sequence", "Optional",
})


def domain_type_names(type_hint: str) -> List[str]:
    """PascalCase names that are domain classes. Primitives and third-party types are not."""
    names: List[str] = []
    for token in pascal_type_names(type_hint):
        if token in _THIRD_PARTY_TYPES or token in names:
            continue
        names.append(token)
    return names


def pascal_type_names(type_hint: str) -> List[str]:
    if not type_hint:
        return []
    names: List[str] = []
    for token in re.split(r"[\[\]|&<>,\s]+", type_hint):
        token = token.strip()
        if token and token[0].isupper():
            names.append(token)
    return names
