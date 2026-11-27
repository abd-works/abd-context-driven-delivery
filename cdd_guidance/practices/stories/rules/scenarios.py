"""scenarios fidelity — scenario, step, given, when, and then rules.

The rules read the graph: a step's keyword, phase, text, and concepts are facts on its node, and a scenario's steps and
examples are its edges, so a graph reloaded from graph.json is checked the same way as one just loaded from files.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.stories.model.modelled_areas import MODEL_WRITTEN_FACT
from cdd_guidance.practices.stories.model.story_map import ACTORS_FACT, NOT_ON_STORY_MAP, STORY_KIND_FACT, StoryType

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_CAMEL_STEP = re.compile(r"^[a-z]+(?:[A-Z][a-z0-9]*)+$")

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

# The parts of an aggregate a Given describes after naming the aggregate's root.
_OWNED_PART_TYPES = ("Entity", "ValueObject")


class StepRule(PracticeGraphRule):
    """A rule that reads steps: a step's keyword, words, and phase are facts on its node, so a graph read back from its
    save is checked the same way as one just read."""

    def keyword(self, step: Node) -> str:
        """given, when, then, and, or but, as the step's model wrote it, in lower case."""
        return str(step.get_fact("keyword", "") or "").casefold()

    def text(self, step: Node) -> str:
        """The step's words after its keyword."""
        return str(step.get_fact("text", "") or "")

    def phase(self, step: Node) -> str:
        """given, when, or then from the step's type; an And or But line carries the phase of the line it continues."""
        return str(step.get_fact("phase", "") or "")

    def is_a(self, step: Node, phase: str) -> bool:
        """Whether step opens with phase's keyword, or with none."""
        return self.keyword(step) in {phase, ""}


class AndChaining(StepRule):
    slug = "and-chaining"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        """Flag a second When before the previous When has its Then, and a When the scenario never answers."""
        pending_when = False
        for step in context.targets(node, "steps"):
            keyword = self._step_keyword(step)
            if keyword == "when" and pending_when:
                return [Finding(node, f"Scenario {node.name!r} starts a new When before the previous interaction has a Then; chain with And.")]
            if keyword in ("when", "then"):
                pending_when = keyword == "when"
        if pending_when:
            return [Finding(node, f"Scenario {node.name!r} ends after When without a Then; add Then or chain with And.")]
        return []

    def _step_keyword(self, step: Node) -> str:
        return self.keyword(step) or self.phase(step)

class ButMarksMissingState(StepRule):
    slug = "but-marks-missing-state"
    requires_judge = True
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if self.keyword(node) != "but":
            return []
        text = self.text(node).casefold()
        if any(word in text for word in ("not ", "without ", "absent", "missing", "no ")):
            return []
        return [Finding(node, f"But step should mark missing or absent state, not a consequence: {self.text(node)!r}.")]

