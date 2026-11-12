"""Content conforms to its schema: every node has each relationship its schema type requires, up to the fidelity its
practice works at, by its practice's schema and the schemas of the patterns its graph applies."""

from expects import be_empty, contain, equal, expect
from mamba import before, description, it

from harness.graph.graph import Graph, Source
from harness.graph.rule_context import RuleCheckContext
from harness.graph.rule_fixture import RuleFixture
from harness.graph.schema_conformance import ConformsToSchema
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays
from cdd_guidance.practices.stories.stories import Stories


def _working_at(graph: Graph, key: str, fidelity: str):
    """The graph's practice called key, working at fidelity, as a session sets it."""
    practice = graph.practice(key)
    practice.fidelities.current = practice.fidelities.entries[fidelity]
    return practice


def _node(practice, type: str, name: str):
    return practice.reading.in_graph.add_named(type, f"{practice.key}:{type}:{name}", name, Source(f"{name}.py", 1, 1))


_STORY_MAP = """\
# Story Map — Checkout

(E) Check Out
    (E) Pay
        (S) Shopper --> Pay For Order
"""

_STORY_TEST = """\
# Sub-epic: Pay

## Story: Pay For Order

#### Scenario: Pay by card

*Given* the cart holds a book
*When* the Shopper pays by card
*Then* the order is paid

#### Scenario: Pay later
"""


def stories_fixture(files: dict[str, str]) -> RuleFixture:
    """The story test files, read by Stories as a live load reads a working copy."""
    return RuleFixture(Stories, files)


def _gaps(practice) -> list[str]:
    """Each gap the rule finds in practice, as it records them."""
    return [message for _, message in ConformsToSchema().check_practice(RuleCheckContext(practice, None))]


with description("conforms to schema"):
    with description("clean engineering worked at code"):
        with before.each:
            self.graph = Graph()
            self.practice = _working_at(self.graph, "clean_engineering", "code")
            self.cart = _node(self.practice, "OoadClass", "Cart")
            self.clear = _node(self.practice, "Operation", "clear")
            self.graph.link("owns", self.cart, self.clear)
            self.lines = _node(self.practice, "Relationship", "lines")

        with description("a relationship with no target"):
            with it("should fail naming the missing relationship, its target, and the schema requiring it"):
                expect(_gaps(self.practice)).to(contain(
                    "Relationship 'lines' has no target relationship to OoadClass | Class, which the clean_engineering practice schema requires."
                ))

            with it("should record its gap on the node when the graph checks the practice"):
                self.practice.reading.in_graph.rule_run.check()
                recorded = [violation.message for violation in self.lines.rules[ConformsToSchema.slug].violations]
                expect(recorded).to(contain(
                    "Relationship 'lines' has no target relationship to OoadClass | Class, which the clean_engineering practice schema requires."
                ))

        with description("a relationship with its target"):
            with it("should pass"):
                self.graph.link("target", self.lines, _node(self.practice, "OoadClass", "Line"), "relationship")
                expect([gap for gap in _gaps(self.practice) if "'lines'" in gap]).to(be_empty)

        with description("an operation with no parameters"):
            with it("should not fail the empty list"):
                expect([gap for gap in _gaps(self.practice) if "parameters" in gap]).to(be_empty)

        with description("a class naming no base class"):
            with it("should not require the optional relationship"):
                expect([gap for gap in _gaps(self.practice) if "baseClass" in gap]).to(be_empty)

        with it("should be checked by every practice without its schema listing it"):
            expect(list(self.practice.reading.checks())).to(contain(ConformsToSchema.slug))

        with it("should be a rule of every node"):
            expect(self.clear.rules.slugs).to(contain(ConformsToSchema.slug))

    with description("a scenario of a story test read from its file"):
        with before.each:
            self.fixture = stories_fixture({"story-map.md": _STORY_MAP, "check-out/pay/pay_story.test.md": _STORY_TEST})

        with description("with its given, when, and then steps"):
            with it("should hold the steps a scenario requires, each read as its Given, When, or Then"):
                expect([gap for gap in self.fixture.hits(ConformsToSchema()) if "'Pay by card'" in gap]).to(be_empty)

        with description("with no steps"):
            with it("should fail for the steps it lacks"):
                expect(self.fixture.hits(ConformsToSchema())).to(contain(
                    "Scenario 'Pay later' has no steps relationship to Step | Given | When | Then | Background, which the stories practice schema requires."
                ))

    with description("a story with no scenarios"):
        with before.each:
            self.graph = Graph()

        with description("worked at the story map"):
            with it("should not require the scenarios a later fidelity creates"):
                practice = _working_at(self.graph, "stories", "story_map")
                _node(practice, "Story", "Check out")
                expect([gap for gap in _gaps(practice) if "scenarios" in gap]).to(be_empty)

        with description("worked at scenarios"):
            with it("should require its scenarios"):
                practice = _working_at(self.graph, "stories", "scenarios")
                _node(practice, "Story", "Check out")
                expect(_gaps(practice)).to(contain(
                    "Story 'Check out' has no scenarios relationship to Scenario, which the stories practice schema requires."
                ))

    with description("an aggregate with no route"):
        with before.each:
            self.graph = Graph()
            self.practice = _working_at(self.graph, "ddd", "tactics")
            _node(self.practice, "Aggregate", "orders")

        with description("with the LERN pattern applied"):
            with it("should fail naming the pattern whose schema requires the route"):
                self.graph.applied_patterns.apply(["lern_domain_driven"])
                expect(_gaps(self.practice)).to(contain(
                    "Aggregate 'orders' has no route relationship to Route, which the lern_domain_driven pattern schema requires."
                ))

        with description("with no pattern applied"):
            with it("should not require a route"):
                expect([gap for gap in _gaps(self.practice) if "route" in gap]).to(equal([]))
