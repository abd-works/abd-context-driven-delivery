"""scenarios fidelity — scenario, step, given, when, and then rules."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.story_model_lookup import example_count, scenario_for_graph_node, story_of

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
        scenario = scenario_for_graph_node(node, context)
        if scenario is None:
            return _and_chaining_from_graph(node, context)
        for when_steps, then_steps in scenario.when_then_runs():
            if when_steps and not then_steps:
                return [
                    f"Scenario {node.name!r} starts a new When before the previous interaction has a Then; chain with And."
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
        story = story_of(context.story_model(), scenario)
        backgrounds = [*getattr(scenario, "backgrounds", []), *getattr(story, "backgrounds", [])]
        background_examples = sum(example_count(background) for background in backgrounds)
        if example_count(scenario) == 0 and background_examples == 0 and context.child_count(node, ("examples",)) == 0:
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
    slug = "given-names-complex-state-root-first"
    node_types = ("Given", "Step")

    def check(self, node, context) -> list[str]:
        if context.step_keyword(node).casefold() not in {"given", ""} and node.type != "Given":
            return []
        text = context.step_text(node)
        if len(text.split()) < 8:
            return []
        if not re.search(r"\b(root|aggregate|cart|order|account)\b", text, re.I):
            return [
                f"Complex Given {text!r} should open with the aggregate root before owned parts."
            ]
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
    """Flag a second When before the previous When has a matching Then."""
    steps = context.children(scenario_node, "steps")
    pending_when = False
    for step in steps:
        kw = _step_keyword(step, context)
        if kw == "when":
            if pending_when:
                return [
                    f"Scenario {scenario_node.name!r} starts a new When before the previous interaction has a Then; chain with And."
                ]
            pending_when = True
        elif kw == "then":
            pending_when = False
    if pending_when:
        return [
            f"Scenario {scenario_node.name!r} ends after When without a Then; add Then or chain with And."
        ]
    return []

class ScenariosShape(PracticeGraphRule):
    slug = "scenarios-shape"
    node_types = ("Scenario",)

    def check(self, node, context) -> list[str]:
        steps = context.children(node, "steps")
        if not steps:
            return [f"Scenario {node.name!r} has no steps."]
        phases = _scenario_phases(node, context, steps)
        missing = []
        if "when" not in phases:
            missing.append("When")
        if "then" not in phases:
            missing.append("Then")
        if missing:
            return [f"Scenario {node.name!r} is missing required phase(s): {', '.join(missing)}."]
        return []


def _scenario_phases(scenario_node, context, steps) -> set[str]:
    phases = {_phase(step, context) for step in steps if _phase(step, context)}
    if "given" in phases:
        return phases
    if _background_provides_given(scenario_node, context):
        phases.add("given")
    return phases


def _background_provides_given(scenario_node, context) -> bool:
    story = _parent_story(scenario_node, context)
    if story is None:
        return False
    for background in context.children(story, "background"):
        for step in context.children(background, "steps"):
            if _phase(step, context) == "given":
                return True
    return False


def _parent_story(node, context):
    parent = getattr(node, "parent", None)
    while parent is not None:
        if parent.type == "Story":
            return parent
        parent = getattr(parent, "parent", None)
    for edge in context.practice.edges.get("scenarios", []):
        if edge.child is node:
            return edge.parent
    return None


def _step_keyword(step, context) -> str:
    return context.step_keyword(step).casefold() or _phase(step, context)

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
