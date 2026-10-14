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
        phases = {_phase(step, context) for step in steps}
        missing = []
        if "given" not in phases:
            missing.append("Given")
        if "when" not in phases:
            missing.append("When")
        if "then" not in phases:
            missing.append("Then")
        if missing:
            return [f"Scenario {node.name!r} is missing required phase(s): {', '.join(missing)}."]
        return []


def _phase(step, context) -> str:
    data = context.node_data(step)
    phase = str(data.get("phase") or "").casefold()
    if phase in {"given", "when", "then"}:
        return phase
    if step.type == "Given":
        return "given"
    if step.type == "When":
        return "when"
    if step.type == "Then":
        return "then"
    keyword = context.step_keyword(step).casefold()
    if keyword in {"given", "when", "then"}:
        return keyword
    label = (step.name or "").casefold()
    for prefix in ("given", "when", "then"):
        if label.startswith(prefix + " "):
            return prefix
    return ""
