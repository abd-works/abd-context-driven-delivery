"""The classes of one practice graph, indexed for rules that compare a class with the rest of the graph.

A second object model, a service-plus-bag pair, or a pass-through layer looks fine inside the file that holds it; the
rules that catch them have to see every class at once. ``ClassGraph`` reads the graph once per check and answers by
class name, so each rule compares classes instead of rescanning every edge for every class.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable

from cdd_guidance.practices.clean_engineering.model.operation import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_IDENTIFIER = re.compile(r"[A-Za-z_]\w*")
_HOLDER = "_module"
# Standard value types: Python's paths, dates, and numbers, and the script values a constructor fills a field with.
_STANDARD_VALUES = frozenset(
    {
        "Path",
        "PurePath",
        "PurePosixPath",
        "PureWindowsPath",
        "datetime",
        "date",
        "time",
        "timedelta",
        "Decimal",
        "Fraction",
        "UUID",
        "Date",
        "Map",
        "Set",
        "URL",
        "RegExp",
    }
)
# A failure is a value the class raises or keeps, not a collaborator it calls.
_FAILURE_SUFFIXES = ("Error", "Exception")
# Bases that make a class a value: a named tuple, an enumeration, a failure, or a collection the owner fills.
_VALUE_BASES = frozenset(
    {
        "NamedTuple",
        "Enum",
        "IntEnum",
        "StrEnum",
        "Flag",
        "Exception",
        "BaseException",
        "Error",
        "list",
        "dict",
        "set",
        "frozenset",
        "tuple",
        "Array",
    }
)


class ClassGraph:
    """Every production class in the practice, its public operations, and the fields it holds."""

    def __init__(self, context: "RuleCheckContext") -> None:
        self.classes = [
            node
            for node in context.nodes("OoadClass")
            if node.name != _HOLDER and not is_test_code(node.source.file)
        ]
        self.by_name: dict[str, list["Node"]] = {}
        for node in self.classes:
            self.by_name.setdefault(node.name, []).append(node)
        self._operations: dict[str, list["Node"]] = {}
        for edge in context.edges("owns"):
            if edge.child.type == "Operation" and edge.parent.type == "OoadClass":
                self._operations.setdefault(edge.parent.node_id, []).append(edge.child)
        self._defining: dict[str, set[str]] = {}
        for node in context.nodes("OoadClass"):
            for operation in self.operations(node):
                self._defining.setdefault(operation.name, set()).add(node.node_id)

    def operations(self, node: "Node") -> list["Node"]:
        """The public operations the graph records for this class."""
        return self._operations.get(node.node_id, [])

    def classes_defining(self, operation_name: str) -> set[str]:
        """Node ids of the classes (module function holders included) that define a public operation of this name."""
        return self._defining.get(operation_name, set())

    def fields(self, node: "Node") -> dict[str, str]:
        """Field name to type hint: declared properties, then the fields its constructor assigns, as the class saves
        them (``held_fields``), so a class read back from a saved graph answers what the class it was read from does."""
        return dict(node.get_fact("held_fields") or {})

    def is_value(self, type_name: str) -> bool:
        """True for a value type: a standard one such as a path, a date, or a number; a failure, named as one or
        derived from one, such as ``ToolCallStopped(Exception)``; a collection, such as ``CallGraph(list)``; or a class
        of the graph its stereotype or base marks as a value object, directly or through the classes it derives from.
        A class makes values from what it holds; only a collaborator it builds is a dependency the caller cannot see."""
        return self._derives(type_name, self._is_value_itself, frozenset())

    def is_failure(self, type_name: str) -> bool:
        """True for a failure: a class named as one, such as ``AgentToolValidationError``, or derived from one. A
        failure keeps the name of what it failed on for its message, not as a copy of that object."""
        return self._derives(type_name, _named_failure, frozenset())

    def _derives(self, type_name: str, is_kind: Callable[[str], bool], seen: frozenset[str]) -> bool:
        """True when the class named type_name is of a kind, or derives from a class that is, through any of the
        classes the graph declares under that name; the one walk up the bases every kind test shares."""
        if is_kind(type_name):
            return True
        if type_name in seen:
            return False
        return any(
            self._derives(base, is_kind, seen | {type_name}) for node in self.by_name.get(type_name, []) for base in self.bases_of(node)
        )

    def _is_value_itself(self, type_name: str) -> bool:
        """A standard value, a collection base, a failure, or a class of the graph its stereotype marks as a value."""
        if type_name in _STANDARD_VALUES or type_name in _VALUE_BASES or _named_failure(type_name):
            return True
        return any(_declares_value(node) for node in self.by_name.get(type_name, []))

    def bases_of(self, node: "Node") -> list[str]:
        """The names of the classes it derives from, each by its own name: ``Epic`` for ``pkg.Epic``, ``list`` for
        ``list[Entry]``."""
        return [str(base).rsplit(".", 1)[-1].split("[", 1)[0] for base in node.get_fact("bases", []) or []]

    def has_behavior(self, node: "Node") -> bool:
        """A class with any operation beyond construction and property access."""
        return any(
            not shape.get("is_property") and shape["name"] not in CONSTRUCTOR_NAMES and not shape["name"].startswith("__")
            for shape in node.get_fact("operation_shapes", []) or []
        )


def _named_failure(type_name: str) -> bool:
    return type_name.endswith(_FAILURE_SUFFIXES)


def _declares_value(node: "Node") -> bool:
    stereotypes = {str(item).lower() for item in node.get_fact("stereotypes", []) or []}
    return "value object" in stereotypes


def names_in(type_hint: str) -> set[str]:
    """The identifiers a type hint mentions: ``dict[str, Practice]`` mentions ``dict``, ``str``, and ``Practice``."""
    return set(_IDENTIFIER.findall(type_hint or ""))
