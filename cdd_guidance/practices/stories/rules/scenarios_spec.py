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
    DomainTermsLinkToModel,
    ExamplesTraceDomainModel,
    FlaggedWritesIntendedGwt,
    GivenNamesComplexStateRootFirst,
    OutlineRequiresManyPermutations,
)
from harness.graph.edge import EdgeType  # noqa: E402
from harness.graph.graph import Graph, Node, Source  # noqa: E402
from harness.graph.saved_graph import NodeIdentity
from harness.graph.saved_graph import SavedGraph  # noqa: E402
from harness.graph.rule_context import RuleCheckContext  # noqa: E402
from harness.graph.rule_fixture import RuleFixture, SchemaRuleRun  # noqa: E402
from cdd_guidance.practices.stories.stories import Stories  # noqa: E402


def _step(keyword: str, text: str, order: int, phase: StepType) -> Step:
    step = Step(text, phase, order)
    step.keyword = keyword
    return step


def _scenario(steps: list[tuple[str, str]], *, examples: int = 0, outline: bool = False, evidence: tuple = ()) -> Scenario:
    """A scenario of steps, each a keyword and its words; an And or But continues the step before it, among that
    step's ands, as the markdown reader holds it."""
    scenario = Scenario("Place the order")
    held: list[Step] = []
    for keyword, text in steps:
        if keyword.lower() in ("and", "but") and held:
            previous = held[-1]
            previous.ands = [*previous.ands, _step(keyword, text, len(previous.ands) + 1, previous.step_type)]
        else:
            held.append(_step(keyword, text, len(held) + 1, StepType(keyword.lower())))
    scenario.steps = held
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
    epic.stories.append(story)
    model = StoryModel()
    model.epics.append(epic)
    practice = (graph or Graph()).practices.named("stories")
    model.record(practice)
    return RuleCheckContext(practice)


def _read_back(context: RuleCheckContext) -> RuleCheckContext:
    """The same graph as graph.json gives it back: each node a plain node holding the facts the object it was read
    from saved."""
    restored = Graph()
    restored.practices.restore(SavedGraph.from_graph(context.graph))
    return RuleCheckContext(restored.practices.named(context.practice.key))


def _scenario_hits(rule, context: RuleCheckContext) -> list[str]:
    """What the rule reports on the story graph where validate runs it."""
    return SchemaRuleRun(rule, context).hits()


def _given_hits(context: RuleCheckContext) -> list[str]:
    return SchemaRuleRun(GivenNamesComplexStateRootFirst(), context).hits()


def _term_hits(context: RuleCheckContext) -> list[str]:
    return SchemaRuleRun(DomainTermsLinkToModel(), context).hits()


