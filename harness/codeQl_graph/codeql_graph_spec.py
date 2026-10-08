"""A CodeQL graph loaded from the account-credentials working copy."""

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_above, contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, CodeQLNode, CodeQLPracticeGraph, Source, query_pack

_ROOT = _HERE
_SAMPLE = _ROOT / "examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]


def walk_tree(node: dict):
    yield node
    for child in node.get("children") or []:
        yield from walk_tree(child)


def tree_names(node: dict) -> list[str]:
    return [child.get("name") for child in node.get("children") or []]


def tree_count(node: dict, type: str) -> int:
    """Distinct nodes of this type written by serialize. A relationship copy shares the home id."""
    return len({item.get("node_id") for item in walk_tree(node) if item.get("type") == type and item.get("type") != item.get("name")})


def owned_types(node: dict, practice: str) -> set[str]:
    """Types of this practice's nodes in the serialized tree. Holders are named for their kind."""
    return {
        item.get("type")
        for item in walk_tree(node)
        if item.get("type") not in {None, "Practice"}
        and item.get("type") != item.get("name")
        and str(item.get("node_id") or "").startswith(f"{practice}:")
    }


def tree_child(node: dict, name: str) -> dict:
    for child in node.get("children") or []:
        if child.get("name") == name:
            return child
    raise AssertionError(f"missing {name}")


def tree_named(node: dict, name: str, type: str) -> dict:
    """The serialized copy that keeps its children. A later relationship copy is empty."""
    matches = [item for item in walk_tree(node) if item.get("name") == name and item.get("type") == type]
    if not matches:
        raise AssertionError(f"missing {type} {name}")
    for item in matches:
        if item.get("children"):
            return item
    return matches[0]


def tree_with(node: dict, type: str, child_name: str) -> dict:
    for item in walk_tree(node):
        if item.get("type") == type and any(child.get("name") == child_name for child in item.get("children") or []):
            return item
    raise AssertionError(f"no {type} with {child_name}")


def tree_by_id(node: dict, node_id: str) -> dict:
    for item in walk_tree(node):
        if item.get("node_id") == node_id and item.get("children"):
            return item
    raise AssertionError(f"missing {node_id}")


def direct_child(node: dict, parent_type: str, child_type: str) -> dict:
    for item in walk_tree(node):
        if item.get("type") != parent_type:
            continue
        for child in item.get("children") or []:
            if child.get("type") == child_type:
                return child
    raise AssertionError(f"no {child_type} under {parent_type}")


def rule_on(node: dict, slug: str) -> dict:
    return tree_child(tree_child(node, "rules"), slug)


def typed_child(node: dict, holder: str, type: str) -> dict:
    for child in tree_child(node, holder).get("children") or []:
        if child.get("type") == type:
            return child
    raise AssertionError(f"missing {type} under {holder}")


