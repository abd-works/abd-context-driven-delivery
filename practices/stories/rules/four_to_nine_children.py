"""four-to-nine-children — ported from practices/stories/scanners (model/graph shape)."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_SCENARIO_CALLS = re.compile(r"\bscenario\s*\(")


def _band(count: int) -> str | None:
    if count == 0:
        return None
    if 4 <= count <= 9:
        return None
    if count in (3, 10):
        return "warning"
    return "error"


class FourToNineChildren(PracticeGraphRule):
    slug = "four-to-nine-children"
    node_types = ("Epic", "SubEpic", "Story", "Scenario")

    def check(self, node, context) -> list[str]:
        count, label = _child_tally(node, context)
        severity = _band(count)
        if severity is None:
            return []
        kind = node.type.lower().replace("subepic", "sub-epic")
        return [f"{kind} {node.name!r}: {count} {label} (target 4-9)"]


def _child_tally(node, context) -> tuple[int, str]:
    if node.type in {"Epic", "SubEpic"}:
        sub = context.child_count(node, ("decomposedInto",))
        return sub, "children"
    if node.type == "Story":
        scenarios = context.child_count(node, ("scenarios",))
        backgrounds = context.child_count(node, ("background",))
        total = scenarios + backgrounds
        if total == 0:
            text = context.text(node)
            total = len(_SCENARIO_CALLS.findall(text))
        label = "scenarios" if backgrounds == 0 else "children"
        return total, label
    if node.type == "Scenario":
        steps = context.child_count(node, ("steps",))
        return steps, "steps"
    return 0, "children"
