from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

from practices.clean_engineering.rules._span import bare_catch_in_span


class UseExceptionsProperly(PracticeGraphRule):
    slug = "use-exceptions-properly"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if bare_catch_in_span(context.span(node)):
            return [f"Operation '{node.name}' has a bare catch."]
        return []
