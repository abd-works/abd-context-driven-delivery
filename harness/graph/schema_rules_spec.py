"""Schema rules bind to nodes as a rules collection."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import be_a, contain, equal, expect
from mamba import before, description, it

from graph import Graph, Node, Source
from harness.graph.graph_rules_collection import GraphRulesCollection
from harness.graph.schema_rules import qualified_rule_label, slugs_for_type


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
        expect(self.operation.rules.slugs()).to(contain("limit-operation-parameters"))

    with it("should expose a specific rule by slug"):
        rule = self.operation.rules["limit-operation-parameters"]
        expect(rule.slug).to(equal("limit-operation-parameters"))

    with it("should record violations on the collection and the rule"):
        self.operation.rules.record_violation("limit-operation-parameters", "too many parameters")
        expect(self.operation.failed_rules).to(equal(["limit-operation-parameters"]))
        expect(self.operation.rules["limit-operation-parameters"].violations).to(
            contain("too many parameters")
        )

    with it("should hang slug, prose body, and executable flag on each node rule"):
        rule = self.operation.rules["limit-operation-parameters"]
        expect(rule.slug).to(equal("limit-operation-parameters"))
        expect(rule.body).not_to(equal(""))
        expect(rule.executable).to(equal(True))

    with it("should attach prose-only rules without an executable check"):
        prose = self.operation.rules["write-invariants"]
        expect(prose.executable).to(equal(False))
        expect(prose.body).not_to(equal(""))

    with it("should match slugs_for_type for operations"):
        expect(slugs_for_type("clean_engineering", "Operation")).to(
            contain("limit-operation-parameters")
        )


with description("DDD schema extends clean engineering"):
    with it("should inherit OoadClass rules on Entity"):
        expect(slugs_for_type("ddd", "Entity")).to(contain("keep-classes-single-responsibility"))

    with it("should inherit Module rules on BoundedContext"):
        expect(slugs_for_type("ddd", "BoundedContext")).to(contain("named-seam-and-constraint"))

    with it("should resolve ce anchor for tactical class types"):
        from harness.graph.schema_rules import ce_anchor_type

        expect(ce_anchor_type("ddd", "ValueObject")).to(equal("OoadClass"))
        expect(ce_anchor_type("ddd", "BoundedContext")).to(equal("Module"))

    with it("should not list flaccid-data-object on value objects"):
        slugs = slugs_for_type("ddd", "ValueObject")
        expect("flaccid-data-object-no-behavior" in slugs).to(equal(False))


with description("LERN overlay rules"):
    with it("should bind tier rules on NodeRoot when the overlay is active"):
        slugs = slugs_for_type("ddd", "NodeRoot", ("lern_domain_driven",))
        expect(slugs).to(contain("node-decides-next-page"))
        expect(slugs).to(contain("node-tier-uses-node-suffix"))

    with it("should prefix overlay-declared tier rules in qualified labels"):
        expect(
            qualified_rule_label("ddd", "NodeRoot", "node-decides-next-page", ("lern_domain_driven",))
        ).to(equal("lern.domain.driven.ddd.NodeRoot.node-decides-next-page"))


with description("a rule label"):
    with it("should name the practice, the node, and the rule"):
        expect(qualified_rule_label("clean_engineering", "Operation", "limit-operation-parameters")).to(
            equal("clean_engineering.Operation.limit-operation-parameters")
        )

    with it("should prefix a pattern node"):
        expect(qualified_rule_label("ddd", "Route", "keep-classes-single-responsibility", ("lern_domain_driven",))).to(
            equal("lern.domain.driven.ddd.Route.keep-classes-single-responsibility")
        )
