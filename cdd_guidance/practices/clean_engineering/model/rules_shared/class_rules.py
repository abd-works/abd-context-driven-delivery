"""OoadClass rules — read the class shape its parser recorded on the graph node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

_CLASS_BUDGET = 9


def _is_accessor(name: str) -> bool:
    """getX / setX / isX — property access, not behavior."""
    for prefix in ("get", "set", "is"):
        if name.startswith(prefix) and len(name) > len(prefix) and name[len(prefix)].isupper():
            return True
    return False


def _public_operations_for_budget(shapes: list[dict]) -> list[str]:
    """Public behavior only: property getters and setters do not count."""
    return [
        str(shape["name"])
        for shape in shapes
        if not str(shape["name"]).startswith("_")
        and shape["name"] not in {"constructor", "__init__", "get", "set"}
        and not shape.get("is_property")
        and not _is_accessor(str(shape["name"]))
    ]


class KeepClassesSingleResponsibility(PracticeGraphRule):
    slug = "keep-classes-single-responsibility"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        if not node.has_fact("operation_shapes"):
            return []
        public_ops = _public_operations_for_budget(node.get_fact("operation_shapes"))
        if len(public_ops) <= _CLASS_BUDGET:
            return []
        return [
            f"Class '{node.name}' exposes {len(public_ops)} public operations "
            f"(budget ~{_CLASS_BUDGET}). Split responsibilities."
        ]
