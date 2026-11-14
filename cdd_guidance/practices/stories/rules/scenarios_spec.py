"""Scenario rules check a story graph: the same answer whether the graph was just loaded or read back from graph.json."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect  # noqa: E402
from mamba import before, context, description, it  # noqa: E402

from cdd_guidance.practices.stories.model.story_model import Background, Epic, Scenario, Step, StepType, Story, StoryModel  # noqa: E402
from cdd_guidance.practices.stories.rules.scenarios import (  # noqa: E402
    AndChaining,
    ExamplesTraceDomainModel,
    FlaggedWritesIntendedGwt,
    GivenNamesComplexStateRootFirst,
    OutlineRequiresManyPermutations,
)
from harness.graph.edge import EdgeType  # noqa: E402
from harness.graph.graph import Graph, Node, Source  # noqa: E402
from harness.graph.saved_graph import SavedGraph  # noqa: E402
from harness.graph.rule_context import RuleCheckContext  # noqa: E402
from harness.graph.rule_fixture import SchemaRuleRun  # noqa: E402


def _step(keyword: str, text: str, order: int) -> Step:
    return Step(text, StepType(keyword.lower()), order, keyword=keyword)


def _scenario(steps: list[tuple[str, str]], *, examples: int = 0, outline: bool = False, evidence: tuple = ()) -> Scenario:
    scenario = Scenario("Place the order")
    scenario.steps = [_step(keyword, text, order) for order, (keyword, text) in enumerate(steps, start=1)]
    for number in range(examples):
        scenario.examples[f"order {number + 1}"] = f"order {number + 1}"
    scenario.is_outline = outline
    scenario.evidence = list(evidence)
    return scenario


def _naming_an_order(*, background_examples: int = 0) -> Scenario:
    """A scenario whose When names the Order concept, with a Background of its own holding background_examples."""
    scenario = _scenario([("When", "the customer places the Order"), ("Then", "the order is placed")])
    scenario.steps[0].concepts = ["Order"]
    background = Background("an open order", 1)
    for number in range(background_examples):
        background.examples[f"order {number + 1}"] = f"order {number + 1}"
    scenario.backgrounds = [background]
    return scenario


def _loaded(scenario: Scenario, graph: Graph | None = None) -> RuleCheckContext:
    """A stories graph recorded by the story loader, so each node holds the object it was read from."""
    story = Story("Submit Order", 1)
    story.scenarios = [scenario]
    epic = Epic("Place Orders", 1)
    epic.append_story(story)
    model = StoryModel()
    model.append_epic(epic)
    practice = (graph or Graph()).practice("stories")
    model.record(practice)
    return RuleCheckContext(practice, None)


def _read_back(context: RuleCheckContext) -> RuleCheckContext:
    """The same graph as graph.json gives it back: each node a plain node holding the facts the object it was read
    from saved."""
    restored = Graph()
    restored.restored_from(SavedGraph.from_graph(context.graph))
    return RuleCheckContext(restored.practice(context.practice.key), None)


def _scenario_hits(rule, context: RuleCheckContext) -> list[str]:
    """What the rule reports on the story graph where validate runs it."""
    return SchemaRuleRun(rule, context).hits()


def _given_hits(context: RuleCheckContext) -> list[str]:
    return SchemaRuleRun(GivenNamesComplexStateRootFirst(), context).hits()


def _order_aggregate(graph: Graph) -> None:
    """A DDD model whose Order aggregate has the Order root and owns LineItem and ShippingAddress."""
    ddd = graph.practice("ddd")

    def add(kind: str, name: str) -> Node:
        node = Node(ddd, kind, f"ddd:{kind}:order:{name}", name, Source("order", 1, 1))
        node.practice.reading.in_graph.hold(node)
        return node

    aggregate = add("Aggregate", "order")
    graph.record(EdgeType("root", 1, "direct"), aggregate, add("EntityRoot", "Order"))
    for kind, name in (("Entity", "LineItem"), ("ValueObject", "ShippingAddress")):
        graph.record(EdgeType("owns", 2, "direct"), aggregate, add(kind, name))


with description("a scenario on a story graph"):
    # A process reads the practices' guidance once, for its first graph; read it here, not in the first example.
    with before.all:
        Graph()

    with context("with a second When before the first When has its Then"):
        with before.each:
            self.context = _loaded(_scenario([("When", "the customer adds a lamp"), ("When", "the customer pays"), ("Then", "the order is placed")]))

        with it("should be told to chain the second When with And"):
            expect(_scenario_hits(AndChaining(), self.context)).to(contain(
                "Scenario 'Place the order' starts a new When before the previous interaction has a Then; chain with And."
            ))

    with context("that ends after a When"):
        with before.each:
            self.context = _loaded(_scenario([("Given", "a cart with a lamp"), ("When", "the customer pays")]))

        with it("should be told it ends without a Then"):
            expect(_scenario_hits(AndChaining(), self.context)).to(equal(
                ["Scenario 'Place the order' ends after When without a Then; add Then or chain with And."]
            ))

    with context("with a Then after each When"):
        with before.each:
            steps = [("When", "the customer adds a lamp"), ("Then", "the cart holds it"), ("When", "the customer pays"), ("Then", "the order is placed")]
            self.context = _loaded(_scenario(steps))

        with it("should pass and-chaining"):
            expect(_scenario_hits(AndChaining(), self.context)).to(equal([]))

    with context("that is an outline with two examples"):
        with before.each:
            self.context = _loaded(_scenario([("When", "the customer pays"), ("Then", "the order is placed")], examples=2, outline=True))

        with it("should need more than two examples"):
            expect(len(_scenario_hits(OutlineRequiresManyPermutations(), self.context))).to(equal(1))

        with context("that is read back from graph.json"):
            with it("should still need more than two examples"):
                expect(len(_scenario_hits(OutlineRequiresManyPermutations(), _read_back(self.context)))).to(equal(1))

    with context("that is an outline with three examples"):
        with it("should pass"):
            context_ = _loaded(_scenario([("When", "the customer pays"), ("Then", "the order is placed")], examples=3, outline=True))
            expect(_scenario_hits(OutlineRequiresManyPermutations(), context_)).to(equal([]))

    with context("that is marked intended with no steps"):
        with before.each:
            self.context = _loaded(_scenario([], evidence=("Intended",)))

        with it("should be told to write its steps"):
            expect(len(_scenario_hits(FlaggedWritesIntendedGwt(), self.context))).to(equal(1))

        with context("that is read back from graph.json"):
            with it("should still be told to write its steps"):
                expect(len(_scenario_hits(FlaggedWritesIntendedGwt(), _read_back(self.context)))).to(equal(1))

    with context("with a long Given and no DDD model loaded"):
        with it("should pass, since nothing says which concept is an aggregate root"):
            given = "a customer named Ann has three saved payment cards on file"
            expect(_given_hits(_loaded(_scenario([("Given", given), ("When", "Ann pays")])))).to(equal([]))

    with context("with a DDD model whose Order aggregate owns line items"):
        with before.each:
            self.graph = Graph()
            _order_aggregate(self.graph)

        with context("with a Given that opens with the Order root"):
            with it("should pass"):
                given = "an Order with a line item for two lamps and a shipping address in Leeds"
                expect(_given_hits(_loaded(_scenario([("Given", given)]), self.graph))).to(equal([]))

        with context("with a Given that names a line item before its Order"):
            with it("should be told to open with the Order root"):
                given = "a line item for two lamps on the Order"
                expect(_given_hits(_loaded(_scenario([("Given", given)]), self.graph))).to(equal(
                    [f"Given {given!r} names LineItem before its aggregate root Order; open with Order, then its owned parts."]
                ))

            # The rule reads DDD's aggregates, roots, and owned parts, which a graph read back holds as plain nodes.
            with context("that is read back from graph.json"):
                with it("should still be told to open with the Order root"):
                    given = "a line item for two lamps on the Order"
                    expect(_given_hits(_read_back(_loaded(_scenario([("Given", given)]), self.graph)))).to(equal(
                        [f"Given {given!r} names LineItem before its aggregate root Order; open with Order, then its owned parts."]
                    ))

        with context("with a Given that names a shipping address and no Order"):
            with it("should be told to open with the Order root"):
                given = "a ShippingAddress in Leeds"
                expect(len(_given_hits(_loaded(_scenario([("Given", given)]), self.graph)))).to(equal(1))

    with context("that names a domain concept"):
        with context("with no examples anywhere"):
            with it("should be told to give an examples table"):
                expect(_scenario_hits(ExamplesTraceDomainModel(), _loaded(_naming_an_order()))).to(equal(
                    ["Scenario 'Place the order' names domain concepts ['Order'] but has no examples table."]
                ))

        with context("with examples in its own Background"):
            with before.each:
                self.context = _loaded(_naming_an_order(background_examples=2))

            with it("should pass"):
                expect(_scenario_hits(ExamplesTraceDomainModel(), self.context)).to(equal([]))

            with context("that is read back from graph.json"):
                with it("should still pass"):
                    expect(_scenario_hits(ExamplesTraceDomainModel(), _read_back(self.context))).to(equal([]))
