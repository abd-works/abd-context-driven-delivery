"""Schema rules bind to nodes as a rules collection."""

from expects import be_a, contain, equal, expect
from mamba import before, description, it

from harness.graph.graph import Graph, Node, Source
from harness.graph.graph_rules_collection import GraphRulesCollection
from harness.graph.schema_rules import PracticeSchema


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
        expect(PracticeSchema.load("clean_engineering").slugs_for("Operation")).to(
            contain("limit-operation-parameters")
        )


with description("DDD schema extends clean engineering"):
    with it("should inherit OoadClass rules on Entity"):
        expect(PracticeSchema.load("ddd").slugs_for("Entity")).to(contain("keep-classes-single-responsibility"))

    with it("should inherit Module rules on BoundedContext"):
        expect(PracticeSchema.load("ddd").slugs_for("BoundedContext")).to(contain("named-seam-and-constraint"))

    with it("should resolve ce anchor for tactical class types"):
        expect(PracticeSchema.load("ddd").anchor_type("ValueObject")).to(equal("OoadClass"))
        expect(PracticeSchema.load("ddd").anchor_type("BoundedContext")).to(equal("Module"))

    with it("should not list flaccid-data-object on value objects"):
        slugs = PracticeSchema.load("ddd").slugs_for("ValueObject")
        expect("flaccid-data-object-no-behavior" in slugs).to(equal(False))


with description("LERN overlay rules"):
    with it("should give NodeRoot the tier rules when the overlay is active"):
        slugs = PracticeSchema.load("ddd", ("lern_domain_driven",)).slugs_for("NodeRoot")
        expect(slugs).to(contain("node-decides-next-page"))
        expect(slugs).to(contain("node-tier-uses-node-suffix"))

    with it("should prefix overlay-declared tier rules in qualified labels"):
        expect(
            PracticeSchema.load("ddd", ("lern_domain_driven",)).rule_label("NodeRoot", "node-decides-next-page")
        ).to(equal("lern.domain.driven.ddd.NodeRoot.node-decides-next-page"))


with description("a rule label"):
    with it("should name the practice, the node, and the rule"):
        expect(PracticeSchema.load("clean_engineering").rule_label("Operation", "limit-operation-parameters")).to(
            equal("clean_engineering.Operation.limit-operation-parameters")
        )

    with it("should prefix a pattern node"):
        expect(PracticeSchema.load("ddd", ("lern_domain_driven",)).rule_label("Route", "keep-classes-single-responsibility")).to(
            equal("lern.domain.driven.ddd.Route.keep-classes-single-responsibility")
        )
