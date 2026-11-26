"""OoadClass rules — read the class shape its parser recorded on the graph node."""

from __future__ import annotations

from harness.graph.violation import Finding

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_CLASS_BUDGET = 9


class KeepClassesSingleResponsibility(ProductionCodeRule):
    slug = "keep-classes-single-responsibility"
    # Requires a judge: whether a class has one reason to change is read from what its members are for; the check counts them.
    requires_judge = True
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[Finding]:
        # A file's module functions are no class, so they share no responsibility to split.
        if node.name == MODULE_FUNCTION_HOLDER or not node.has_fact("operation_shapes"):
            return []
        public_ops = self._public_operations_for_budget(node.get_fact("operation_shapes"))
        if len(public_ops) <= _CLASS_BUDGET:
            return []
        return [Finding(node, f"Class '{node.name}' exposes {len(public_ops)} public operations "
            f"(budget ~{_CLASS_BUDGET}). Split responsibilities.")]

    def _is_accessor(self, name: str) -> bool:
        """getX / setX / isX — property access, not behavior."""
        for prefix in ("get", "set", "is"):
            if name.startswith(prefix) and len(name) > len(prefix) and name[len(prefix)].isupper():
                return True
        return False

    def _public_operations_for_budget(self, shapes: list[dict]) -> list[str]:
        """Public behavior only: property getters and setters do not count, nor an operation declared private, by a leading
        `_` or by the language's own keyword."""
        return [
            str(shape["name"])
            for shape in shapes
            if not str(shape["name"]).startswith("_")
            and not shape.get("is_private")
            and shape["name"] not in {"constructor", "__init__", "get", "set"}
            and not shape.get("is_property")
            and not self._is_accessor(str(shape["name"]))
        ]
