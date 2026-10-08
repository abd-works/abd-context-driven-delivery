"""Rules attach to the node they check, and a violation filter keeps those hits on the graph."""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_above, contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, CodeQLNode, RuleResult, Source


def rule_on(node: dict, slug: str) -> dict:
    for child in node.get("children") or []:
        if child.get("name") != "rules":
            continue
        for rule in child.get("children") or []:
            if rule.get("name") == slug:
                return rule
    raise AssertionError(f"missing {slug}")


with description("rule categories"):
    with context("on an operation and a class"):
        with before.each:
            self.graph = CodeQLGraph()
            self.graph._practice_roots = {"clean_engineering": Path(".")}
            self.practice = self.graph.practice("clean_engineering")
            self.practice.graph = self.graph
            self.practice.bind_rule("limit-operation-parameters", ["Operation"])
            self.practice.bind_rule("use-explicit-dependencies", ["OoadClass"])
            self.failure = CodeQLNode(self.practice, "Operation", "clean_engineering:Operation:failure", "failure", Source(".", 1, 2))
            self.register = CodeQLNode(self.practice, "Operation", "clean_engineering:Operation:register", "register", Source(".", 3, 4))
            self.account = CodeQLNode(self.practice, "OoadClass", "clean_engineering:OoadClass:AccountCredentials", "AccountCredentials", Source(".", 1, 8))
            self.failure.rules.append(RuleResult("limit-operation-parameters", "Operation 'failure' takes more than two parameters."))
            self.practice.root_node.children = [self.failure, self.register, self.account]
            for node in (self.failure, self.register, self.account):
                node.parent = self.practice.root_node

        with it("should attach the parameter rule to the operation that fails it"):
            rule = rule_on(self.failure.serialize(), "limit-operation-parameters")
            expect(rule["status"]).to(equal("violating"))
            expect(rule["violation"]).to(contain("takes more than two parameters"))

        with it("should attach the parameter rule to the operation that passes it"):
            expect(rule_on(self.register.serialize(), "limit-operation-parameters")["status"]).to(equal("passing"))

        with it("should leave the class rule off an operation"):
            category = next(child for child in self.failure.serialize()["children"] if child["name"] == "rules")
            names = [child["name"] for child in category["children"]]
            expect("use-explicit-dependencies" in names).to(equal(False))

        with it("should attach the class rule to the class"):
            rule = rule_on(self.account.serialize(), "use-explicit-dependencies")
            expect(rule["status"]).to(equal("passing"))

        with it("should leave the parameter rule off the class"):
            category = next(child for child in self.account.serialize()["children"] if child["name"] == "rules")
            names = [child["name"] for child in category["children"]]
            expect("limit-operation-parameters" in names).to(equal(False))

        with context("with violations of the parameter rule"):
            with before.each:
                self.graph.filter.select_rules(["limit-operation-parameters"])
                self.graph.filter.select_violations()

            with it("should attach the violation on the serialized operation"):
                rule = rule_on(self.failure.serialize(), "limit-operation-parameters")
                expect(rule["status"]).to(equal("violating"))
                expect(len(rule["violation"])).to(be_above(0))

            with it("should leave the passing rule off the serialized operation"):
                names = [child["name"] for child in self.register.serialize()["children"]]
                expect("rules" in names).to(equal(False))

            with it("should attach that violation on the nodes the filter returns"):
                self.practice.by_id[self.failure.node_id] = self.failure
                self.practice.by_id[self.register.node_id] = self.register
                self.practice.nodes["Operation"] = [self.failure, self.register]
                returned = json.loads(self.graph.return_nodes())
                failure = next(node for node in returned if node["name"] == "failure")
                expect([rule["status"] for rule in failure["rules"]]).to(equal(["violating"]))
                expect("register" in [node["name"] for node in returned]).to(equal(False))
