"""OoadClass rules — read parsed class shape."""

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


def _public_operations_for_budget(operations) -> list:
    """Count public behavior — not getters/setters (primitive accessors)."""
    singles: list = []
    accessor_groups: dict[str, list] = {}
    for op in operations:
        name = str(op.name)
        if name.startswith("_") or name in {"constructor", "__init__", "get", "set"}:
            continue
        if getattr(op, "is_property", False):
            continue
        if name.startswith("get") and len(name) > 3 and name[3].isupper():
            key = _accessor_property_key(name)
            if key:
                accessor_groups.setdefault(key, []).append(op)
            continue
        if name.startswith("set") and len(name) > 3 and name[3].isupper():
            key = _accessor_property_key(name)
            if key:
                accessor_groups.setdefault(key, []).append(op)
            continue
        if name.startswith("is") and len(name) > 2 and name[2].isupper():
            continue
        if name.startswith("is") and len(name) > 2 and name[2].islower():
            continue
        singles.append(op)
    meaningful = list(singles)
    meaningful.extend(group[0] for group in accessor_groups.values())
    return meaningful


class KeepClassesSingleResponsibility(PracticeGraphRule):
    slug = "keep-classes-single-responsibility"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        public_ops = _public_operations_for_budget(oclass.operations)
        budget = _public_op_budget(node.name)
        if len(public_ops) <= budget:
            return []
        return [
            f"Class '{node.name}' exposes {len(public_ops)} public operations "
            f"(budget ~{budget}). Split responsibilities."
        ]
