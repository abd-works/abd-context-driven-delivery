"""OoadClass rules — read parsed class shape."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

_PUBLIC_OP_LIMIT = 7


class KeepClassesSingleResponsibility(PracticeGraphRule):
    slug = "keep-classes-single-responsibility"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        public_ops = [
            op
            for op in oclass.operations
            if not str(op.name).startswith("_") and op.name not in {"constructor", "__init__"}
        ]
        if len(public_ops) <= _PUBLIC_OP_LIMIT:
            return []
        return [
            f"Class '{node.name}' exposes {len(public_ops)} public operations "
            f"(budget ~{_PUBLIC_OP_LIMIT}). Split responsibilities."
        ]
