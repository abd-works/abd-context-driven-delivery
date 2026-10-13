"""scenarios-shape — Gherkin skeleton from graph step children (historical scanner)."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class ScenariosShape(PracticeGraphRule):
    slug = "scenarios-shape"
    node_types = ("Scenario",)

    def check(self, node, context) -> list[str]:
        steps = context.children(node, "steps")
        if not steps:
            return [f"Scenario {node.name!r} has no steps."]
        labels = [step.name.lower() for step in steps]
        has_given = any(label.startswith("given") for label in labels)
        has_when = any(label.startswith("when") for label in labels)
        has_then = any(label.startswith("then") for label in labels)
        missing = []
        if not has_given:
            missing.append("Given")
        if not has_when:
            missing.append("When")
        if not has_then:
            missing.append("Then")
        if missing:
            return [f"Scenario {node.name!r} is missing required phase(s): {', '.join(missing)}."]
        return []
