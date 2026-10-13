from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

from practices.clean_engineering.rules._span import brace_depth


class SimplifyControlFlow(PracticeGraphRule):
    slug = "simplify-control-flow"
    node_types = ("Operation",)
    limit = 3

    def check(self, node, context) -> list[str]:
        depth = max(0, brace_depth(context.span(node)) - 1)
        if depth <= self.limit:
            return []
        return [f"Operation '{node.name}' nests control flow {depth} levels deep (max {self.limit})."]
