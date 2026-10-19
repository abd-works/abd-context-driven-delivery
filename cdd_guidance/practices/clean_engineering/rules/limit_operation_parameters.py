"""Graph + model — applies to every code channel."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class LimitOperationParameters(PracticeGraphRule):
    slug = "limit-operation-parameters"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        matched = context.ce_operation(node)
        if matched is not None:
            _oclass, operation = matched
            count = len(operation.parameters)
        else:
            count = sum(
                1
                for edge in node.practice.edges.get("hasParameter", [])
                if edge.parent is node
            )
        if count <= 2:
            return []
        return [f"Operation '{node.name}' takes more than two parameters."]
