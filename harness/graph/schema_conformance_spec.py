"""Content conforms to its schema: every node has each relationship its schema type requires, up to the fidelity its
practice works at, by its practice's schema and the schemas of the patterns its graph applies."""

from expects import be_empty, contain, equal, expect
from mamba import before, description, it

from harness.graph.graph import Graph, Source
from harness.graph.rule_context import RuleCheckContext
from harness.graph.schema_conformance import ConformsToSchema
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays


def _working_at(graph: Graph, key: str, fidelity: str):
    """The graph's practice called key, working at fidelity, as a session sets it."""
    practice = graph.practice(key)
    practice.fidelities.current = practice.fidelities.entries[fidelity]
    return practice


def _node(practice, type: str, name: str):
    return practice.reading.in_graph.add_named(type, f"{practice.key}:{type}:{name}", name, Source(f"{name}.py", 1, 1))


def _gaps(practice) -> list[str]:
    """Each gap the rule finds in practice, as it records them."""
    return [message for _, message in ConformsToSchema().check_practice(RuleCheckContext(practice, None))]


with description("conforms to schema"):
    with description("an operation of clean engineering worked at code"):
        with before.each:
            self.graph = Graph()
            self.practice = _working_at(self.graph, "clean_engineering", "code")
            self.cart = _node(self.practice, "OoadClass", "Cart")
            self.add = _node(self.practice, "Operation", "add")
            self.graph.link("participants", self.cart, self.add)

        with description("that has no parameters"):
            with it("should fail naming the missing relationship, its target, and the schema requiring it"):
                expect(_gaps(self.practice)).to(contain(
                    "Operation 'add' has no parameters relationship to Parameter, which the clean_engineering practice schema requires."
                ))

        with description("that holds its parameters, under the kind its practice records them, and the members it invokes"):
            with before.each:
                self.graph.link("hasParameter", self.add, _node(self.practice, "Parameter", "item"))
                self.graph.link("invokes", self.add, _node(self.practice, "Property", "items"), "relationship")
                self.graph.link("participants", self.cart, self.graph.node("clean_engineering:Property:items"))

            with it("should pass"):
                expect(_gaps(self.practice)).to(be_empty)

        with description("whose class names no base class"):
            with it("should not require the optional relationship"):
                expect([gap for gap in _gaps(self.practice) if "baseClass" in gap]).to(be_empty)

        with it("should be checked by every practice without its schema listing it"):
            expect(list(self.practice.reading.checks())).to(contain(ConformsToSchema.slug))

        with it("should be a rule of every node"):
            expect(self.add.rules.slugs).to(contain(ConformsToSchema.slug))

        with it("should record its gap on the node when the graph checks the practice"):
            self.practice.reading.in_graph.rule_run.check()
            recorded = [violation.message for violation in self.add.rules[ConformsToSchema.slug].violations]
            expect(recorded).to(contain(
                "Operation 'add' has no parameters relationship to Parameter, which the clean_engineering practice schema requires."
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
