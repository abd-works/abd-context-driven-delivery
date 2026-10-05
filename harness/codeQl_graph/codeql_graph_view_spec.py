"""Filter, stage, passing rules, packages, and source folds on a CodeQL graph."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_above, contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, CodeQLNode, CodeQLPracticeGraph, RuleResult, Source

_FOLDS = _HERE / "examples" / "folds"


def operation(practice: CodeQLPracticeGraph, name: str, owner: str, text: str, folder: Path) -> CodeQLNode:
    path = folder / f"{name}.ts"
    path.write_text(text, encoding="utf-8")
    node = CodeQLNode(practice, "Operation", f"clean_engineering:Operation:{path.name}:{name}:{owner}", name, Source(path.name, 1, len(text.splitlines()), str(folder)))
    practice.by_id[node.node_id] = node
    practice.nodes.setdefault("Operation", []).append(node)
    return node


with description("a CodeQL graph"):
    with context("with a failing operation and a passing operation"):
        with before.all:
            self.graph = CodeQLGraph()
            self.graph._practice_roots["clean_engineering"] = _HERE
            self.practice = self.graph.practice("clean_engineering")
            self.failure = CodeQLNode(
                self.practice, "Operation", "clean_engineering:Operation:failure.ts:failure:Account", "failure", Source(".", 1, 1)
            )
            self.failure.rules.append(RuleResult("limit-operation-parameters", "too many"))
            self.register = CodeQLNode(
                self.practice, "Operation", "clean_engineering:Operation:register.ts:register:Account", "register", Source(".", 1, 1)
            )
            root = self.practice.root_node
            root.children.extend([self.failure, self.register])
            self.practice.bind_rule("limit-operation-parameters", ["Operation"])
            self.practice.bind_rule("keep-operations-small-focused", ["Operation"])
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
            returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
            expect(returned).to(equal(["failure"]))

    with context("with a relationship selected"):
        with before.all:
            self.graph = CodeQLGraph()
            self.graph._practice_roots["clean_engineering"] = _HERE
            self.practice = self.graph.practice("clean_engineering")
            self.module = CodeQLNode(self.practice, "Module", "id:module", "account-credentials", Source(".", 1, 1))
            self.class_node = CodeQLNode(self.practice, "OoadClass", "id:class", "AccountCredentials", Source(".", 1, 1))
            self.other = CodeQLNode(self.practice, "OoadClass", "id:other", "Customer", Source(".", 1, 1))
            self.module.stage = "discovery"
            self.class_node.stage = "implementation"
            root = self.practice.root_node
            root.children.extend([self.module, self.class_node, self.other])
            self.practice.record(
                {"kind": "owns", "order": 2, "display": "direct"},
                self.module,
                self.class_node,
            )
            self.graph.filter.select_relationships(["owns"])

        with it("should keep the stage from the query on the node"):
            expect(self.class_node.stage).to(equal("implementation"))

        with it("should give the edge the child node's stage"):
            edge = self.practice.edges["owns"][0]
            expect(edge.stage).to(equal("implementation"))

        with it("should return the nodes on the selected edge"):
            import json
            returned = {node["name"] for node in json.loads(self.graph.return_nodes())}
            expect(returned).to(equal({"account-credentials", "AccountCredentials"}))

    with context("with a query row that carries a stage"):
        with before.all:
            self.practice = CodeQLPracticeGraph("clean_engineering")
            self.node = CodeQLNode.from_fact(
                self.practice,
                CodeQLNode.fact(["id", "AccountCredentials", "OoadClass", "clean_engineering", "account.ts", "1", "4", "implementation"]),
            )

        with it("should store the stage on the node"):
            expect(self.node.stage).to(equal("implementation"))

    with context("with a package between a module and a class"):
        with before.all:
            self.practice = CodeQLPracticeGraph("clean_engineering")
            self.practice.by_id[self.practice.root_node.node_id] = self.practice.root_node
            self.practice.apply_nodes([
                ["clean_engineering:Module:src/domain:domain", "domain", "Module", "clean_engineering", "src/domain", "1", "1", "discovery"],
                ["clean_engineering:Package:src/domain/customer:customer", "customer", "Package", "clean_engineering", "src/domain/customer", "1", "1", "discovery"],
                ["clean_engineering:OoadClass:src/domain/customer/Customer.ts:Customer", "Customer", "OoadClass", "clean_engineering", "src/domain/customer/Customer.ts", "1", "3", "implementation"],
            ])
            self.practice.apply_edges([
                [self.practice.root_node.node_id, "clean_engineering:Module:src/domain:domain", "owns", "1", "direct"],
                ["clean_engineering:Module:src/domain:domain", "clean_engineering:Package:src/domain/customer:customer", "owns", "2", "direct"],
                ["clean_engineering:Package:src/domain/customer:customer", "clean_engineering:OoadClass:src/domain/customer/Customer.ts:Customer", "owns", "2", "direct"],
            ])
            self.practice.root_node.populate()

        with it("should parent the package on the module"):
            package = next(child for child in self.practice.nodes["Module"][0].children if child.name == "customer")
            expect(package.type).to(equal("Package"))

        with it("should parent the class on the package"):
            package = self.practice.nodes["Package"][0]
            expect([child.name for child in package.children]).to(equal(["Customer"]))

    with context("with source that opens a block and calls an operation"):
        with before.all:
            _FOLDS.mkdir(parents=True, exist_ok=True)
            self.practice = CodeQLPracticeGraph("clean_engineering")
            self.callee = operation(
                self.practice,
                "emailValidationCode",
                "AccountCredentials",
                "emailValidationCode(): void {\n  const code = new ValidationCode()\n}\n",
                _FOLDS,
            )
            self.class_node = CodeQLNode(
                self.practice,
                "OoadClass",
                "clean_engineering:OoadClass:ValidationCode.ts:ValidationCode",
                "ValidationCode",
                Source("ValidationCode.ts", 1, 3, str(_FOLDS)),
            )
            (_FOLDS / "ValidationCode.ts").write_text("class ValidationCode {\n  value: string\n}\n", encoding="utf-8")
            self.caller = operation(
                self.practice,
                "register",
                "AccountCredentials",
                "async register(): Promise<void> {\n  this.emailValidationCode()\n}\n",
                _FOLDS,
            )
            self.caller.source.expand([self.callee, self.class_node])

        with it("should fold the block around the call"):
            blocks = [fold for fold in self.caller.source.folds if fold.kind == "block" and fold.end > fold.start]
            expect(len(blocks)).to(be_above(0))

        with it("should fold the inlined operation past the call line"):
            calls = [fold for fold in self.caller.source.folds if fold.kind == "call" and fold.end > fold.start]
            expect(len(calls)).to(be_above(0))

        with it("should fold the class named in the inlined operation"):
            classes = [fold for fold in self.caller.source.folds if fold.kind == "class" and fold.end > fold.start]
            expect(len(classes)).to(be_above(0))
