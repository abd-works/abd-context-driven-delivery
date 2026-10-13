from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

from practices.clean_engineering.rules._span import unnamed_numbers_in_span


class ProvideMeaningfulContext(PracticeGraphRule):
    slug = "provide-meaningful-context"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        for raw in unnamed_numbers_in_span(context.span(node)):
            return [f"Operation '{node.name}' uses the unnamed number {raw}."]
        return []