def _order_aggregate(graph: Graph) -> None:
    """A DDD model whose Order aggregate has the Order root and owns LineItem and ShippingAddress."""
    ddd = graph.practices.named("ddd")

    def add(kind: str, name: str) -> Node:
        node = Node(ddd, NodeIdentity(type=kind, node_id=f"ddd:{kind}:order:{name}", name=name), Source("order", 1, 1))
        node.practice.reading.in_graph.hold(node)
        return node

    aggregate = add("Aggregate", "order")
    graph.edges.record(EdgeType("root", 1, "direct"), aggregate, add("EntityRoot", "Order"))
    for kind, name in (("Entity", "LineItem"), ("ValueObject", "ShippingAddress")):
        graph.edges.record(EdgeType("owns", 2, "direct"), aggregate, add(kind, name))


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

        # An example name such as "one-line-item order" uses the part's words to describe the root, not to name the part.
        with context("with a Given whose example name joins a part's words to the root by a hyphen"):
            with it("should pass"):
                given = "the ++two-line-item Order++ ships to Leeds"
                expect(_given_hits(_loaded(_scenario([("Given", given)]), self.graph))).to(equal([]))

        with context("with an And that names a line item after an earlier Given opened with the Order"):
            with it("should pass, since the scenario already opened with the root"):
                steps = [("Given", "an Order for two lamps"), ("And", "its line item for the lamps is backordered")]
                expect(_given_hits(_loaded(_scenario(steps), self.graph))).to(equal([]))

            with context("that is read back from graph.json"):
                with it("should still pass"):
                    steps = [("Given", "an Order for two lamps"), ("And", "its line item for the lamps is backordered")]
                    expect(_given_hits(_read_back(_loaded(_scenario(steps), self.graph)))).to(equal([]))

        # A Background above a story's scenarios is the state they share; the reader copies it into each scenario.
        with context("read from a scenarios file whose shared Background opens with the Order"):
            with before.each:
                self.fixture = RuleFixture(Stories, {
                    "story-map.md": "# (E) Sell Lamps\n## (E) Take Orders\n### (S) Customer --> Place Order\n",
                    "story_tests/sell-lamps/take-orders/take_orders_story.test.md": (
                        "# Sub-epic: Take Orders\n\n## Story: Place Order\n\n"
                        "### Background\n\n*Given* an Order for two lamps\n\n"
                        "#### Scenario: Order two lamps\n\n"
                        "*Given* its line item for the lamps is in stock\n"
                        "*When* the **Customer** places the order\n*Then* the order is placed\n\n"
                        "#### Scenario: Order backordered lamps\n\n"
                        "*Given* its line item for the lamps is backordered\n"
                        "*When* the **Customer** places the order\n*Then* the order waits for the lamps\n"
                    ),
                })
                _order_aggregate(self.fixture.practice.reading.graph)

            with it("should pass a scenario's Given that names a line item alone"):
                expect(self.fixture.hits(GivenNamesComplexStateRootFirst())).to(equal([]))

            with it("should read the Background's step from the scenarios file"):
                steps = [node for node in self.fixture.practice.reading.in_graph.nodes("Given") if node.get_fact("text") == "an Order for two lamps"]
                expect([node.source.file for node in steps]).to(equal(["story_tests/sell-lamps/take-orders/take_orders_story.test.md"]))

        with context("with an And that names a line item before any Given names the Order"):
            with it("should be told to open with the Order root"):
                steps = [("Given", "a customer named Ann"), ("And", "a line item for two lamps")]
                expect(len(_given_hits(_loaded(_scenario(steps), self.graph)))).to(equal(1))

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


    with context("whose step underlines a domain term"):
        with context("with no DDD model loaded"):
            with it("should pass, since there is no model to link to"):
                given = "an ++order++ with two lamps"
                expect(_term_hits(_loaded(_scenario([("Given", given)])))).to(equal([]))

        with context("with a DDD model whose Order aggregate owns line items"):
            with before.each:
                self.graph = Graph()
                _order_aggregate(self.graph)

            with context("with the term linked to its heading in the domain model"):
                with it("should pass"):
                    given = "an ++[order](../domain-model.md#order-aggregate-root-entity)++ with a ++[line item](../domain-model.md#lineitem-entity)++"
                    expect(_term_hits(_loaded(_scenario([("Given", given)]), self.graph))).to(equal([]))

            with context("with the term left unlinked"):
                with it("should be told to link it to the domain model"):
                    given = "an ++order++ with a ++line item++ for two lamps"
                    expect(_term_hits(_loaded(_scenario([("Given", given)]), self.graph))).to(equal([
                        f"Step {given!r} names the domain terms ['order', 'line item'] without linking them to their headings in the domain model."
                    ]))

                with context("that is read back from graph.json"):
                    with it("should still be told to link it"):
                        given = "an ++order++ with two lamps"
                        expect(len(_term_hits(_read_back(_loaded(_scenario([("Given", given)]), self.graph))))).to(equal(1))

            with context("with an underlined example name that is no domain class"):
                with it("should pass"):
                    given = "an ++[order](../domain-model.md#order-aggregate-root-entity)++ holding ++two lamps++"
                    expect(_term_hits(_loaded(_scenario([("Given", given)]), self.graph))).to(equal([]))

        # The markdown reader keeps a step's words without their links, so the rule reads which terms were linked from
        # what the reader recorded off the line.
        with context("read from a scenarios file, with a DDD model whose Order aggregate owns line items"):
            with before.each:
                self.fixture = RuleFixture(Stories, {
                    "story-map.md": "# (E) Sell Lamps\n## (E) Take Orders\n### (S) Customer --> Place Order\n",
                    "story_tests/sell-lamps/take-orders/take_orders_story.test.md": (
                        "# Sub-epic: Take Orders\n\n## Story: Place Order\n\n#### Scenario: Order two lamps\n\n"
                        "*Given* an ++[order](../domain-model.md#order-aggregate-root-entity)++ with two lamps\n"
                        "*And* a ++line item++ for the lamps\n"
                        "*When* the **Customer** places the order\n"
                        "*Then* the order is placed\n"
                    ),
                })
                _order_aggregate(self.fixture.practice.reading.graph)

            with it("should be told to link only the term the file left unlinked"):
                expect(self.fixture.hits(DomainTermsLinkToModel())).to(equal([
                    "Step 'a ++line item++ for the lamps' names the domain terms ['line item'] without linking them to their headings in the domain model."
                ]))
