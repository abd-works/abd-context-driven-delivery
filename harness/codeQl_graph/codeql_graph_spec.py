"""A CodeQL graph loaded from the account-credentials working copy."""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_above, contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, CodeQLNode

_ROOT = _HERE
_SAMPLE = _ROOT / "examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]
_QUERIES = _ROOT / "queries"


def child_names(node: CodeQLNode) -> list[str]:
    return [child.name for child in node.children]


def named(nodes: list[CodeQLNode], name: str) -> CodeQLNode:
    for node in nodes:
        if node.name == name:
            return node
    raise AssertionError(f"missing {name}")


def operation_named(nodes: list[CodeQLNode], name: str, parent_name: str) -> CodeQLNode:
    for node in nodes:
        if node.name == name and node.parent is not None and node.parent.name == parent_name:
            return node
    raise AssertionError(f"missing {name} on {parent_name}")


def holder(node: CodeQLNode, kind: str) -> CodeQLNode:
    for child in node.children:
        if child.name == kind:
            return child
    raise AssertionError(f"missing {kind}")


def find(root: CodeQLNode, name: str) -> CodeQLNode:
    queue = [root]
    seen: set[str] = set()
    while queue:
        node = queue.pop(0)
        if node.node_id in seen:
            continue
        seen.add(node.node_id)
        if node.name == name:
            return node
        queue.extend(node.children)
    raise AssertionError(f"missing {name}")