with description("a CodeQL graph"):
    with context("loaded from the account credentials working copy"):
        with before.all:
            self.graph = CodeQLGraph()
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            self.graph.load_working_copy(str(_ROOT), roots, database=str(_SAMPLE))

        with context("with clean engineering"):
            with before.all:
                self.clean = self.graph.practice("clean_engineering")
                self.clean_tree = self.clean.root_node.serialize()
                self.account = tree_named(self.clean_tree, "AccountCredentials", "OoadClass")

            with it("should count three modules"):
                expect(tree_count(self.clean_tree, "Module")).to(equal(3))

            with it("should count fourteen classes"):
                expect(tree_count(self.clean_tree, "OoadClass")).to(equal(14))

            with it("should include module, class, operation, property, and parameter nodes"):
                expect(
                    {"Module", "OoadClass", "Operation", "Property", "Parameter"} <= owned_types(self.clean_tree, "clean_engineering")
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
                            "retrievedUsing",
                            "invokes",
                            "dependsOn",
                        ]
                    )
                )

            with it("should own the account-credentials, customer, and onboarding modules"):
                expect(tree_names(self.clean_tree)).to(equal(["account-credentials", "customer", "onboarding"]))

            with it("should identify the customer module by its source path and keep its classes"):
                module = tree_named(self.clean_tree, "customer", "Module")
                expect(module["node_id"]).to(equal("clean_engineering:Module:src/customer"))
                expect(
                    {"Address", "Customer", "CustomerException", "CustomerRepository", "Identity"} <= set(tree_names(module))
                ).to(equal(True))

            with it("should leave a belongsTo copy of the customer module without its classes"):
                copies = [
                    item
                    for item in walk_tree(self.clean_tree)
                    if item.get("node_id") == "clean_engineering:Module:src/customer" and not item.get("children")
                ]
                expect(len(copies)).to(be_above(0))

            with it("should list token and customer first on AccountCredentials"):
                expect(tree_names(self.account)[:2]).to(equal(["token", "customer"]))

            with it("should include register on AccountCredentials"):
                expect(tree_names(self.account)).to(contain("register"))

            with it("should include properties on AccountCredentials"):
                expect(tree_names(self.account)).to(contain("properties"))

            with it("should include belongsTo on AccountCredentials"):
                expect(tree_names(self.account)).to(contain("belongsTo"))

            with context("with a module, a class, an operation, a property, and a parameter"):
                with before.all:
                    self.module = tree_named(self.clean_tree, "account-credentials", "Module")
                    self.class_node = tree_named(self.clean_tree, "AccountCredentials", "OoadClass")
                    self.operation = tree_child(self.class_node, "register")
                    self.property = tree_child(self.class_node, "token")

                with it("should parent the module on the practice"):
                    expect(tree_child(self.clean_tree, "account-credentials")["node_id"]).to(equal(self.module["node_id"]))

                with it("should parent the class on its module"):
                    expect(tree_child(self.module, "AccountCredentials")["type"]).to(equal("OoadClass"))

                with it("should parent the operation on its class"):
                    expect(self.operation["type"]).to(equal("Operation"))

                with it("should parent the property on its class"):
                    expect(self.property["type"]).to(equal("Property"))

                with it("should parent the parameter on its operation through hasParameter"):
                    parameter = None
                    for item in walk_tree(self.clean_tree):
                        if item.get("type") != "Operation":
                            continue
                        for holder in item.get("children") or []:
                            if holder.get("name") != "hasParameter":
                                continue
                            for child in holder.get("children") or []:
                                if child.get("name") == "validationCode":
                                    parameter = child
                    expect(parameter["type"]).to(equal("Parameter"))

                with it("should run rule queries after the node and edge queries"):
                    expect(self.clean.loaded).to(equal(["nodes", "edges", "rules"]))

            with context("with the register operation"):
                with before.all:
                    self.register = self.clean.by_id[tree_child(self.account, "register")["node_id"]]

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

                    with it("should attach the parameter rule to the operation that fails it"):
                        failure = tree_named(self.clean_tree, "failure", "Operation")
                        rule = rule_on(failure, "limit-operation-parameters")
                        expect(rule["status"]).to(equal("violating"))
                        expect(len(rule["violation"])).to(be_above(0))

                    with it("should attach the parameter rule to the operation that passes it"):
                        register = tree_named(self.clean_tree, "register", "Operation")
                        expect(rule_on(register, "limit-operation-parameters")["status"]).to(equal("passing"))

                    with it("should leave the class dependency rule off an operation"):
                        failure = tree_named(self.clean_tree, "failure", "Operation")
                        attached = [child["name"] for child in tree_child(failure, "rules")["children"]]
                        expect("use-explicit-dependencies" in attached).to(equal(False))

                with context("with violations of the parameter rule"):
                    with before.all:
                        self.graph.filter.select_rules(["limit-operation-parameters"])
                        self.graph.filter.select_violations()
                        self.violation_tree = self.graph.practice("clean_engineering").root_node.serialize()

                    with it("should return the operation that fails the rule"):
                        returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
                        expect(returned).to(contain("failure"))

                    with it("should leave the operation that passes the rule out"):
                        returned = [node["name"] for node in json.loads(self.graph.return_nodes())]
                        expect("register" in returned).to(equal(False))

                    with it("should attach the violation on the returned operation"):
                        returned = json.loads(self.graph.return_nodes())
                        failure = next(node for node in returned if node["name"] == "failure")
                        attached = [rule for rule in failure["rules"] if rule["name"] == "limit-operation-parameters"]
                        expect(len(attached)).to(equal(1))
                        expect(attached[0]["status"]).to(equal("violating"))
                        expect(len(attached[0]["violation"])).to(be_above(0))

                    with it("should attach that violation on the serialized graph"):
                        failure = tree_named(self.violation_tree, "failure", "Operation")
                        rule = rule_on(failure, "limit-operation-parameters")
                        expect(rule["status"]).to(equal("violating"))
                        expect(len(rule["violation"])).to(be_above(0))

                    with it("should leave the passing rule off the serialized graph"):
                        register = tree_named(self.violation_tree, "register", "Operation")
                        attached = [
                            rule["name"]
                            for child in register.get("children") or []
                            if child.get("name") == "rules"
                            for rule in child.get("children") or []
                        ]
                        expect("limit-operation-parameters" in attached).to(equal(False))

                with context("with classes selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["OoadClass"])

                    with it("should offer the class dependency rule"):
                        expect(self.graph.filter.rules).to(contain("use-explicit-dependencies"))

                    with it("should attach the class dependency rule to the class"):
                        rule = rule_on(self.account, "use-explicit-dependencies")
                        expect(rule["type"]).to(equal("Rule"))
                        expect(rule["status"] in {"passing", "violating"}).to(equal(True))

                    with it("should leave the operation parameter rule off the class"):
                        attached = [child["name"] for child in tree_child(self.account, "rules")["children"]]
                        expect("limit-operation-parameters" in attached).to(equal(False))

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
                self.stories_tree = self.stories.root_node.serialize()
                self.clean_tree = self.graph.practice("clean_engineering").root_node.serialize()

            with it("should count one epic"):
                expect(tree_count(self.stories_tree, "Epic")).to(equal(1))

            with it("should count three stories"):
                expect(tree_count(self.stories_tree, "Story")).to(equal(3))

            with it("should include epic, sub-epic, story, scenario, background, step, and example nodes"):
                expect(
                    {"Epic", "SubEpic", "Story", "Scenario", "Background", "Step", "Example"}
                    <= owned_types(self.stories_tree, "stories")
                ).to(equal(True))

            with it("should own Onboard A Customer"):
                expect(tree_names(self.stories_tree)).to(contain("Onboard A Customer"))

            with context("with an epic, a sub-epic, a story, a scenario, a step, and an example"):
                with it("should parent the epic on the practice"):
                    expect(tree_child(self.stories_tree, "Onboard A Customer")["type"]).to(equal("Epic"))

                with it("should parent the sub-epic on its epic"):
                    epic = tree_child(self.stories_tree, "Onboard A Customer")
                    expect(tree_child(epic, "Authenticate User")["type"]).to(equal("SubEpic"))

                with it("should parent the story on its sub-epic"):
                    expect(direct_child(self.stories_tree, "SubEpic", "Story")["type"]).to(equal("Story"))

                with it("should parent the scenario on its story"):
                    expect(direct_child(self.stories_tree, "Story", "Scenario")["type"]).to(equal("Scenario"))

                with it("should parent the step on its scenario"):
                    expect(direct_child(self.stories_tree, "Scenario", "Step")["type"]).to(equal("Step"))

                with it("should list Create account steps in source order"):
                    steps = [
                        child["name"]
                        for child in tree_named(self.stories_tree, "Create account", "Scenario")["children"]
                        if child["type"] == "Step"
                    ]
                    expect(steps).to(
                        equal(
                            [
                                "when the User creates their account",
                                "then the account is unconfirmed and a validation code is emailed",
                            ]
                        )
                    )

                with it("should leave scopes out of the serialized graph"):
                    expect("scopes" in json.dumps(self.stories_tree)).to(equal(False))

            with context("with a step that invokes an operation"):
                with before.all:
                    self.invoking_step = tree_with(self.stories_tree, "Step", "invokes")
                    self.invoked = typed_child(self.invoking_step, "invokes", "Operation")

                with it("should place that operation under the step"):
                    expect(self.invoked["type"]).to(equal("Operation"))
                    expect(str(self.invoked["node_id"]).startswith("clean_engineering:")).to(equal(True))

                with it("should place that step back under the operation"):
                    operation = tree_by_id(self.clean_tree, self.invoked["node_id"])
                    expect(tree_names(tree_child(operation, "invokes"))).to(contain(self.invoking_step["name"]))

            with context("with a then step that observes an example"):
                with before.all:
                    self.observing_step = tree_with(self.stories_tree, "Step", "observes")
                    self.observed = typed_child(self.observing_step, "observes", "Example")

                with it("should place that example under observes"):
                    expect(self.observed["type"]).to(equal("Example"))

                with it("should parent observes on the step"):
                    expect(tree_child(self.observing_step, "observes")["name"]).to(equal("observes"))

            with context("with an example that demonstrates a class"):
                with before.all:
                    self.demonstrating = tree_with(self.stories_tree, "Example", "demonstrates")
                    self.demonstrated = typed_child(self.demonstrating, "demonstrates", "OoadClass")

                with it("should place that class under demonstrates"):
                    expect(str(self.demonstrated["node_id"]).startswith("clean_engineering:OoadClass:")).to(equal(True))

                with it("should place that example back on the class"):
                    class_node = tree_by_id(self.clean_tree, self.demonstrated["node_id"])
                    expect(tree_names(tree_child(class_node, "demonstratedThrough"))).to(contain(self.demonstrating["name"]))

            with context("with an example retrieved using a property"):
                with before.all:
                    self.retrieving = tree_with(self.stories_tree, "Example", "retrievedUsing")
                    self.retrieved = typed_child(self.retrieving, "retrievedUsing", "Property")

                with it("should place that property under retrievedUsing"):
                    expect(str(self.retrieved["node_id"]).startswith("clean_engineering:Property:")).to(equal(True))

                with it("should parent retrievedUsing on the example"):
                    expect(tree_child(self.retrieving, "retrievedUsing")["name"]).to(equal("retrievedUsing"))

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
                self.ddd_tree = self.ddd.root_node.serialize()
                self.bounded_context = tree_named(self.ddd_tree, "bounded context", "BoundedContext")
                self.aggregate = tree_named(self.ddd_tree, "account-credentials", "Aggregate")

            with it("should count one bounded context"):
                expect(tree_count(self.ddd_tree, "BoundedContext")).to(equal(1))

            with it("should count two aggregates"):
                expect(tree_count(self.ddd_tree, "Aggregate")).to(equal(2))

            with it("should count zero entities"):
                expect(tree_count(self.ddd_tree, "Entity")).to(equal(0))

            with it("should count two entity roots"):
                expect(tree_count(self.ddd_tree, "EntityRoot")).to(equal(2))

            with it("should count five value objects"):
                expect(tree_count(self.ddd_tree, "ValueObject")).to(equal(5))

            with it("should count two repositories"):
                expect(tree_count(self.ddd_tree, "Repository")).to(equal(2))

            with it("should order root, owns, belongsTo, accesses, and associates"):
                expect(self.ddd.edge_type_kinds).to(equal(["root", "owns", "belongsTo", "accesses", "associates"]))

            with it("should include only domain stereotypes"):
                expect(
                    owned_types(self.ddd_tree, "ddd")
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
                expect(tree_names(self.ddd_tree)).to(equal(["bounded context"]))

            with it("should own account-credentials and customer under the bounded context"):
                expect(tree_names(self.bounded_context)).to(equal(["account-credentials", "customer"]))

            with it("should identify the customer aggregate by its source path and keep its members"):
                customer = tree_named(self.ddd_tree, "customer", "Aggregate")
                expect(customer["node_id"]).to(equal("ddd:Aggregate:src/customer"))
                expect({"Customer", "CustomerRepository", "Address", "Identity"} <= set(tree_names(customer))).to(equal(True))

            with it("should leave a belongsTo copy of the customer aggregate without its members"):
                copies = [
                    item
                    for item in walk_tree(self.ddd_tree)
                    if item.get("node_id") == "ddd:Aggregate:src/customer" and not item.get("children")
                ]
                expect(len(copies)).to(be_above(0))

            with it("should include AccountCredentials"):
                expect(tree_names(self.aggregate)).to(contain("AccountCredentials"))

            with it("should include ValidationCode"):
                expect(tree_names(self.aggregate)).to(contain("ValidationCode"))

            with it("should include AccountToken"):
                expect(tree_names(self.aggregate)).to(contain("AccountToken"))

            with it("should include AccountCredentialsRepository"):
                expect(tree_names(self.aggregate)).to(contain("AccountCredentialsRepository"))

            with it("should type AccountCredentials as an entity root"):
                expect(tree_child(self.aggregate, "AccountCredentials")["type"]).to(equal("EntityRoot"))

            with context("with a bounded context, an aggregate, an entity root, a value object, and a repository"):
                with it("should parent the bounded context on the practice"):
                    expect(tree_child(self.ddd_tree, "bounded context")["type"]).to(equal("BoundedContext"))

                with it("should parent the aggregate on its bounded context"):
                    expect(tree_child(self.bounded_context, "account-credentials")["type"]).to(equal("Aggregate"))

                with it("should parent the entity root on its aggregate"):
                    expect(tree_child(self.aggregate, "AccountCredentials")["type"]).to(equal("EntityRoot"))

                with it("should parent the value object on its aggregate"):
                    expect(direct_child(self.ddd_tree, "Aggregate", "ValueObject")["type"]).to(equal("ValueObject"))

                with it("should parent the repository on its aggregate"):
                    expect(direct_child(self.ddd_tree, "Aggregate", "Repository")["type"]).to(equal("Repository"))

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
            with before.all:
                self.bdd_tree = self.graph.practice("bdd").root_node.serialize()

            with it("should count zero specs"):
                expect(tree_count(self.bdd_tree, "Spec")).to(equal(0))

            with it("should have no edges"):
                expect(tree_names(self.bdd_tree)).to(equal([]))

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
            with before.all:
                self.ux_tree = self.graph.practice("ux").root_node.serialize()

            with it("should count zero maps"):
                expect(tree_count(self.ux_tree, "UxMap")).to(equal(0))

            with it("should have no edges"):
                expect(tree_names(self.ux_tree)).to(equal([]))

            with it("should have no edge types"):
                expect(self.graph.practice("ux").edge_type_kinds).to(equal([]))

        with context("with a typescript pack and a python pack"):
            with it("should load the typescript class query"):
                expect((query_pack("clean_engineering", "typescript") / "nodes" / "classes.ql").is_file()).to(equal(True))

            with it("should load the python class query"):
                expect((query_pack("clean_engineering", "python") / "nodes" / "classes.ql").is_file()).to(equal(True))


def _node(practice: CodeQLPracticeGraph, type: str, name: str, line: int) -> CodeQLNode:
    return CodeQLNode(practice, type, f"{type}:{line}:{name}", name, Source("story.ts", line, line))


with description("a scenario"):
    with context("with steps recorded in query order"):
        with before.each:
            self.practice = CodeQLPracticeGraph("stories")
            self.scenario = _node(self.practice, "Scenario", "Create account", 139)
            self.given = _node(self.practice, "Step", "given the account exists", 10)
            self.when = _node(self.practice, "Step", "when the User creates their account", 20)
            self.then = _node(self.practice, "Step", "then the account is unconfirmed", 30)
            owns = {"kind": "owns", "order": 1, "display": "direct"}
            self.practice.record(owns, self.scenario, self.then)
            self.practice.record(owns, self.scenario, self.when)
            self.practice.record(owns, self.scenario, self.given)
            self.scenario.populate()

        with it("should list the steps in source order"):
            names = [child["name"] for child in self.scenario.serialize()["children"]]
            expect(names).to(equal([self.given.name, self.when.name, self.then.name]))

    with context("with an invoked operation recorded before an earlier definition"):
        with before.each:
            self.practice = CodeQLPracticeGraph("stories")
            self.step = _node(self.practice, "Step", "when the User creates their account", 20)
            self.later = _node(self.practice, "Operation", "register", 80)
            self.earlier = _node(self.practice, "Operation", "save", 5)
            invokes = {"kind": "invokes", "order": 2, "display": "grouped"}
            self.practice.record(invokes, self.step, self.later)
            self.practice.record(invokes, self.step, self.earlier)
            self.step.populate()

        with it("should keep that call order under the step"):
            names = tree_names(tree_child(self.step.serialize(), "invokes"))
            expect(names).to(equal([self.later.name, self.earlier.name]))


with description("a step"):
    with context("with a stored line on the following statement"):
        with before.each:
            relative = "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts"
            self.source = Source(relative, 146, 160, str(_SAMPLE))
            self.source.align_to_label("when the User creates their account")

        with it("should open on that call in the file"):
            expect(self.source.start_line).to(equal(142))
            expect(self.source.text.splitlines()[0]).to(contain("when('the User creates their account'"))

        with it("should stop at the end of that call"):
            expect("then(" in self.source.text).to(equal(False))
