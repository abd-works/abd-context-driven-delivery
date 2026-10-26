"""OoadClass rules — read the class shape its parser recorded on the graph node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

_PUBLIC_OP_LIMIT = 7
_REPOSITORY_CLIENT_BUDGET = 20
_AGGREGATE_BUDGET = 18


def _public_op_budget(class_name: str) -> int:
    if class_name.endswith("Repository") or class_name.endswith("Client"):
        return _REPOSITORY_CLIENT_BUDGET
    return _AGGREGATE_BUDGET


def _accessor_property_key(name: str) -> str | None:
    if name.startswith("get") and len(name) > 3 and name[3].isupper():
        return name[3:]
    if name.startswith("set") and len(name) > 3 and name[3].isupper():
        return name[3:]
    return None


def _public_operations_for_budget(shapes: list[dict]) -> list[str]:
    """Count public behavior — not getters/setters (primitive accessors)."""
    singles: list[str] = []
    accessor_groups: dict[str, list[str]] = {}
    for shape in shapes:
        name = str(shape["name"])
        if name.startswith("_") or name in {"constructor", "__init__", "get", "set"}:
            continue
        if shape.get("is_property"):
            continue
        key = _accessor_property_key(name)
        if key:
            accessor_groups.setdefault(key, []).append(name)
            continue
        if name.startswith("is") and len(name) > 2:
            continue
        singles.append(name)
    return singles + [group[0] for group in accessor_groups.values()]


class KeepClassesSingleResponsibility(PracticeGraphRule):
    slug = "keep-classes-single-responsibility"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        if not node.has_fact("operation_shapes"):
            return []
        public_ops = _public_operations_for_budget(node.get_fact("operation_shapes"))
        budget = _public_op_budget(node.name)
        if len(public_ops) <= budget:
            return []
        return [
            f"Class '{node.name}' exposes {len(public_ops)} public operations "
            f"(budget ~{budget}). Split responsibilities."
        ]