with description("a CodeQL graph"):
    with context("loaded from the account credentials working copy"):
        with before.all:
            self.graph = CodeQLGraph()
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            self.graph.load_working_copy(str(_ROOT), roots, database=str(_SAMPLE))

        with context("with clean engineering"):
            with before.all:
                self.clean = self.graph.practice("clean_engineering")
                self.account = find(self.clean.root_node, "AccountCredentials")

            with it("should count three modules"):
                expect(self.clean.node_count("Module")).to(equal(3))

            with it("should count fourteen classes"):
                expect(self.clean.node_count("OoadClass")).to(equal(14))

            with it("should include module, class, operation, property, and parameter nodes"):
                expect(
                    {"Module", "OoadClass", "Operation", "Property", "Parameter"} <= self.clean.node_types
                ).to(equal(True))

            with it("should order relative, owns, properties, belongsTo, hasParameter, hasType, invokes, and dependsOn"):
                expect(self.clean.edge_type_kinds).to(
                    equal(
                        [
                            "relative",
                            "owns",
                            "properties",
                            "demonstrates",
                            "belongsTo",
                            "hasParameter",
                            "hasType",
                            "demonstratedThrough",
                            "returns",
                            "invokes",
                            "dependsOn",
                        ]
                    )
                )

            with it("should own the account-credentials, customer, and onboarding modules"):
                expect(child_names(self.clean.root_node)).to(equal(["account-credentials", "customer", "onboarding"]))

            with it("should list token and customer first on AccountCredentials"):
                expect(child_names(self.account)[:2]).to(equal(["token", "customer"]))

            with it("should include register on AccountCredentials"):
                expect(child_names(self.account)).to(contain("register"))

            with it("should include properties on AccountCredentials"):
                expect(child_names(self.account)).to(contain("properties"))

            with it("should include belongsTo on AccountCredentials"):
                expect(child_names(self.account)).to(contain("belongsTo"))

            with context("with a module, a class, an operation, a property, and a parameter"):
                with before.all:
                    self.module = named(self.clean.nodes["Module"], "account-credentials")
                    self.class_node = named(self.clean.nodes["OoadClass"], "AccountCredentials")
                    self.operation = operation_named(self.clean.nodes["Operation"], "register", "AccountCredentials")
                    self.property = named(self.clean.nodes["Property"], "token")
                    self.parameter = named(self.clean.nodes["Parameter"], "validationCode")

                with it("should parent the module on the practice"):
                    expect(self.module.parent.name).to(equal("clean_engineering"))

                with it("should parent the class on its module"):
                    expect(self.class_node.parent.name).to(equal("account-credentials"))

                with it("should parent the operation on its class"):
                    expect(self.operation.parent.name).to(equal("AccountCredentials"))

                with it("should parent the property on its class"):
                    expect(self.property.parent.name).to(equal("AccountCredentials"))

                with it("should parent the parameter on its operation"):
                    expect(self.parameter.parent.type).to(equal("Operation"))

                with it("should run rule queries after the node and edge queries"):
                    expect(self.clean.loaded).to(equal(["nodes", "edges", "rules"]))

            with context("with the register operation"):
                with before.all:
                    self.register = operation_named(self.clean.nodes["Operation"], "register", "AccountCredentials")

                with it("should show the register body as Monaco text"):
                    expect(self.register.source.text.splitlines()[0].strip()).to(equal("async register(): Promise<void> {"))

                with it("should name the source file"):
                    expect(self.register.source.file).to(contain("account-credentials.ts"))

                with it("should start at the file line Monaco numbers from"):
                    expect(self.register.source.startLine).to(be_above(0))

                with it("should mark the emailValidationCode call"):
                    expect(self.register.source.text).to(contain("/* call:this.emailValidationCode */"))

                with it("should fold that call for Monaco"):
                    expect(any(fold.kind == "call" and fold.start == fold.end for fold in self.register.source.folds)).to(equal(True))

            with context("with the practice selected"):
                with before.all:
                    self.graph.filter.select_practices(["clean_engineering"])

                with it("should offer the class type named by the class query"):
                    expect(self.graph.filter.node_types).to(contain("OoadClass"))

                with it("should offer the module type named by the module query"):
                    expect(self.graph.filter.node_types).to(contain("Module"))

                with it("should return AccountCredentials"):
                    returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
                    expect(returned).to(contain("AccountCredentials"))

                with it("should return the account-credentials module"):
                    returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
                    expect(returned).to(contain("account-credentials"))

                with context("with operations selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["Operation"])

                    with it("should offer invokes for operations"):
                        expect(self.graph.filter.relationships).to(contain("invokes"))

                    with it("should offer the operation parameter rule"):
                        expect(self.graph.filter.rules).to(contain("limit-operation-parameters"))

                    with it("should leave the class dependency rule out of the rule filter"):
                        expect("use-explicit-dependencies" in self.graph.filter.rules).to(equal(False))

                    with it("should return the failure operation"):
                        returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
                        expect(returned).to(contain("failure"))

                    with it("should leave classes out of the operation results"):
                        returned = {node["type"] for node in json.loads(self.graph.return_nodes())}
                        expect("OoadClass" in returned).to(equal(False))

                with context("with violations of the parameter rule"):
                    with before.all:
                        self.graph.filter.select_rules(["limit-operation-parameters"])
                        self.graph.filter.select_violations()

                    with it("should return the operation that fails the rule"):
                        returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
                        expect(returned).to(contain("failure"))

                    with it("should leave the operation that passes the rule out"):
                        returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
                        expect("register" in returned).to(equal(False))

                with context("with classes selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["OoadClass"])

                    with it("should offer the class dependency rule"):
                        expect(self.graph.filter.rules).to(contain("use-explicit-dependencies"))

                    with it("should leave the operation parameter rule out of the rule filter"):
                        expect("limit-operation-parameters" in self.graph.filter.rules).to(equal(False))

                    with it("should leave invokes out of the class relationships"):
                        expect("invokes" in self.graph.filter.relationships).to(equal(False))

                    with it("should leave modules out of the class results"):
                        returned = {node["type"] for node in json.loads(self.graph.return_nodes())}
                        expect("Module" in returned).to(equal(False))

        with context("with stories"):
            with before.all:
                self.stories = self.graph.practice("stories")

            with it("should count one epic"):
                expect(self.stories.node_count("Epic")).to(equal(1))

            with it("should count three stories"):
                expect(self.stories.node_count("Story")).to(equal(3))

            with it("should include epic, story, scenario, background, step, and example nodes"):
                expect(
                    {"Epic", "Story", "Scenario", "Background", "Step", "Example"} <= self.stories.node_types
                ).to(equal(True))

            with it("should own Onboard A Customer"):
                expect(child_names(self.stories.root_node)).to(contain("Onboard A Customer"))

            with context("with an epic, a story, a scenario, a step, and an example"):
                with before.all:
                    self.epic = named(self.stories.nodes["Epic"], "Onboard A Customer")
                    self.story = self.stories.nodes["Story"][0]
                    self.scenario = self.stories.nodes["Scenario"][0]
                    self.step = self.stories.nodes["Step"][0]
                    self.example = self.stories.nodes["Example"][0]

                with it("should parent the epic on the practice"):
                    expect(self.epic.parent.name).to(equal("stories"))

                with it("should parent the story on its epic"):
                    expect(self.story.parent.type).to(equal("Epic"))

                with it("should parent the scenario on its story"):
                    expect(self.scenario.parent.type).to(equal("Story"))

                with it("should parent the step on its scenario"):
                    expect(self.step.parent.type).to(equal("Scenario"))

                with it("should parent the example on scopes"):
                    expect(self.example.parent.name).to(equal("scopes"))

                with it("should parent scopes on the step"):
                    expect(self.example.parent.parent.type).to(equal("Step"))

            with context("with a step that invokes an operation"):
                with before.all:
                    self.invoking_step = next(
                        step
                        for step in self.stories.nodes["Step"]
                        if any(child.name == "invokes" for child in step.children)
                    )
                    self.invoked = next(
                        child for child in holder(self.invoking_step, "invokes").children if child.type == "Operation"
                    )

                with it("should place that operation under the step"):
                    expect(self.invoked.practice.name).to(equal("clean_engineering"))

                with it("should place that step back under the operation"):
                    expect(child_names(holder(self.invoked, "invokes"))).to(contain(self.invoking_step.name))

            with context("with the practice selected"):
                with before.all:
                    self.graph.filter.select_practices(["stories"])

                with it("should offer the story type named by the story query"):
                    expect(self.graph.filter.node_types).to(contain("Story"))

                with it("should offer the epic type named by the epic query"):
                    expect(self.graph.filter.node_types).to(contain("Epic"))

                with it("should leave class node types out of the node filter"):
                    expect("OoadClass" in self.graph.filter.node_types).to(equal(False))

                with it("should return the epic"):
                    expect([node["name"] for node in json.loads(self.graph.return_nodes())]).to(contain("Onboard A Customer"))

                with it("should leave classes out of the results"):
                    expect("OoadClass" in {node["type"] for node in json.loads(self.graph.return_nodes())}).to(equal(False))

        with context("with domain-driven design"):
            with before.all:
                self.ddd = self.graph.practice("ddd")
                self.bounded_context = find(self.ddd.root_node, "bounded context")
                self.aggregate = find(self.bounded_context, "account-credentials")

            with it("should count one bounded context"):
                expect(self.ddd.node_count("BoundedContext")).to(equal(1))

            with it("should count two aggregates"):
                expect(self.ddd.node_count("Aggregate")).to(equal(2))

            with it("should count zero entities"):
                expect(self.ddd.node_count("Entity")).to(equal(0))

            with it("should count two entity roots"):
                expect(self.ddd.node_count("EntityRoot")).to(equal(2))

            with it("should count five value objects"):
                expect(self.ddd.node_count("ValueObject")).to(equal(5))

            with it("should count two repositories"):
                expect(self.ddd.node_count("Repository")).to(equal(2))

            with it("should order root, owns, belongsTo, accesses, and associates"):
                expect(self.ddd.edge_type_kinds).to(equal(["root", "owns", "belongsTo", "accesses", "associates"]))

            with it("should include only domain stereotypes"):
                expect(
                    self.ddd.node_types
                    <= {
                        "BoundedContext",
                        "Aggregate",
                        "Entity",
                        "EntityRoot",
                        "ValueObject",
                        "Repository",
                        "DomainService",
                        "DomainEvent",
                        "Specification",
                        "Factory",
                    }
                ).to(equal(True))

            with it("should own the bounded context"):
                expect(child_names(self.ddd.root_node)).to(equal(["bounded context"]))

            with it("should own account-credentials and customer under the bounded context"):
                expect(child_names(self.bounded_context)).to(equal(["account-credentials", "customer"]))

            with it("should include AccountCredentials"):
                expect(child_names(self.aggregate)).to(contain("AccountCredentials"))

            with it("should include ValidationCode"):
                expect(child_names(self.aggregate)).to(contain("ValidationCode"))

            with it("should include AccountToken"):
                expect(child_names(self.aggregate)).to(contain("AccountToken"))

            with it("should include AccountCredentialsRepository"):
                expect(child_names(self.aggregate)).to(contain("AccountCredentialsRepository"))

            with it("should type AccountCredentials as an entity root"):
                expect(find(self.aggregate, "AccountCredentials").type).to(equal("EntityRoot"))

            with context("with a bounded context, an aggregate, an entity root, a value object, and a repository"):
                with before.all:
                    self.bounded = self.ddd.nodes["BoundedContext"][0]
                    self.aggregate_node = named(self.ddd.nodes["Aggregate"], "account-credentials")
                    self.entity_root = named(self.ddd.nodes["EntityRoot"], "AccountCredentials")
                    self.value = self.ddd.nodes["ValueObject"][0]
                    self.repository = self.ddd.nodes["Repository"][0]

                with it("should parent the bounded context on the practice"):
                    expect(self.bounded.parent.name).to(equal("ddd"))

                with it("should parent the aggregate on its bounded context"):
                    expect(self.aggregate_node.parent.type).to(equal("BoundedContext"))

                with it("should parent the entity root on its aggregate"):
                    expect(self.entity_root.parent.name).to(equal("account-credentials"))

                with it("should parent the value object on its aggregate"):
                    expect(self.value.parent.type).to(equal("Aggregate"))

                with it("should parent the repository on its aggregate"):
                    expect(self.repository.parent.type).to(equal("Aggregate"))

            with context("with the practice selected"):
                with before.all:
                    self.graph.filter.select_practices(["ddd"])

                with it("should offer the aggregate type named by the aggregate query"):
                    expect(self.graph.filter.node_types).to(contain("Aggregate"))

                with it("should offer the entity root type named by the entity root query"):
                    expect(self.graph.filter.node_types).to(contain("EntityRoot"))

                with it("should leave story node types out of the node filter"):
                    expect("Story" in self.graph.filter.node_types).to(equal(False))

                with it("should return the bounded context"):
                    expect([node["name"] for node in json.loads(self.graph.return_nodes())]).to(contain("bounded context"))

                with it("should leave stories out of the results"):
                    expect("Story" in {node["type"] for node in json.loads(self.graph.return_nodes())}).to(equal(False))

                with context("with entity roots selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["EntityRoot"])

                    with it("should offer accesses for entity roots"):
                        expect(self.graph.filter.relationships).to(contain("accesses"))

                    with it("should leave owns out of the entity root relationships"):
                        expect("owns" in self.graph.filter.relationships).to(equal(False))

                    with it("should return AccountCredentials"):
                        expect([node["name"] for node in json.loads(self.graph.return_nodes())]).to(contain("AccountCredentials"))

                    with it("should leave aggregates out of the entity root results"):
                        expect("Aggregate" in {node["type"] for node in json.loads(self.graph.return_nodes())}).to(equal(False))

                with context("with aggregates selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["Aggregate"])

                    with it("should offer owns for aggregates"):
                        expect(self.graph.filter.relationships).to(contain("owns"))

                    with it("should leave accesses out of the aggregate relationships"):
                        expect("accesses" in self.graph.filter.relationships).to(equal(False))

                    with it("should return the account-credentials aggregate"):
                        expect([node["name"] for node in json.loads(self.graph.return_nodes())]).to(contain("account-credentials"))

                    with it("should leave entity roots out of the aggregate results"):
                        expect("EntityRoot" in {node["type"] for node in json.loads(self.graph.return_nodes())}).to(equal(False))

        with context("with behavior-driven development that has no specs"):
            with it("should count zero specs"):
                expect(self.graph.practice("bdd").node_count("Spec")).to(equal(0))

            with it("should have no edges"):
                expect(self.graph.practice("bdd").edge_count).to(equal(0))

            with it("should have no edge types"):
                expect(self.graph.practice("bdd").edge_type_kinds).to(equal([]))

            with context("with the practice selected"):
                with before.all:
                    self.graph.filter.select_practices(["bdd"])

                with it("should offer the spec type named by the spec query"):
                    expect(self.graph.filter.node_types).to(contain("Spec"))

                with it("should offer the description type named by the description query"):
                    expect(self.graph.filter.node_types).to(contain("Description"))

                with it("should leave class node types out of the node filter"):
                    expect("OoadClass" in self.graph.filter.node_types).to(equal(False))

                with it("should leave classes out of the results"):
                    expect("OoadClass" in {node["type"] for node in json.loads(self.graph.return_nodes())}).to(equal(False))

                with context("with specs selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["Spec"])

                    with it("should leave descriptions out of the node filter"):
                        expect("Description" in self.graph.filter.node_types).to(equal(False))

                    with it("should offer no relationships"):
                        expect(self.graph.filter.relationships).to(equal([]))

                    with it("should leave descriptions out of the results"):
                        expect("Description" in {node["type"] for node in json.loads(self.graph.return_nodes())}).to(equal(False))

        with context("with experience design that has no map"):
            with it("should count zero maps"):
                expect(self.graph.practice("ux").node_count("UxMap")).to(equal(0))

            with it("should have no edges"):
                expect(self.graph.practice("ux").edge_count).to(equal(0))

            with it("should have no edge types"):
                expect(self.graph.practice("ux").edge_type_kinds).to(equal([]))

        with context("with a typescript pack and a python pack"):
            with it("should load the typescript class query"):
                expect((_QUERIES / "typescript" / "clean_engineering" / "nodes" / "classes.ql").is_file()).to(equal(True))

            with it("should load the python class query"):
                expect((_QUERIES / "python" / "clean_engineering" / "nodes" / "classes.ql").is_file()).to(equal(True))
