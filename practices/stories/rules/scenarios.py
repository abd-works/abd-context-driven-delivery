"""scenarios fidelity — scenario, step, given, when, and then rules."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.story_model_lookup import example_count, scenario_for_graph_node

_CAMEL_STEP = re.compile(r"^[a-z]+(?:[A-Z][a-z0-9]*)+$")

_PLAIN_ENGLISH = re.compile(r"^[a-z].*(?:\s+[a-z].*)+$", re.IGNORECASE)

_DOMAIN_CLASS = re.compile(r"\bclass\s+([A-Z]\w*)\b")

_INLINE_CONDITIONAL = re.compile(
    r"\bwhen\s+[<{]?\w+[>}]?\s+is\s+(?:true|false)\b", re.I
)

_GESTURE = re.compile(
    r"\b(click(?:s|ed|ing)?|tap(?:s|ped|ping)?|press(?:es|ed|ing)?|button|link|field|widget|screen)\b",
    re.I,
)

class AndChaining(PracticeGraphRule):
    slug = "and-chaining"
    node_types = ("Scenario",)

    def check(self, node, context) -> list[str]:
        if context.children(node, "steps"):
            return _and_chaining_from_graph(node, context)
        scenario = scenario_for_graph_node(node, context)
        if scenario is None:
            return []
        for when_steps, then_steps in scenario.when_then_runs():
            if when_steps and not then_steps:
                return [
                    f"Scenario {node.name!r} has a When with no Then; add the result or chain it with And."
                ]
        return []

class ButMarksMissingState(PracticeGraphRule):
    slug = "but-marks-missing-state"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node, context) -> list[str]:
        if context.step_keyword(node).casefold() != "but":
            return []
        text = context.step_text(node).casefold()
        if any(word in text for word in ("not ", "without ", "absent", "missing", "no ")):
            return []
        return [f"But step should mark missing or absent state, not a consequence: {context.step_text(node)!r}."]

class WhenHoldsTheOperation(PracticeGraphRule):
    slug = "when-holds-the-operation"
    node_types = ("When", "Step")

    def check(self, node, context) -> list[str]:
        if context.step_keyword(node).casefold() not in {"when", ""}:
            if node.type not in {"When"}:
                return []
        text = context.step_text(node)
        if not text or " and " in text.casefold():
            return []
        if len(text.split()) < 2:
            return [f"When {text!r} should name the operation under test in plain language."]
        return []

class OutlineRequiresManyPermutations(PracticeGraphRule):
    slug = "outline-requires-many-permutations"
    node_types = ("Scenario",)

    def check(self, node, context) -> list[str]:
        outline = context.scenario_outline(node)
        scenario = scenario_for_graph_node(node, context)
        if scenario is not None:
            outline = outline or scenario.is_outline
        if not outline:
            return []
        examples = context.child_count(node, ("examples",))
        if scenario is not None:
            examples = max(examples, example_count(scenario))
        if examples <= 2:
            return [
                f"Scenario outline {node.name!r} needs more than two example rows (found {examples})."
            ]
        return []

class ExamplesTraceDomainModel(PracticeGraphRule):
    slug = "examples-trace-domain-model"
    node_types = ("Scenario",)

    def check(self, node, context) -> list[str]:
        scenario = scenario_for_graph_node(node, context)
        if scenario is None:
            return []
        concepts: set[str] = set()
        for step in scenario.steps:
            concepts.update(step.concepts)
            for child in step.ands:
                concepts.update(child.concepts)
        if not concepts:
            return []
        if example_count(scenario) == 0 and context.child_count(node, ("examples",)) == 0:
            return [
                f"Scenario {node.name!r} names domain concepts {sorted(concepts)} but has no examples table."
            ]
        return []

class WhenNamesIntentNotInterfaceGesture(PracticeGraphRule):
    slug = "when-names-intent-not-interface-gesture"
    node_types = ("When", "Step")

    def check(self, node, context) -> list[str]:
        kw = context.step_keyword(node).casefold()
        if kw not in {"when", ""} and node.type != "When":
            return []
        text = context.step_text(node)
        if _GESTURE.search(text):
            return [f"When step {text!r} names a UI gesture; state the domain intent instead."]
        return []

class BehavioralAndSystemObservableOutcomes(PracticeGraphRule):
    slug = "behavioral-and-system-observable-outcomes"
    node_types = ("Then", "Step")

    def check(self, node, context) -> list[str]:
        kw = context.step_keyword(node).casefold()
        if kw not in {"then", ""} and node.type != "Then":
            return []
        text = context.step_text(node)
        if _INLINE_CONDITIONAL.search(text):
            return [f"Then step {text!r} embeds a conditional guard; assert an observable outcome instead."]
        return []

class FlaggedWritesIntendedGwt(PracticeGraphRule):
    slug = "flagged-writes-intended-gwt"
    node_types = ("Scenario",)

    def check(self, node, context) -> list[str]:
        evidence = context.scenario_evidence(node)
        scenario = scenario_for_graph_node(node, context)
        if scenario is not None:
            evidence = evidence or list(scenario.evidence)
        if not evidence:
            return []
        if any("intended" in item.casefold() for item in evidence):
            steps = context.child_count(node, ("steps",))
            if steps == 0:
                return [f"Scenario {node.name!r} is marked intended but has no GWT steps written."]
        return []

class GivenNamesComplexStateRootFirst(PracticeGraphRule):
    """Writing guidance only. A Given does not have to name a repository or an aggregate root."""

    slug = "given-names-complex-state-root-first"
    node_types = ("Given", "Step")

    def check(self, node, context) -> list[str]:
        return []

class ScenarioNamesContinuation(PracticeGraphRule):
    slug = "scenario-names-continuation"
    node_types = ("Then", "Step")

    def check(self, node, context) -> list[str]:
        if context.step_keyword(node).casefold() not in {"then", ""} and node.type != "Then":
            return []
        text = context.step_text(node)
        if "next story" in text.casefold() or "continues in" in text.casefold():
            return []
        if re.search(r"\bstory\b", text, re.I) and len(text.split()) > 12:
            return [
                f"Long Then {text!r} should name the next story on the map when continuing a flow."
            ]
        return []

def _and_chaining_from_graph(scenario_node, context) -> list[str]:
    """A When opens an interaction. That interaction needs a Then before the next When."""
    open_when = False
    for step in context.children(scenario_node, "steps"):
        phase = _phase(step, context)
        if phase == "when":
            if open_when:
                return [
                    f"Scenario {scenario_node.name!r} has two When steps with no Then between them; continue that interaction with And."
                ]
            open_when = True
        elif phase == "then":
            open_when = False
    if open_when:
        return [
            f"Scenario {scenario_node.name!r} has a When with no Then; add the result or chain it with And."
        ]
    return []

class ScenariosShape(PracticeGraphRule):
    slug = "scenarios-shape"
    node_types = ("Scenario",)

    def check(self, node, context) -> list[str]:
        steps = context.children(node, "steps")
        if not steps:
            return [f"Scenario {node.name!r} has no steps."]
        phases = {_phase(step, context) for step in steps}
        phases.update(_background_givens(node, context))
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

def _background_givens(scenario, context) -> set[str]:
    """A Given on the story background, or on the scenario's own background, supplies the phase."""
    found: set[str] = set()
    owners = list(context.children(scenario, "background"))
    story = _story_of(scenario)
    if story is not None:
        owners.extend(context.children(story, "background"))
    for background in owners:
        for step in context.children(background, "steps"):
            if _phase(step, context) == "given":
                found.add("given")
    return found


