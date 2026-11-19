"""scenarios fidelity — scenario, step, given, when, and then rules.

The rules read the graph: a step's keyword, phase, text, and concepts are facts on its node, and a scenario's steps and
examples are its edges, so a graph reloaded from graph.json is checked the same way as one just loaded from files.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.stories.model.story_model import NOT_ON_STORY_MAP

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_CAMEL_STEP = re.compile(r"^[a-z]+(?:[A-Z][a-z0-9]*)+$")

_PLAIN_ENGLISH = re.compile(r"^[a-z].*(?:\s+[a-z].*)+$", re.IGNORECASE)

_INLINE_CONDITIONAL = re.compile(
    r"\bwhen\s+[<{]?\w+[>}]?\s+is\s+(?:true|false)\b", re.I
)

_GESTURE = re.compile(
    r"\b(click(?:s|ed|ing)?|tap(?:s|ped|ping)?|press(?:es|ed|ing)?|button|link|field|widget|screen)\b",
    re.I,
)

# Two alternatives read better as separate steps or scenarios; an outline earns its table with more.
_ALTERNATIVES_WITHOUT_AN_OUTLINE = 2
# A Then longer than this that mentions a story is continuing a flow into another story, so it should name that story.
_CONTINUING_THEN_WORDS = 12

# The parts of an aggregate a Given describes after naming the aggregate's root.
_OWNED_PART_TYPES = ("Entity", "ValueObject")


class AndChaining(PracticeGraphRule):
    slug = "and-chaining"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        """Flag a second When before the previous When has its Then, and a When the scenario never answers."""
        pending_when = False
        for step in context.children(node, "steps"):
            keyword = self._step_keyword(step)
            if keyword == "when" and pending_when:
                return [
                    f"Scenario {node.name!r} starts a new When before the previous interaction has a Then; chain with And."
                ]
            if keyword in ("when", "then"):
                pending_when = keyword == "when"
        if pending_when:
            return [f"Scenario {node.name!r} ends after When without a Then; add Then or chain with And."]
        return []

    def _step_keyword(self, step: Node) -> str:
        return _keyword(step).casefold() or _phase(step)

class ButMarksMissingState(PracticeGraphRule):
    slug = "but-marks-missing-state"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if _keyword(node).casefold() != "but":
            return []
        text = _text(node).casefold()
        if any(word in text for word in ("not ", "without ", "absent", "missing", "no ")):
            return []
        return [f"But step should mark missing or absent state, not a consequence: {_text(node)!r}."]

class WhenHoldsTheOperation(PracticeGraphRule):
    slug = "when-holds-the-operation"
    node_types = ("When", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if _keyword(node).casefold() not in {"when", ""}:
            if node.type not in {"When"}:
                return []
        text = _text(node)
        if not text or " and " in text.casefold():
            return []
        if len(text.split()) < 2:
            return [f"When {text!r} should name the operation under test in plain language."]
        return []

class OutlineRequiresManyPermutations(PracticeGraphRule):
    slug = "outline-requires-many-permutations"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if not self._is_outline(node):
            return []
        examples = context.child_count(node, ("examples",))
        if examples <= _ALTERNATIVES_WITHOUT_AN_OUTLINE:
            return [
                f"Scenario outline {node.name!r} needs more than two example rows (found {examples})."
            ]
        return []

    def _is_outline(self, node: Node) -> bool:
        """The scenario's node records it as an outline."""
        return bool(node.facts.get("is_outline"))

def scenario_domain_concepts(steps: list[Node]) -> set[str]:
    """The bold terms the steps name, less their actors: who acts (Customer, My Paradise) is not a concept to give an
    example of."""
    concepts: set[str] = set()
    actors: set[str] = set()
    for step in steps:
        concepts.update(step.get_fact("concepts") or [])
        if step.get_fact("actor"):
            actors.add(step.get_fact("actor"))
    return concepts - actors


class ExamplesTraceDomainModel(PracticeGraphRule):
    """A scenario's examples edges hold its own examples and those its own and its story's Backgrounds hold, so the
    rule reads only the graph."""

    slug = "examples-trace-domain-model"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        concepts = self._named_concepts(node, context)
        if not concepts or context.child_count(node, ("examples",)):
            return []
        return [f"Scenario {node.name!r} names domain concepts {sorted(concepts)} but has no examples table."]

    def _named_concepts(self, scenario: Node, context: RuleCheckContext) -> set[str]:
        """The domain concepts a scenario's steps and their And continuations name."""
        steps = [
            each
            for step in context.children(scenario, "steps")
            for each in (step, *context.children(step, "ands"))
        ]
        return scenario_domain_concepts(steps)


