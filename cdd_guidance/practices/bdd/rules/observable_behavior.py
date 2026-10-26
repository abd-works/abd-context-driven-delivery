"""observable-behavior — specs prove what a stakeholder can see, never private members."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class ObservableBehavior(PracticeGraphRule):
    slug = "observable-behavior"
    node_types = ("Spec", "Description", "Context", "Observation")

    def check(self, node, context) -> list[str]:
        probe = node.get_fact("private_probe") or {}
        if not probe:
            return []
        return [f"Line {probe['line']}: {probe['kind']}."]
