"""prefer-class-operations — module-level private helpers that only one class calls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class PreferClassOperations(ProductionCodeRule):
    slug = "prefer-class-operations"
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        return [
            f"Module function '{function}' (line {line}) is only used from '{node.name}'. "
            f"Move it onto '{node.name}' as a method."
            for function, line in node.get_fact("module_helpers", [])
        ]
