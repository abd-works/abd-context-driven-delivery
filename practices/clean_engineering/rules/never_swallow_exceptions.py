from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

from practices.clean_engineering.rules._span import swallowing_catch_in_span


class NeverSwallowExceptions(PracticeGraphRule):
    slug = "never-swallow-exceptions"
    node_types = ("Operation",)

    def check(self, node, context) -> list[str]:
        if swallowing_catch_in_span(context.span(node)):
            return [f"Operation '{node.name}' swallows a caught failure."]
        return []
