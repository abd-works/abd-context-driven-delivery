"""prefer-class-operations — module-level private helpers that only one class calls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule
from harness.graph.violation import Finding

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class PreferClassOperations(ProductionCodeRule):
    slug = "prefer-class-operations"
    # Requires a judge: whether a free function belongs on a class is read from who calls it and why; the check counts its callers.
    requires_judge = True
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        """Each module helper only this class uses, found on the helper's own line, where it is to be moved from."""
        return [
            Finding(node, f"Module function '{function}' (line {line}) is only used from '{node.name}'. Move it onto '{node.name}' as a method.", (line, line))
            for function, line in node.get_fact("module_helpers", [])
        ]