def _story_of(node):
    current = getattr(node, "parent", None)
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if getattr(current, "type", "") == "Story":
            return current
        current = getattr(current, "parent", None)
    return None


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

class PlainEnglishGwtSteps(PracticeGraphRule):
    slug = "plain-english-gwt-steps"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node, context) -> list[str]:
        text = (node.name or "").strip()
        if not text:
            return []
        if " " not in text and _CAMEL_STEP.match(text):
            return [f"Step {text!r} looks like code; write plain English GWT phrasing."]
        if text.isidentifier() or (text.replace("_", "").isalnum() and " " not in text):
            return [f"Step {text!r} looks like an identifier; write plain English GWT phrasing."]
        if len(text.split()) >= 2 or _PLAIN_ENGLISH.match(text):
            return []
        return []

class GwtStepsTraceToDomainOperations(PracticeGraphRule):
    slug = "gwt-steps-trace-to-domain-operations"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        name = (node.name or "").strip()
        classes = _DOMAIN_CLASS.findall(text)
        if name.isidentifier() or (name.replace("_", "").isalnum() and " " not in name):
            return [f"Step {name!r} does not trace to a domain operation; use the domain type in the step phrase."]
        if not classes:
            return []
        if any(cls.lower() in name.lower() for cls in classes):
            return []
        return [
            f"Step {name!r} does not name a domain concept ({', '.join(classes)}); tie GWT to domain operations."
        ]

class DomainOperationInTheStep(PracticeGraphRule):
    slug = "domain-operation-in-the-step"
    node_types = ("Story", "Step", "Given", "When", "Then")

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        if re.search(r"export function (?:activate|handle|process)\w*\s*\(", text):
            return ["Story shared file exports orchestration instead of calling domain methods in GWT steps."]
        return []
