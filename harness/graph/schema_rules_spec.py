"""A practice schema gives each node type its rules as a rules collection."""

from expects import be, be_a, contain, equal, expect
from mamba import before, description, it

from harness.graph.graph import Graph, Node, Source
from harness.graph.graph_rules_collection import GraphRulesCollection
from harness.graph.pattern_overlays import PatternOverlays
from harness.graph.schema_rules import PracticeSchema
from harness.guidance.practice_catalogue import PracticeCatalogue
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays

# The overlay the LERN pattern owns, as a graph applying that pattern holds it.
_LERN = tuple(pattern.graph_overlay for pattern in PatternOverlays(["lern_domain_driven"]).patterns)


with description("schema rules on a node"):
    with before.each:
        self.graph = Graph()
        self.practice = self.graph.practice("clean_engineering")
        self.operation = Node(
            self.practice,
            "Operation",
            "clean_engineering:Operation:op",
            "save",
            Source(".", 1, 5),
        )

    with it("should attach a rules collection from schema.yaml"):
        expect(self.operation.rules).to(be_a(GraphRulesCollection))

    with it("should list limit-operation-parameters for an operation"):
        expect(self.operation.rules.slugs).to(contain("limit-operation-parameters"))

    with it("should expose a specific rule by slug"):
        rule = self.operation.rules["limit-operation-parameters"]
        expect(rule.slug).to(equal("limit-operation-parameters"))

    with it("should record violations on the collection and the rule"):
        self.operation.rules.record_violation("limit-operation-parameters", "too many parameters")
        expect(self.operation.failed_rules).to(equal(["limit-operation-parameters"]))
        expect([violation.message for violation in self.operation.rules["limit-operation-parameters"].violations]).to(
            contain("too many parameters")
        )

    with it("should say the rule is failing once it holds a violation"):
        self.operation.rules.record_violation("limit-operation-parameters", "too many parameters")
        expect(self.operation.rules["limit-operation-parameters"].is_failing).to(equal(True))

    with it("should place a recorded violation at the node's source"):
        self.operation.rules.record_violation("limit-operation-parameters", "too many parameters")
        hit = self.operation.rules["limit-operation-parameters"].violations[0]
        source = self.operation.source
        expect((hit.location, hit.line, hit.end_line)).to(equal((source.file, source.start_line, source.end_line)))

    with it("should list a recorded violation with its rule"):
        self.operation.rules.record_violation("limit-operation-parameters", "too many parameters")
        listed = [(violation.rule, violation.message) for violation in self.operation.rules.violations]
        expect(listed).to(contain(("limit-operation-parameters", "too many parameters")))

    with it("should hang slug, prose body, and executable flag on each node rule"):
        rule = self.operation.rules["limit-operation-parameters"]
        expect(rule.slug).to(equal("limit-operation-parameters"))
        expect(rule.body).not_to(equal(""))
        expect(rule.executable).to(equal(True))

    with it("should attach prose-only rules without an executable check"):
        prose = self.operation.rules["write-invariants"]
        expect(prose.executable).to(equal(False))
        expect(prose.body).not_to(equal(""))

    with it("should give an operation its schema's rules"):
        expect(PracticeSchema(PracticeCatalogue.create("clean_engineering")).slugs_for("Operation")).to(
            contain("limit-operation-parameters")
        )


with description("DDD schema extends clean engineering"):
    with it("should inherit OoadClass rules on Entity"):
        expect(PracticeSchema(PracticeCatalogue.create("ddd")).slugs_for("Entity")).to(contain("keep-classes-single-responsibility"))

    with it("should inherit Module rules on BoundedContext"):
        expect(PracticeSchema(PracticeCatalogue.create("ddd")).slugs_for("BoundedContext")).to(contain("named-seam-and-constraint"))

    with it("should resolve ce anchor for tactical class types"):
        expect(PracticeSchema(PracticeCatalogue.create("ddd")).anchor_type("ValueObject")).to(equal("OoadClass"))
        expect(PracticeSchema(PracticeCatalogue.create("ddd")).anchor_type("BoundedContext")).to(equal("Module"))

    with it("should not list flaccid-data-object on value objects"):
        slugs = PracticeSchema(PracticeCatalogue.create("ddd")).slugs_for("ValueObject")
        expect("flaccid-data-object-no-behavior" in slugs).to(equal(False))


with description("LERN overlay rules"):
    with it("should give NodeRoot the tier rules when the overlay is active"):
        slugs = PracticeSchema(PracticeCatalogue.create("ddd"), _LERN).slugs_for("NodeRoot")
        expect(slugs).to(contain("node-decides-next-page"))
        expect(slugs).to(contain("node-tier-uses-node-suffix"))

    with it("should prefix overlay-declared tier rules in qualified labels"):
        expect(
            PracticeSchema(PracticeCatalogue.create("ddd"), _LERN).rule_label("NodeRoot", "node-decides-next-page")
        ).to(equal("lern.domain.driven.ddd.NodeRoot.node-decides-next-page"))


with description("a rule label"):
    with it("should name the practice, the node, and the rule"):
        expect(PracticeSchema(PracticeCatalogue.create("clean_engineering")).rule_label("Operation", "limit-operation-parameters")).to(
            equal("clean_engineering.Operation.limit-operation-parameters")
        )

    with it("should prefix a pattern node"):
        expect(PracticeSchema(PracticeCatalogue.create("ddd"), _LERN).rule_label("Route", "keep-classes-single-responsibility")).to(
            equal("lern.domain.driven.ddd.Route.keep-classes-single-responsibility")
        )


with description("a practice's schema in a graph"):
    with before.all:
        self.graph = Graph()
        self.practice = self.graph.practice("ddd")
        self.own_storage = set(vars(self.practice))
        self.schema = self.practice.in_graph.schema

    with it("should be made once, by the practice's part of the graph"):
        expect(self.practice.in_graph.schema).to(be(self.schema))

    with it("should leave the practice's own storage to the practice"):
        expect(set(vars(self.practice)) - self.own_storage).to(equal(set()))

    with it("should read the extended practice's schema from that practice's part of the same graph"):
        clean = self.graph.practice("clean_engineering")
        expect(self.schema.anchor_type("ValueObject")).to(equal("OoadClass"))
        expect(clean.in_graph.schema_with(())).to(be(clean.in_graph.schema))
