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
from harness.graph.schema_rules import slugs_for_type


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

    with it("should match slugs_for_type for operations"):
        expect(slugs_for_type("clean_engineering", "Operation")).to(
            contain("limit-operation-parameters")
        )
