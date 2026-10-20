"""Graph + model — applies to every code channel."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

MAX_DOMAIN_PARAMETERS = 3
_PARAMETER_NAMES_EXCLUDED_FROM_COUNT = frozenset({"self", "cls"})
# Creation / mapping factories may take a record or full field set (align with prefer-instance-operations).
_PARAMETER_COUNT_EXEMPT_OPERATION_NAMES = frozenset({"create", "fromFields", "instance", "fromRequest"})
_CAMEL_FROM_FACTORY = re.compile(r"^from[A-Z]")
_LOAD_FACTORY = re.compile(r"^load(?:[A-Z].*)?$")


def _parameter_count_exempt(operation_name: str) -> bool:
    if operation_name in _PARAMETER_COUNT_EXEMPT_OPERATION_NAMES:
        return True
    if operation_name.startswith("from_"):
        return True
    if _CAMEL_FROM_FACTORY.match(operation_name):
        return True
    return _LOAD_FACTORY.match(operation_name) is not None


def counted_parameters(names: list[str]) -> int:
    return sum(1 for name in names if name not in _PARAMETER_NAMES_EXCLUDED_FROM_COUNT)


class LimitOperationParameters(PracticeGraphRule):
    slug = "limit-operation-parameters"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if _parameter_count_exempt(node.name):
            return []

        matched = context.ce_operation(node)
        if matched is not None:
            _oclass, operation = matched
            names = [param.name for param in operation.parameters]
        else:
            names = [
                edge.child.name
                for edge in node.practice.edges.get("hasParameter", [])
                if edge.parent is node
            ]
        count = counted_parameters(names)
        if count <= MAX_DOMAIN_PARAMETERS:
            return []
        return [
            f"Operation '{node.name}' takes {count} parameters "
            f"(maximum {MAX_DOMAIN_PARAMETERS}, excluding self).",
        ]
