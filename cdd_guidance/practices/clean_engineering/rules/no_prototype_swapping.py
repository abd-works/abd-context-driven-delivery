"""Clean Engineering: an object keeps the class it was built as."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_PROTOTYPE_SWAP = re.compile(r"\bObject\.setPrototypeOf\s*\(|\.__proto__\s*=(?!=)|\.__class__\s*=(?!=)")


class NoPrototypeSwapping(PracticeGraphRule):
    """Checked on the whole class: private helpers that do the swap are not always parsed as operations."""

    slug = "no-prototype-swapping"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        span = context.span(node)
        found = _PROTOTYPE_SWAP.search(span)
        if found is None:
            return []
        line = node.source.start_line + span.count("\n", 0, found.start())
        return [
            f"{node.name} line {line} swaps an object's class with `{found.group(0).strip()}`; "
            f"build the right class instead (a factory or an overridable `blank()`)."
        ]