# An underlined term in a step, ++cart++, and the same term written as a link, ++[cart](domain-model.md#cart-…)++.
_UNDERLINED_TERM = re.compile(r"\+\+([^+\n]+?)\+\+")
_LINKED_TERM = re.compile(r"^\[[^\]]+\]\([^)]*\)$")
# The classes of the DDD model a step can name: aggregate roots, entities, and value objects.
_DOMAIN_CLASS_TYPES = ("EntityRoot", "Entity", "ValueObject")


class DomainTermsLinkToModel(PracticeGraphRule):
    """Which underlined terms are domain terms comes from the DDD model loaded beside the stories: a term that names one
    of its classes, as the class (LineItem) or as words (line item). Without a DDD model there is no heading to link
    to, so the rule passes."""

    slug = "domain-terms-link-to-model"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        classes = self._class_keys(context)
        if not classes:
            return []
        text = _text(node)
        unlinked = [
            term.strip()
            for term in _UNDERLINED_TERM.findall(text)
            if not _LINKED_TERM.match(term.strip()) and self._key(term) in classes
        ]
        if not unlinked:
            return []
        return [
            f"Step {text!r} names the domain terms {unlinked} without linking them to their headings in the domain model."
        ]

    def _class_keys(self, context: RuleCheckContext) -> set[str]:
        """Each class of the DDD model as the key a term is matched by: its name lower case, with no spaces."""
        ddd = context.practice.reading.domain_model
        if ddd is None:
            return set()
        return {self._key(node.name) for kind in _DOMAIN_CLASS_TYPES for node in ddd.in_graph.nodes(kind)}

    def _key(self, name: str) -> str:
        """The name lower case, with no spaces, hyphens, or underscores, and no plural s: line items and LineItem
        match."""
        key = re.sub(r"[\s_-]+", "", name).casefold()
        return key[:-1] if key.endswith("s") and len(key) > 3 else key


