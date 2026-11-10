"""prefer-class-operations — module-level private helpers that only one class calls."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class PreferClassOperations(PracticeGraphRule):
    slug = "prefer-class-operations"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        return [
            f"Module function '{function}' (line {line}) is only used from '{node.name}'. "
            f"Move it onto '{node.name}' as a method."
            for function, line in node.get_fact("module_helpers", [])
        ]
