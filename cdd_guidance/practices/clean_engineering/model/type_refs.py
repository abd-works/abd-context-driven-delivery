"""Type-name helpers shared by CE tree sync and the practice graph."""

from __future__ import annotations

import re
from typing import List




def name_with_type(name: str, type_hint: str) -> str:
    """A member as a model line writes it: `total: int`, or its name alone when it has no type."""
    return f"{name}: {type_hint}" if type_hint else name


_PRIMITIVE_TYPE_NAMES = frozenset(
    {
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
    }
)


def is_primitive_type(type_name: str) -> bool:
    if not type_name:
        return True
    if type_name.lower().strip() in _PRIMITIVE_TYPE_NAMES:
        return True
    return type_name[0].islower()


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
