"""Operation rules that measure every operation a file defines, not only the ones the graph records a node for.

The working copy records an Operation node for each public method. Private methods and module functions stay on their
class's parsed model (a file's module functions hang on its first class, or on a ``_module`` holder). A size, nesting,
parameter, or exception rule that read only Operation nodes would pass a 60-line private helper untouched, so these
rules also read the class node's parsed operations that have no node of their own.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from harness.graph.practice_rule import PracticeGraphRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

    from cdd_guidance.practices.clean_engineering.model.operation import Operation


class MeasuredOperation:
    """One operation a rule measures: a recorded Operation node, or a parsed operation the graph keeps no node for."""

    def __init__(self, name: str, label: str, fact: Callable[[str, object], object], source_lines: int = 0) -> None:
        self.name = name
        self.label = label
        self._fact = fact
        self._source_lines = source_lines

    @classmethod
    def from_node(cls, node: "Node") -> "MeasuredOperation":
        """Graph facts come from the node; a measurement the graph does not save comes from the parsed operation, and
        is absent from a graph read back from graph.json, which keeps no parsed objects."""

        def fact(key: str, default: object = None) -> object:
            if node.has_fact(key):
                return node.get_fact(key, default)
            if node.model is None:
                return default
            if key == "parameters":
                return _parameter_pairs(node.model)
            return getattr(node.model, key, default)

        span = node.source.end_line - node.source.start_line + 1
        return cls(node.name, f"Operation '{node.name}'", fact, span if span > 1 else 0)

    @classmethod
    def from_parsed(cls, operation: "Operation") -> "MeasuredOperation":
        def fact(key: str, default: object = None) -> object:
            if key == "parameters":
                return _parameter_pairs(operation)
            return getattr(operation, key, default)

        return cls(operation.name, f"Operation '{operation.name}' (line {operation.line})", fact)

    def fact(self, key: str, default: object = None) -> object:
        return self._fact(key, default)

    @property
    def line_count(self) -> int:
        """The parser's count; for a node without one, the lines its source span covers."""
        return self.fact("line_count") or self._source_lines


class OperationMeasureRule(PracticeGraphRule):
    """Checks each recorded Operation node, and each operation of a class that the graph records no node for."""

    node_types = ("Operation", "OoadClass")

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if node.type == "Operation":
            return self.measure(MeasuredOperation.from_node(node))
        return [
            hit
            for operation in _unrecorded_operations(node, context)
            for hit in self.measure(MeasuredOperation.from_parsed(operation))
        ]

    def measure(self, operation: MeasuredOperation) -> list[str]:
        return []


def _unrecorded_operations(node: "Node", context: "RuleCheckContext") -> list["Operation"]:
    operations = getattr(node.model, "operations", None) or []
    file = node.source.file
    return [
        operation
        for operation in operations
        if context.practice.registered(f"clean_engineering:Operation:{file}:{operation.name}:{node.name}") is None
    ]


def _parameter_pairs(operation: "Operation") -> list[list[str]]:
    """The ``[name, type hint]`` pairs the working copy saves as an Operation node's ``parameters`` fact."""
    return [[parameter.name, parameter.type_hint] for parameter in operation.parameters]
