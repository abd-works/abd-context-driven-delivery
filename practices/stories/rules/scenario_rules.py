"""Scenario / GWT rules — graph + StoryModel fields."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.story_model_lookup import example_count, scenario_for_graph_node

_INLINE_CONDITIONAL = re.compile(
    r"\bwhen\s+[<{]?\w+[>}]?\s+is\s+(?:true|false)\b", re.I
)
_GESTURE = re.compile(
    r"\b(click(?:s|ed|ing)?|tap(?:s|ped|ping)?|press(?:es|ed|ing)?|button|link|field|widget|screen)\b",
    re.I,
)
_ONE_OFF = re.compile(
    r"\b(once|one[- ]time|initial setup|bootstrap only|migrate legacy)\b", re.I
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


class BranchOnMechanicalUniqueness(PracticeGraphRule):
    slug = "branch-on-mechanical-uniqueness"
    node_types = ("Epic", "SubEpic", "Story")

    def check(self, node, context) -> list[str]:
        siblings = [
            edge.child
            for edge in context.practice.edges.get("decomposedInto", [])
            if edge.parent is node and edge.child.type == "Story"
        ]
        if len(siblings) < 2:
            return []
        names = [s.name.strip().casefold() for s in siblings]
        verbs = [n.split()[0] for n in names if n.split()]
        if len(verbs) >= 2 and len(set(verbs)) == 1 and len(set(names)) > 1:
            return [
                f"Stories under {node.name!r} share the same verb {verbs[0]!r}; split by distinct mechanics or merge."
            ]
        return []


class BehavioursNotOneTimeTasks(PracticeGraphRule):
    slug = "behaviours-not-one-time-tasks"
    node_types = ("Story",)

    def check(self, node, context) -> list[str]:
        if _ONE_OFF.search(node.name or ""):
            return [f"Story {node.name!r} reads like a one-time task, not a repeatable behaviour."]
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
    steps = context.children(scenario_node, "steps")
    seen_then = False
    for step in steps:
        kw = context.step_keyword(step).casefold()
        if kw == "then":
            seen_then = True
        if kw == "when" and not seen_then:
            return [
                f"Scenario {scenario_node.name!r} has When before any Then; add Given/Then or chain with And."
            ]
    return []
