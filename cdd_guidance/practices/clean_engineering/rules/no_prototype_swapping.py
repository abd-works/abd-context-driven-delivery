"""Clean Engineering: an object keeps the class it was built as."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class NoPrototypeSwapping(PracticeGraphRule):
    """Checked on the whole class: private helpers that do the swap are not graph operations."""

    slug = "no-prototype-swapping"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        swap = node.get_fact("prototype_swap") or {}
        if not swap:
            return []
        return [
            f"{node.name} line {swap['line']} swaps an object's class with `{swap['code']}`; "
            f"build the right class instead (a factory or an overridable `blank()`)."
        ]