class WhenHoldsTheOperation(StepRule):
    slug = "when-holds-the-operation"
    node_types = ("When", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not self.is_a(node, "when"):
            if node.type not in {"When"}:
                return []
        text = self.text(node)
        if not text or " and " in text.casefold():
            return []
        if len(text.split()) < 2:
            return [Finding(node, f"When {text!r} should name the operation under test in plain language.")]
        return []

class OutlineRequiresManyPermutations(PracticeGraphRule):
    slug = "outline-requires-many-permutations"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not self._is_outline(node):
            return []
        examples = len(context.targets(node, "examples"))
        if examples <= _ALTERNATIVES_WITHOUT_AN_OUTLINE:
            return [Finding(node, f"Scenario outline {node.name!r} needs more than two example rows (found {examples}).")]
        return []

    def _is_outline(self, node: Node) -> bool:
        """The scenario's node records it as an outline."""
        return bool(node.facts.get("is_outline"))

class ExamplesTraceDomainModel(PracticeGraphRule):
    """A scenario's examples edges hold its own examples and those its own and its story's Backgrounds hold, so the
    rule reads only the graph."""

    slug = "examples-trace-domain-model"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        concepts = self._named_concepts(node, context)
        if not concepts or len(context.targets(node, "examples")):
            return []
        return [Finding(node, f"Scenario {node.name!r} names domain concepts {sorted(concepts)} but has no examples table.")]

    def _named_concepts(self, scenario: Node, context: RuleCheckContext) -> set[str]:
        """The domain concepts a scenario's steps and their And continuations name."""
        steps = [
            each
            for step in context.targets(scenario, "steps")
            for each in (step, *context.targets(step, "ands"))
        ]
        return self.domain_concepts(steps)

    def domain_concepts(self, steps: list[Node]) -> set[str]:
        """The bold terms the steps name, less their actors: who acts (Customer, My Paradise) is not a concept to give an
        example of."""
        concepts: set[str] = set()
        actors: set[str] = set()
        for step in steps:
            concepts.update(step.get_fact("concepts") or [])
            if step.get_fact("actor"):
                actors.add(step.get_fact("actor"))
        return concepts - actors


# An underlined term in a step, ++cart++, and the same term written as a link, ++[cart](domain-model.md#cart-…)++.
_UNDERLINED_TERM = re.compile(r"\+\+([^+\n]+?)\+\+")
_LINKED_TERM = re.compile(r"^\[[^\]]+\]\([^)]*\)$")
# The classes of the DDD model a step can name: aggregate roots, entities, and value objects.
_DOMAIN_CLASS_TYPES = ("EntityRoot", "Entity", "ValueObject")


class DomainTermsLinkToModel(StepRule):
    """Which underlined terms are domain terms comes from the models loaded beside the stories: the DDD domain model's
    classes, and the classes a Clean Engineering model document (``*-model.md``) declares. A term that names one of
    them, as the class (LineItem) or as words (line item), is a domain term. Without either model there is no heading
    to link to, so the rule passes."""

    slug = "domain-terms-link-to-model"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        classes = self._class_keys(context)
        if not classes:
            return []
        text = self.text(node)
        # The markdown reader keeps the step's words without their links and records the terms its line linked.
        linked = {self._key(term) for term in node.get_fact("linked_terms", []) or []}
        unlinked = [
            term.strip()
            for term in _UNDERLINED_TERM.findall(text)
            if not _LINKED_TERM.match(term.strip()) and self._key(term) in classes - linked
        ]
        if not unlinked:
            return []
        return [Finding(node, f"Step {text!r} names the domain terms {unlinked} without linking them to their headings in the domain model.")]

    def _class_keys(self, context: RuleCheckContext) -> set[str]:
        """Each class of the DDD model, and each class a Clean Engineering model document declares, as the key a term
        is matched by: its name lower case, with no spaces. Classes read from code are left out: a model document is
        what a term links to."""
        reading = context.practice.reading
        keys: set[str] = set()
        ddd = reading.domain_model
        if ddd is not None:
            keys |= {self._key(node.name) for kind in _DOMAIN_CLASS_TYPES for node in ddd.in_graph.nodes(kind)}
        clean = reading.object_model
        if clean is not None:
            keys |= {
                self._key(node.name)
                for node in clean.in_graph.nodes("OoadClass")
                if node.source is not None and (node.source.file or "").endswith("-model.md")
            }
        return keys

    def _key(self, name: str) -> str:
        """The name lower case, with no spaces, hyphens, or underscores, and no plural s: line items and LineItem
        match."""
        key = re.sub(r"[\s_-]+", "", name).casefold()
        return key[:-1] if key.endswith("s") and len(key) > 3 else key


class WhenNamesIntentNotInterfaceGesture(StepRule):
    slug = "when-names-intent-not-interface-gesture"
    requires_judge = True
    node_types = ("When", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not self.is_a(node, "when") and node.type != "When":
            return []
        text = self.text(node)
        if _GESTURE.search(text):
            return [Finding(node, f"When step {text!r} names a UI gesture; state the domain intent instead.")]
        return []

class BehavioralAndSystemObservableOutcomes(StepRule):
    slug = "behavioral-and-system-observable-outcomes"
    node_types = ("Then", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not self.is_a(node, "then") and node.type != "Then":
            return []
        text = self.text(node)
        if _INLINE_CONDITIONAL.search(text):
            return [Finding(node, f"Then step {text!r} embeds a conditional guard; assert an observable outcome instead.")]
        return []

class ThenObservesAnExample(StepRule):
    """Whether a model is written for a Then's area of the story map is a fact the Stories reading records on the
    Then (*ModelledAreas*); with none written the rule passes, so scenarios can be written before any model."""

    slug = "then-observes-an-example"
    node_types = ("Then", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if self.phase(node) != "then" or not node.get_fact(MODEL_WRITTEN_FACT) or context.targets(node, "observes"):
            return []
        return [Finding(node, f"Then {self.text(node)!r} observes no Example, though a model is written for its area of the story map; "
            "name an example in it, or in a Given of its scenario or of its story's Background.")]


class FlaggedWritesIntendedGwt(PracticeGraphRule):
    slug = "flagged-writes-intended-gwt"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not any("intended" in item.casefold() for item in self._evidence(node)):
            return []
        if len(context.targets(node, "steps")) == 0:
            return [Finding(node, f"Scenario {node.name!r} is marked intended but has no GWT steps written.")]
        return []

    def _evidence(self, node: Node) -> list[str]:
        """The evidence labels the scenario's node records; none when it records none."""
        raw = node.facts.get("evidence")
        return [str(item) for item in raw] if isinstance(raw, list) else []

class GivenNamesComplexStateRootFirst(StepRule):
    """Which concept is an aggregate root and which are its owned parts comes from the DDD model loaded beside the
    stories. Without a DDD model the graph cannot tell a root from an owned part, so the rule passes."""

    slug = "given-names-complex-state-root-first"
    node_types = ("Given", "Step")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not self.is_a(node, "given") and node.type != "Given":
            return []
        text = self.text(node)
        earlier = " ".join(self.text(step) for step in self._earlier_steps(node, context))
        for part, root in self._owned_parts(context).items():
            part_at = self._first_mention(part, text)
            if part_at is None or self._first_mention(root, earlier) is not None:
                continue
            root_at = self._first_mention(root, text)
            if root_at is None or root_at > part_at:
                return [Finding(node, f"Given {text!r} names {part} before its aggregate root {root}; open with {root}, then its owned parts.")]
        return []

    def _earlier_steps(self, step: Node, context: RuleCheckContext) -> list[Node]:
        """Its story's background steps and the steps before it in its scenario: a root one of them names is already
        open, so a later step may name that root's parts alone."""
        for edge in context.edges("steps"):
            if edge.child is step:
                steps = context.targets(edge.parent, "steps")
                before = [each for earlier in steps[: steps.index(step)] for each in self._with_ands(earlier, context)]
                tree = context.practice.reading.story_tree
                return tree.background_steps(tree.story_of(edge.parent)) + before
        # An And or But line is held among the ands of the step it continues.
        for edge in context.edges("ands"):
            if edge.child is step:
                ands = context.targets(edge.parent, "ands")
                before = [each for earlier in ands[: ands.index(step)] for each in self._with_ands(earlier, context)]
                return self._earlier_steps(edge.parent, context) + [edge.parent] + before
        return []

    def _with_ands(self, step: Node, context: RuleCheckContext) -> list[Node]:
        """The step and every And or But line that continues it."""
        return [step, *(each for continued in context.targets(step, "ands") for each in self._with_ands(continued, context))]

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
        # A word joined to another by a hyphen describes it, as "line" does in "one-line cart", so it is no mention.
        pattern = r"(?<![\w-])" + r"[\s_-]*".join(re.escape(word) for word in words) + r"s?(?![\w-])"
        found = re.search(pattern, text, re.I)
        return found.start() if found else None


class ScenariosNameAStoryOnTheMap(PracticeGraphRule):
    """A scenarios file specifies stories by their names. A story it names that the story map does not hold is read
    with its scenarios and reported here, on the story, so the file is never read as empty."""

    slug = "scenarios-name-a-story-on-the-map"
    node_types = ("Story",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        if not node.get_fact(NOT_ON_STORY_MAP):
            return []
        file = node.source.file if node.source is not None else ""
        return [Finding(node, f"Story {node.name!r} has scenarios in {file} and is not on the story map; add it to the map or name the "
            "story the scenarios belong to.")]


class ScenariosShape(StepRule):
    slug = "scenarios-shape"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        steps = context.targets(node, "steps")
        if not steps:
            return [Finding(node, f"Scenario {node.name!r} has no steps.")]
        phases = self._scenario_phases(node, context, steps)
        missing = []
        if "when" not in phases:
            missing.append("When")
        if "then" not in phases:
            missing.append("Then")
        if missing:
            return [Finding(node, f"Scenario {node.name!r} is missing required phase(s): {', '.join(missing)}.")]
        return []

    def _scenario_phases(self, scenario_node: Node, context: RuleCheckContext, steps: list[Node]) -> set[str]:
        phases = {self.phase(step) for step in steps if self.phase(step)}
        if "given" in phases:
            return phases
        if self._background_provides_given(scenario_node, context):
            phases.add("given")
        return phases


    def _background_provides_given(self, scenario_node: Node, context: RuleCheckContext) -> bool:
        tree = context.practice.reading.story_tree
        return any(self.phase(step) == "given" for step in tree.background_steps(tree.story_of(scenario_node)))


class PlainEnglishGwtSteps(StepRule):
    slug = "plain-english-gwt-steps"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        text = self.text(node).strip()
        if not text:
            return []
        if " " not in text and _CAMEL_STEP.match(text):
            return [Finding(node, f"Step {text!r} looks like code; write plain English GWT phrasing.")]
        if text.isidentifier() or (text.replace("_", "").isalnum() and " " not in text):
            return [Finding(node, f"Step {text!r} looks like an identifier; write plain English GWT phrasing.")]
        return []

class GwtStepsTraceToDomainOperations(StepRule):
    slug = "gwt-steps-trace-to-domain-operations"
    requires_judge = True
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        name = self.text(node).strip()
        classes = node.get_fact("domain_class_names", [])
        if name.isidentifier() or (name.replace("_", "").isalnum() and " " not in name):
            return [Finding(node, f"Step {name!r} does not trace to a domain operation; use the domain type in the step phrase.")]
        if not classes:
            return []
        if any(cls.lower() in name.lower() for cls in classes):
            return []
        return [Finding(node, f"Step {name!r} does not name a domain concept ({', '.join(classes)}); tie GWT to domain operations.")]


# A step's subject, then the verb that says the subject is, or holds, what follows: its predicate.
_PREDICATE = re.compile(r"^(?P<subject>.*?\S)\s+(?P<verb>is|has)\s+(?P<predicate>.+?)[\s.]*$", re.I)
_ARTICLE = re.compile(r"^(?:the|a|an)\s+", re.I)
# A term the markdown scenarios underline as a whole, ++Me on the checklist++, which names an example or a term.
_WHOLLY_UNDERLINED = re.compile(r"^\+\+([^+]+)\+\+$")
# The marks a step's words carry in a markdown scenarios file: bold actors, underlined terms, backticks.
_STEP_MARKS = re.compile(r"\*\*|\+\+|`")
# What splits an example's name written as code into words: paidOrder, paid_order.
_NAME_WORD_BREAK = re.compile(r"_+|(?<=[a-z0-9])(?=[A-Z])")
# Words that join others and name nothing in the domain.
_LINKING_WORDS = frozenset({"the", "a", "an", "to", "of", "on", "in", "for", "from", "with", "and", "or", "by", "at", "as", "up", "set", "is", "has"})
# The share of the fewer Thens two scenarios must have in common to say the same: more than half.
_SAME_OUTCOME_SHARE = 0.5


def _plain(text: str) -> str:
    """A step's words as a reader reads them: no markup, one space between words, in lower case."""
    return " ".join(_STEP_MARKS.sub("", text).split()).casefold().rstrip(" .")


def _naming_words(text: str) -> set[str]:
    """The words of text that can name something, each without a plural s."""
    words = re.findall(r"[a-z0-9]+", _plain(_NAME_WORD_BREAK.sub(" ", text)))
    return {word.rstrip("s") for word in words if word not in _LINKING_WORDS}


def _with_ands(steps: list[Node], context: RuleCheckContext) -> list[Node]:
    """steps, each followed by the And and But steps chained onto it."""
    return [held for step in steps for held in (step, *context.targets(step, "ands"))]


class StepSaysMoreThanAnExampleName(StepRule):
    """A step's predicate is the state it gives, the action it takes, or the outcome it checks. When the whole predicate
    after ``is`` or ``has`` is one example's name and that name holds no domain word, as in ``the cart is Me on the
    checklist``, the step tells a reader nothing they can follow without opening the example. An example is named by
    a term the markdown underlines as a whole, or, in a story test, by the plain words of an example the step uses. The
    domain words are those the story map names the step's area with, its epic or sub-epic and that area's stories, and
    the terms, concepts and classes the story's steps name."""

    slug = "step-says-more-than-an-example-name"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        found = _PREDICATE.match(self.text(node).strip())
        if found is None:
            return []
        name = self._example_named(_ARTICLE.sub("", found.group("predicate").strip()), node, context)
        if not name or _naming_words(name) & self._domain_words(node, context):
            return []
        subject, verb = _plain(found.group("subject")), found.group("verb").casefold()
        return [Finding(node, f"Step {self.text(node)!r} says only that {subject} {verb} the example {name!r}; say in domain "
            f"words what {subject} holds or is, so a reader can follow the step without opening the example.")]

    def _example_named(self, predicate: str, node: Node, context: RuleCheckContext) -> str:
        """The example the whole predicate names: an underlined term, or the plain words of an example the step uses;
        empty when the predicate says anything more."""
        underlined = _WHOLLY_UNDERLINED.match(predicate)
        if underlined is not None:
            return underlined.group(1).strip()
        said = _plain(predicate)
        for example in context.targets(node, "observes"):
            if " ".join(_NAME_WORD_BREAK.sub(" ", example.name).split()).casefold() == said:
                return predicate
        return ""

    def _domain_words(self, node: Node, context: RuleCheckContext) -> set[str]:
        """The domain words of the step's story: the names of its area of the story map, the epic or sub-epic it sits
        under and that area's stories, and the terms its steps link to the domain model, the concepts and domain classes
        they name, and the classes the model links them to."""
        tree = context.practice.reading.story_tree
        story = tree.story_of(node)
        scenarios = tree.scenarios(story) if story is not None else []
        steps = [step for scenario in scenarios for step in _with_ands(tree.steps(scenario), context)] or [node]
        terms: list[str] = [story.name] if story is not None else []
        area = tree.area_of(story) if story is not None else None
        if area is not None and area is not story:
            terms.extend([area.name, *(named.name for named in tree.stories_under(area))])
        for step in steps:
            for fact in ("linked_terms", "concepts", "domain_class_names"):
                terms.extend(str(term) for term in step.get_fact(fact) or [])
            terms.extend(target.name for target in context.targets(step, "names"))
        return {word for term in terms for word in _naming_words(term)}


class ScenariosDifferInWhenOrOutcome(StepRule):
    """Two scenarios of one story that run the same When, by its words or by the first operation its realization calls,
    and whose Thens mostly say the same, specify one behaviour twice. The Thens say the same when more than half of the
    fewer Thens are said by the other scenario too, word for word or as the start of a longer Then that only adds detail
    after a comma; a Then that goes on otherwise, as ``stores the porting as verified``, says something else."""

    slug = "scenarios-differ-in-when-or-outcome"
    node_types = ("Story",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        tree = context.practice.reading.story_tree
        scenarios = tree.scenarios(node)
        findings: list[Finding] = []
        for index, first in enumerate(scenarios):
            for second in scenarios[index + 1:]:
                if self._same_when(first, second, context) and self._same_outcome(first, second, context):
                    findings.append(Finding(second, f"Scenario {second.name!r} runs the same When as {first.name!r} in story "
                        f"{node.name!r} and checks mostly the same Thens; merge them into one scenario, or make each show a "
                        "different case."))
        return findings

    def _same_when(self, first: Node, second: Node, context: RuleCheckContext) -> bool:
        ones, others = self._when_of(first, context), self._when_of(second, context)
        if ones is None or others is None:
            return False
        return ones[0] == others[0] or (bool(ones[1]) and ones[1] == others[1])

    def _when_of(self, scenario: Node, context: RuleCheckContext) -> tuple[str, str] | None:
        """The scenario's first When, as its words and the first operation its realization calls; none without one."""
        when = next((step for step in _with_ands(context.targets(scenario, "steps"), context) if self.phase(step) == "when"), None)
        if when is None:
            return None
        calls = when.get_fact("realization_calls") or []
        return _plain(self.text(when)), "".join(str(calls[0]).split()) if calls else ""

    def _same_outcome(self, first: Node, second: Node, context: RuleCheckContext) -> bool:
        ones, others = self._thens(first, context), self._thens(second, context)
        fewer, more = (ones, others) if len(ones) <= len(others) else (others, ones)
        if not fewer:
            return False
        said = [then for then in fewer if any(_says_as_much(then, other) for other in more)]
        return len(said) > len(fewer) * _SAME_OUTCOME_SHARE

    def _thens(self, scenario: Node, context: RuleCheckContext) -> list[str]:
        steps = _with_ands(context.targets(scenario, "steps"), context)
        return [_plain(self.text(step)) for step in steps if self.phase(step) == "then"]


def _says_as_much(then: str, other: str) -> bool:
    """Whether two Thens say the same: the same words, or one the start of the other, which only adds detail after a
    comma."""
    shorter, longer = sorted((then, other), key=len)
    return shorter == longer or (longer.startswith(shorter) and longer[len(shorter):].startswith(","))


class PersonStoriesShowThePersonActing(StepRule):
    """A story whose actor is a person is that person's interaction with the product, and the design canvas shows each
    of its scenarios as what the person does on a screen. A scenario of such a story whose Whens name only the system
    looking something up has no person action to show: merge it into a scenario the person acts in, or move it to a
    system story. A person is the actor of any user story on the map, so a When in which another person acts, such as
    the Customer signing in on an Administrator's story, still shows a person on a screen. A When names the person by
    the actor its line marks, or by opening with the actor's name."""

    slug = "person-stories-show-the-person-acting"
    node_types = ("Scenario",)

    def check(self, node: Node, context: RuleCheckContext) -> list[Finding]:
        story = context.practice.reading.story_tree.story_of(node)
        if story is None or story.get_fact(STORY_KIND_FACT) != StoryType.USER.value:
            return []
        actors = [str(actor).strip() for actor in story.get_fact(ACTORS_FACT) or [] if str(actor).strip()]
        whens = [step for step in _with_ands(context.targets(node, "steps"), context) if self.phase(step) == "when"]
        if not actors or not whens or any(self._acts(when, [*actors, *self._people(context)]) for when in whens):
            return []
        said = "; ".join(repr(self.text(when)) for when in whens)
        return [Finding(node, f"Scenario {node.name!r} of the {actors[0]}'s story {story.name!r} has no When in which the "
            f"{actors[0]} acts ({said}); merge it into a scenario the {actors[0]} acts in, or move it to a system story.")]

    @staticmethod
    def _people(context: RuleCheckContext) -> list[str]:
        """The actors of every user story on the story map: the people the product serves."""
        stories = [story for story in context.nodes("Story") if story.get_fact(STORY_KIND_FACT) == StoryType.USER.value]
        actors = (str(actor).strip() for story in stories for actor in story.get_fact(ACTORS_FACT) or [])
        return list(dict.fromkeys(actor for actor in actors if actor))

    def _acts(self, when: Node, actors: list[str]) -> bool:
        marked = str(when.get_fact("actor") or "").strip().casefold()
        opening = _ARTICLE.sub("", _plain(self.text(when)))
        return any(marked == actor.casefold() or opening.startswith(actor.casefold()) for actor in actors)
