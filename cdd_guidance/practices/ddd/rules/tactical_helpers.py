"""Shared checks for DDD tactical graph rules — names, paths, and recorded operation shapes."""

from __future__ import annotations

import re

_TECHNICAL_SUFFIXES = frozenset({"result", "response", "dto", "request"})
_AGENT_NOUNS = frozenset({"manager", "helper", "processor", "handler", "controller"})
_CAMEL = re.compile(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])")
_REPOSITORY_LIFECYCLE = re.compile(
    r"^(?:add|remove|delete|find|get|load|save|store|fetch|by_id|find_by)",
    re.IGNORECASE,
)
_UI_METHODS = frozenset({"open", "isshowing", "close", "show", "hide", "select"})
_SCREEN_NAME = re.compile(r"^(Select|Screen|Dialog|Modal|View|Page)\w*$")


def ident_tokens(name: str) -> list[str]:
    return [token.lower() for token in _CAMEL.findall(name or "") if token]


def technical_name_violation(class_name: str) -> str | None:
    tokens = ident_tokens(class_name)
    if not tokens:
        return None
    if tokens[-1] in _TECHNICAL_SUFFIXES or any(token in _AGENT_NOUNS for token in tokens):
        return f"Class '{class_name}' uses a technical name instead of a domain concept."
    return None


def public_operation_names(node) -> list[str]:
    return [
        shape["name"]
        for shape in node.get_fact("operation_shapes", [])
        if shape["name"] and not str(shape["name"]).startswith("_")
    ]


def repository_lifecycle_ops(node) -> list[str]:
    return [name for name in public_operation_names(node) if _REPOSITORY_LIFECYCLE.search(name)]


def is_presentation_module_source(node) -> bool:
    """React screen modules — not DDD building blocks in code."""
    path = (getattr(getattr(node, "source", None), "file", None) or "").replace("\\", "/").lower()
    return path.endswith(".tsx")


def is_screen_driver_class(node) -> bool:
    if not node.has_fact("operation_shapes"):
        return False
    public = {name.lower() for name in public_operation_names(node)}
    if public & _UI_METHODS and ("open" in public or "isshowing" in public):
        return True
    return bool(_SCREEN_NAME.search(node.name))
