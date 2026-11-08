"""Clean Engineering: an object keeps the class it was built as."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class NoPrototypeSwapping(ProductionCodeRule):
    """Checked on the whole class: private helpers that do the swap are not graph operations."""

    slug = "no-prototype-swapping"
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        swap = node.get_fact("prototype_swap") or {}
        if not swap:
            return []
        return [
            f"{node.name} line {swap['line']} swaps an object's class with `{swap['code']}`; "
            f"build the right class instead (a factory or an overridable `blank()`)."
        ]