class WhenNamesIntentNotInterfaceGesture(PracticeGraphRule):
    slug = "when-names-intent-not-interface-gesture"
    node_types = ("When", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        kw = _keyword(node).casefold()
        if kw not in {"when", ""} and node.type != "When":
            return []
        text = _text(node)
        if _GESTURE.search(text):
            return [f"When step {text!r} names a UI gesture; state the domain intent instead."]
        return []

class BehavioralAndSystemObservableOutcomes(PracticeGraphRule):
    slug = "behavioral-and-system-observable-outcomes"
    node_types = ("Then", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        kw = _keyword(node).casefold()
        if kw not in {"then", ""} and node.type != "Then":
            return []
        text = _text(node)
        if _INLINE_CONDITIONAL.search(text):
            return [f"Then step {text!r} embeds a conditional guard; assert an observable outcome instead."]
        return []

class FlaggedWritesIntendedGwt(PracticeGraphRule):
    slug = "flagged-writes-intended-gwt"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if not any("intended" in item.casefold() for item in self._evidence(node)):
            return []
        if context.child_count(node, ("steps",)) == 0:
            return [f"Scenario {node.name!r} is marked intended but has no GWT steps written."]
        return []

    def _evidence(self, node: Node) -> list[str]:
        """The evidence labels the scenario's node records; none when it records none."""
        raw = node.facts.get("evidence")
        return [str(item) for item in raw] if isinstance(raw, list) else []

class GivenNamesComplexStateRootFirst(PracticeGraphRule):
    """Which concept is an aggregate root and which are its owned parts comes from the DDD model loaded beside the
    stories. Without a DDD model the graph cannot tell a root from an owned part, so the rule passes."""

    slug = "given-names-complex-state-root-first"
    node_types = ("Given", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if _keyword(node).casefold() not in {"given", ""} and node.type != "Given":
            return []
        text = _text(node)
        for part, root in self._owned_parts(context).items():
            part_at = self._first_mention(part, text)
            if part_at is None:
                continue
            root_at = self._first_mention(root, text)
            if root_at is None or root_at > part_at:
                return [f"Given {text!r} names {part} before its aggregate root {root}; open with {root}, then its owned parts."]
        return []

    def _owned_parts(self, context: RuleCheckContext) -> dict[str, str]:
        """Each entity and value object an aggregate in the DDD model owns, mapped to the name of that aggregate's root."""
        graph = context.graph
        ddd = context.practice.reading.domain_model
        if ddd is None:
            return {}
        owned: dict[str, str] = {}
        for aggregate in ddd.in_graph.nodes("Aggregate"):
            roots = [edge.child.name for edge in graph.edges.from_parent("root", aggregate)]
            if not roots:
                continue
            for edge in graph.edges.from_parent("owns", aggregate):
                if edge.child.type in _OWNED_PART_TYPES:
                    owned[edge.child.name] = roots[0]
        return owned

    def _first_mention(self, concept: str, text: str) -> int | None:
        """Where text first names a model concept, written as the class (LineItem) or as words (line items)."""
        words = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", concept) or [concept]
        pattern = r"\b" + r"[\s_-]*".join(re.escape(word) for word in words) + r"s?\b"
        found = re.search(pattern, text, re.I)
        return found.start() if found else None


class ScenarioNamesContinuation(PracticeGraphRule):
    slug = "scenario-names-continuation"
    node_types = ("Then", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if _keyword(node).casefold() not in {"then", ""} and node.type != "Then":
            return []
        text = _text(node)
        if "next story" in text.casefold() or "continues in" in text.casefold():
            return []
        if re.search(r"\bstory\b", text, re.I) and len(text.split()) > _CONTINUING_THEN_WORDS:
            return [
                f"Long Then {text!r} should name the next story on the map when continuing a flow."
            ]
        return []

class ScenariosNameAStoryOnTheMap(PracticeGraphRule):
    """A scenarios file specifies stories by their names. A story it names that the story map does not hold is read
    with its scenarios and reported here, on the story, so the file is never read as empty."""

    slug = "scenarios-name-a-story-on-the-map"
    node_types = ("Story",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        if not node.get_fact(NOT_ON_STORY_MAP):
            return []
        file = node.source.file if node.source is not None else ""
        return [
            f"Story {node.name!r} has scenarios in {file} and is not on the story map; add it to the map or name the "
            "story the scenarios belong to."
        ]


class ScenariosShape(PracticeGraphRule):
    slug = "scenarios-shape"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        steps = context.children(node, "steps")
        if not steps:
            return [f"Scenario {node.name!r} has no steps."]
        phases = self._scenario_phases(node, context, steps)
        missing = []
        if "when" not in phases:
            missing.append("When")
        if "then" not in phases:
            missing.append("Then")
        if missing:
            return [f"Scenario {node.name!r} is missing required phase(s): {', '.join(missing)}."]
        return []

    def _scenario_phases(self, scenario_node: Node, context: RuleCheckContext, steps: list[Node]) -> set[str]:
        phases = {_phase(step) for step in steps if _phase(step)}
        if "given" in phases:
            return phases
        if self._background_provides_given(scenario_node, context):
            phases.add("given")
        return phases


    def _background_provides_given(self, scenario_node: Node, context: RuleCheckContext) -> bool:
        story = self._parent_story(scenario_node, context)
        if story is None:
            return False
        for background in context.children(story, "background"):
            for step in context.children(background, "steps"):
                if _phase(step) == "given":
                    return True
        return False


    def _parent_story(self, node: Node, context: RuleCheckContext) -> Node | None:
        parent = getattr(node, "parent", None)
        while parent is not None:
            if parent.type == "Story":
                return parent
            parent = getattr(parent, "parent", None)
        for edge in context.edges("scenarios"):
            if edge.child is node:
                return edge.parent
        return None


def _keyword(step: Node) -> str:
    """Given, When, Then, And, or But, as the step's model wrote it."""
    return str(step.get_fact("keyword", "") or "")


def _text(step: Node) -> str:
    """The step's words after its keyword."""
    return str(step.get_fact("text", "") or "")


def _phase(step: Node) -> str:
    """given, when, or then from the step's type; an And or But line carries the phase of the line it continues."""
    return str(step.get_fact("phase", "") or "")


class PlainEnglishGwtSteps(PracticeGraphRule):
    slug = "plain-english-gwt-steps"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        text = _text(node).strip()
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

    def check(self, node: Node, context: RuleCheckContext) -> list[str]:
        name = _text(node).strip()
        classes = node.get_fact("domain_class_names", [])
        if name.isidentifier() or (name.replace("_", "").isalnum() and " " not in name):
            return [f"Step {name!r} does not trace to a domain operation; use the domain type in the step phrase."]
        if not classes:
            return []
        if any(cls.lower() in name.lower() for cls in classes):
            return []
        return [
            f"Step {name!r} does not name a domain concept ({', '.join(classes)}); tie GWT to domain operations."
        ]
