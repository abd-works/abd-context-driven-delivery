"""Filter, stage, passing rules, and packages on a graph."""

from pathlib import Path

_HERE = Path(__file__).resolve().parent

from expects import contain, equal, expect
from harness.installation.data_class import data_of  # noqa: E402
from mamba import before, context, description, it

from harness.graph.edge import EdgeType
from harness.graph.graph import Graph, Node, Source
from harness.graph.saved_graph import SavedGraph, SavedPractice
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue


def _saved_node(node_id: str, name: str, type: str, file: str, end_line: int, stage: str) -> dict:
    return {"node_id": node_id, "name": name, "type": type, "practice": "clean_engineering", "file": file, "line": 1, "end_line": end_line, "stage": stage}


with description("a graph"):
    with context("with a failing operation and a passing operation"):
        with before.all:
            self.graph = Graph()
            self.graph.open(_HERE)
            self.practice = self.graph.practice("clean_engineering")
            self.failure = Node(
                self.practice, "Operation", "clean_engineering:Operation:failure.ts:failure:Account", "failure", Source(".", 1, 1)
            )
            self.failure.rules.record_violation("limit-operation-parameters", "too many")
            self.register = Node(
                self.practice, "Operation", "clean_engineering:Operation:register.ts:register:Account", "register", Source(".", 1, 1)
            )
            root = self.practice.in_graph.root
            root.children.extend([self.failure, self.register])
            self.graph.filter.select_rules(["limit-operation-parameters"])
            self.graph.filter.select_violations()

        with it("should list the failed rule on the failing operation"):
            expect(self.failure.failed_rules).to(equal(["limit-operation-parameters"]))

        with it("should list the rule that did not fail"):
            expect(self.register.passing_rules).to(contain("limit-operation-parameters"))

        with it("should leave the failed rule out of the passing rules"):
            expect("limit-operation-parameters" in self.failure.passing_rules).to(equal(False))

        with it("should return the operation that fails"):
            import json
            returned = [node["name"] for node in data_of(self.graph.return_nodes())]
            expect(returned).to(equal(["failure"]))

    with context("with a relationship selected"):
        with before.all:
            self.graph = Graph()
            self.graph.open(_HERE)
            self.practice = self.graph.practice("clean_engineering")
            self.module = Node(self.practice, "Module", "id:module", "account-credentials", Source(".", 1, 1))
            self.class_node = Node(self.practice, "OoadClass", "id:class", "AccountCredentials", Source(".", 1, 1))
            self.other = Node(self.practice, "OoadClass", "id:other", "Customer", Source(".", 1, 1))
            self.module.stage = "discovery"
            self.class_node.stage = "implementation"
            root = self.practice.in_graph.root
            root.children.extend([self.module, self.class_node, self.other])
            self.graph.record(EdgeType("owns", 2, "direct"), self.module, self.class_node)
            self.graph.filter.select_relationships(["owns"])

        with it("should keep the stage from the query on the node"):
            expect(self.class_node.stage).to(equal("implementation"))

        with it("should give the edge the child node's stage"):
            edge = self.practice.in_graph.edges("owns")[0]
            expect(edge.stage).to(equal("implementation"))

        with it("should return the nodes on the selected edge"):
            import json
            returned = {node["name"] for node in data_of(self.graph.return_nodes())}
            expect(returned).to(equal({"account-credentials", "AccountCredentials"}))

    with context("with a saved node that carries a stage"):
        with before.all:
            graph = Graph()
            saved = {"nodes": [_saved_node("id", "AccountCredentials", "OoadClass", "account.ts", 4, "implementation")]}
            graph.restored_from(SavedGraph([], {"clean_engineering": SavedPractice.from_record("clean_engineering", saved)}))
            self.node = graph.node("id")

        with it("should store the stage on the node"):
            expect(self.node.stage).to(equal("implementation"))

    with context("with a package between a module and a class"):
        with before.all:
            graph = Graph()
            root = graph.practice("clean_engineering").in_graph.root
            module, package = "clean_engineering:Module:src/domain:domain", "clean_engineering:Package:src/domain/customer:customer"
            customer = "clean_engineering:OoadClass:src/domain/customer/Customer.ts:Customer"
            saved = SavedPractice.from_record("clean_engineering", {
                "nodes": [
                    _saved_node(module, "domain", "Module", "src/domain", 1, "discovery"),
                    _saved_node(package, "customer", "Package", "src/domain/customer", 1, "discovery"),
                    _saved_node(customer, "Customer", "OoadClass", "src/domain/customer/Customer.ts", 3, "implementation"),
                ],
                "edges": [
                    {"parent": root.node_id, "child": module, "kind": "owns", "order": 1, "display": "direct"},
                    {"parent": module, "child": package, "kind": "owns", "order": 2, "display": "direct"},
                    {"parent": package, "child": customer, "kind": "owns", "order": 2, "display": "direct"},
                ],
            })
            graph.restored_from(SavedGraph([], {"clean_engineering": saved}))
            self.tree = data_of(graph.practice("clean_engineering").in_graph.root.serialize())

        with it("should parent the package on the module"):
            package = next(child for child in self.tree["children"][0]["children"] if child["name"] == "customer")
            expect(package["type"]).to(equal("Package"))

        with it("should parent the class on the package"):
            package = next(child for child in self.tree["children"][0]["children"] if child["name"] == "customer")
            expect([child["name"] for child in package["children"] if child["type"] != "rules"]).to(equal(["Customer"]))
