"""The classes of Clean Engineering's graph, indexed for the facts that compare a class with the rest of the graph.

A second object model, a service-plus-bag pair, or a pass-through layer looks fine inside the file that holds it; the
facts that catch them have to see every class at once. ``ProductionClasses`` reads the graph once after each read, from the
nodes' saved facts and the graph's edges, and answers by class name, so each fact compares classes instead of rescanning
every edge for every class.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Callable, Iterator

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.reading.code_read import DESCRIBED_FACT
from cdd_guidance.practices.source_code import ProjectTestCode

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading

_IDENTIFIER = re.compile(r"[A-Za-z_]\w*")
# A constructor handing its base a message: Python's `super().__init__("...")`, a brace language's `super("...")`.
_HANDS_MESSAGE = re.compile(r"\bsuper\(\)\.__init__\(\s*[^)\s]|\bsuper\(\s*[^)\s]")
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
        "WeakMap",
        "WeakSet",
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


class ProductionClass:
    """One class of production code as the graph holds it, which answers for itself: the fields it holds, the bases it
    derives from, its public operations, whether it does any work, whether another class mixes it in, and whether it is
    a value or a failure. It is a view of its node, read from the facts the node saves and the graph's edges, so a class
    read back from a saved graph answers what the class it was read from does; the facts a recorder writes go on its
    node."""

    def __init__(self, node: "Node", classes: "ProductionClasses") -> None:
        self.node = node
        self._classes = classes

    @property
    def name(self) -> str:
        return self.node.name

    @property
    def node_id(self) -> str:
        return self.node.node_id

    @property
    def fields(self) -> dict[str, str]:
        """Field name to type hint: declared properties, then the fields its constructor assigns, as the class saves
        them (``held_fields``)."""
        return dict(self.node.get_fact("held_fields") or {})

    @property
    def bases(self) -> list[str]:
        """The names of the classes it derives from, each by its own name: ``Epic`` for ``pkg.Epic``, ``list`` for
        ``list[Entry]``."""
        return [str(base).rsplit(".", 1)[-1].split("[", 1)[0] for base in self.node.get_fact("bases", []) or []]

    @property
    def operations(self) -> list["Node"]:
        """The public operations the graph records for this class."""
        return self._classes.operations_of(self.node)

    @property
    def operation_count(self) -> int:
        return len(self.operations)

    @property
    def has_behavior(self) -> bool:
        """Any operation beyond construction and property access. The operations' shapes list getters too, which the
        graph holds as property nodes, so they are read from the class's own fact."""
        return any(
            not shape.get("is_property") and shape["name"] not in CONSTRUCTOR_NAMES and not shape["name"].startswith("__")
            for shape in self.node.get_fact("operation_shapes")
        )

    @property
    def is_mixin(self) -> bool:
        """A class another class mixes in before the base it derives from, such as a reading mixed into a model."""
        return self._classes.is_mixed_in(self.name)

    @property
    def is_value(self) -> bool:
        return self._classes.is_value(self.name)

    @property
    def is_failure(self) -> bool:
        return self._classes.is_failure(self.name)

    @property
    def file(self) -> str:
        return self.node.source.file or ""


