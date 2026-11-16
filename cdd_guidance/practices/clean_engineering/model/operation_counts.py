"""How many operations a class declares, and how many of them its visibility makes public."""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES

if TYPE_CHECKING:
    from harness.graph.graph import Node

# A script's private member: TypeScript's and JavaScript's `#name`.
_SCRIPT_PRIVATE_MARK = "#"


class OperationCount(NamedTuple):
    """<<Value Object>> A class's operations: every one it declares, its getters, setters, and constructor included,
    and those its visibility makes public. A constructor builds the object; it is counted but never public. In Python
    an operation is public when its name does not start with ``_``, so a dunder such as ``__init__`` is not; in a
    language with a visibility keyword, such as TypeScript, JavaScript, or Java, when it is not marked ``private`` and
    its name does not start with ``#``."""

    total: int
    public: int


def operation_count(node: "Node") -> OperationCount:
    """The operations of the class node, from the shapes of its operations it saves (``operation_shapes``)."""
    shapes = node.get_fact("operation_shapes", []) or []
    python = (node.source.file or "").endswith(".py")
    public = [shape for shape in shapes if shape["name"] not in CONSTRUCTOR_NAMES and _is_public(shape, python)]
    return OperationCount(len(shapes), len(public))


def _is_public(shape: dict, python: bool) -> bool:
    name = shape["name"]
    if python:
        return not name.startswith("_")
    return not shape.get("is_private") and not name.startswith(_SCRIPT_PRIVATE_MARK)
