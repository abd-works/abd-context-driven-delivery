"""Graph + model — applies to every code channel."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

MAX_DOMAIN_PARAMETERS = 3
_PARAMETER_NAMES_EXCLUDED_FROM_COUNT = frozenset({"self", "cls"})
# Creation factories may take the full field set required to construct the aggregate.
_PARAMETER_COUNT_EXEMPT_OPERATION_NAMES = frozenset({"create"})


def counted_parameters(names: list[str]) -> int:
    return sum(1 for name in names if name not in _PARAMETER_NAMES_EXCLUDED_FROM_COUNT)


class LimitOperationParameters(PracticeGraphRule):
    slug = "limit-operation-parameters"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if node.name in _PARAMETER_COUNT_EXEMPT_OPERATION_NAMES:
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