class ProductionClasses:
    """Every production class in the practice read from code, each a *ProductionClass*, read once after each read; a
    class a model document describes has no code to measure, so it is none of them. It answers by class
    name, so each fact compares classes instead of rescanning every edge for every class, and says what kind of class a
    type name stands for: a value, a failure, or a failure that writes its own message."""

    def __init__(self, reading: "GraphReading") -> None:
        in_graph = reading.in_graph
        # The index of the classes Clean Engineering read by name, which its type linking asks too.
        self._index = reading.code_index
        self._operations: dict[str, list["Node"]] = {}
        for edge in in_graph.edge_index.of("owns"):
            if edge.child.type == "Operation" and edge.parent.type == "OoadClass":
                self._operations.setdefault(edge.parent.node_id, []).append(edge.child)
        self._classes = {node.node_id: ProductionClass(node, self) for node in in_graph.nodes("OoadClass") if _is_production(node, reading.test_code)}
        # A class mixed in comes before the base a class derives from: `class Model(Reading, BaseModel)`.
        self._mixins = {base for each in self for base in each.bases[:-1]}
        self._defining: dict[str, set[str]] = {}
        for node in in_graph.nodes("OoadClass"):
            for operation in self.operations_of(node):
                self._defining.setdefault(operation.name, set()).add(node.node_id)

    def __iter__(self) -> Iterator[ProductionClass]:
        return iter(self._classes.values())

    def named(self, type_name: str) -> list[ProductionClass]:
        """The production classes the graph holds called type_name."""
        return [self._classes[node.node_id] for node in self._index.classes_named(type_name) if node.node_id in self._classes]

    def defining(self, operation_name: str) -> set[str]:
        """Node ids of the classes (module function holders included) that define a public operation of this name."""
        return self._defining.get(operation_name, set())

    def operations_of(self, node: "Node") -> list["Node"]:
        """The public operations the graph records for the class node, production code or not."""
        return self._operations.get(node.node_id, [])

    def is_mixed_in(self, name: str) -> bool:
        return name in self._mixins

    def is_value(self, type_name: str) -> bool:
        """True for a value type: a standard one such as a path, a date, or a number; a failure, named as one or
        derived from one, such as ``ToolCallStopped(Exception)``; a collection, such as ``CallGraph(list)``; or a class
        of the graph its stereotype or base marks as a value object, directly or through the classes it derives from.
        A class makes values from what it holds; only a collaborator it builds is a dependency the caller cannot see."""
        return self._derives(type_name, self._is_value_itself, frozenset())

    def is_failure(self, type_name: str) -> bool:
        """True for a failure: a class named as one, such as ``AgentToolValidationError``, or derived from one. A
        failure keeps the name of what it failed on for its message, not as a copy of that object."""
        return self._derives(type_name, self._named_failure, frozenset())

    def gives_own_message(self, failure: str) -> bool:
        """True when a failure the graph declares writes its own message: its constructor hands its base one, such
        as ``super().__init__(f"paths are required to commit")``."""
        return any(
            _HANDS_MESSAGE.search(operation.get_fact("body_text") or "")
            for declared in self.named(failure)
            for operation in declared.operations
            if operation.name in CONSTRUCTOR_NAMES
        )

    def _derives(self, type_name: str, is_kind: Callable[[str], bool], seen: frozenset[str]) -> bool:
        """True when the class named type_name is of a kind, or derives from a class that is, through any of the
        classes the graph declares under that name; the one walk up the bases every kind test shares."""
        if is_kind(type_name):
            return True
        if type_name in seen:
            return False
        return any(self._derives(base, is_kind, seen | {type_name}) for declared in self.named(type_name) for base in declared.bases)

    def _is_value_itself(self, type_name: str) -> bool:
        """A standard value, a collection base, a failure, or a class of the graph its stereotype marks as a value."""
        if type_name in _STANDARD_VALUES or type_name in _VALUE_BASES or self._named_failure(type_name):
            return True
        return any(_declares_value(declared.node) for declared in self.named(type_name))

    def _named_failure(self, type_name: str) -> bool:
        return type_name.endswith(_FAILURE_SUFFIXES)


def _is_production(node: "Node", test_code: "ProjectTestCode") -> bool:
    """A class of production code, read from code: neither one a model document describes, which has no code to
    measure, nor one read from a spec or test support, nor the holder of a file's functions."""
    return node.name != MODULE_FUNCTION_HOLDER and not test_code.is_test_code(node.source.file) and not node.has_fact(DESCRIBED_FACT)


def _declares_value(node: "Node") -> bool:
    stereotypes = {str(item).lower() for item in node.get_fact("stereotypes", []) or []}
    return "value object" in stereotypes


def parameters_of(operation: "Node") -> list["Node"]:
    """The parameters an operation takes, in the order it declares them: the nodes its hasParameter edges lead to, which
    a graph read back from its saved file keeps too."""
    return [edge.child for edge in operation.graph.edges.from_parent("hasParameter", operation)]


# The parameter a method takes for its own object, which is no parameter a caller supplies.
_PARAMETER_NAMES_EXCLUDED_FROM_COUNT = frozenset({"self", "cls"})


def counted_parameters(names: list[str], packed: dict[str, int] | None = None) -> int:
    """Each named parameter counts once, except a packed tuple or ``*args``, which counts each value it carries."""
    packed = packed or {}
    named = [name for name in names if name not in _PARAMETER_NAMES_EXCLUDED_FROM_COUNT]
    unnamed = [values for name, values in packed.items() if name not in named]
    return sum(packed.get(name, 1) for name in named) + sum(unnamed)


def names_in(type_hint: str) -> set[str]:
    """The identifiers a type hint mentions: ``dict[str, Practice]`` mentions ``dict``, ``str``, and ``Practice``."""
    return set(_IDENTIFIER.findall(type_hint or ""))
