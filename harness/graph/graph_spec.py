"""A graph loaded from the account-credentials working copy."""

import json
from pathlib import Path

_HERE = Path(__file__).resolve().parent

from expects import be, be_above, be_none, contain, equal, expect
from harness.installation.destination import data_of  # noqa: E402
from mamba import after, before, context, description, it

from harness.graph.graph import EdgeType, Graph, Node, PracticeGraph, Source
from harness.graph.pattern_overlays import PatternOverlays

_ROOT = _HERE
_SAMPLE = _ROOT / "_examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]
# CustomerRepository.exception takes four parameters, over the three limit-operation-parameters allows.
_OVER_LIMIT = "exception"
# A story's source widens from its shareStory line through the call's closing line.
_HANDLE_REQUEST_END = 449
# Stories records each step as its phase type; the schema declares given, when, and then as steps.
_STEP_TYPES = {"Step", "Given", "When", "Then"}
# Serialize appends each node's applicable rules as a "rules" category of Rule rows.
_RULE_TYPES = {"rules", "Rule"}


def walk_tree(node: dict):
    yield node
    for child in node.get("children") or []:
        yield from walk_tree(child)


def tree_names(node: dict) -> list[str]:
    """Graph children by name. The rules category serialize appends is not a graph child."""
    return [child.get("name") for child in node.get("children") or [] if child.get("type") not in _RULE_TYPES]


def tree_count(node: dict, type: str) -> int:
    """Distinct nodes of this type written by serialize. A relationship copy shares the home id."""
    return len({item.get("node_id") for item in walk_tree(node) if item.get("type") == type and item.get("type") != item.get("name")})


def owned_types(node: dict, practice: str) -> set[str]:
    """Types of this practice's nodes in the serialized tree. Holders are named for their kind."""
    return {
        item.get("type")
        for item in walk_tree(node)
        if item.get("type") not in {None, "Practice", *_RULE_TYPES}
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


def _is_type(item: dict, type: str) -> bool:
    if type == "Step":
        return item.get("type") in _STEP_TYPES
    return item.get("type") == type


def tree_with(node: dict, type: str, child_name: str) -> dict:
    for item in walk_tree(node):
        if _is_type(item, type) and any(child.get("name") == child_name for child in item.get("children") or []):
            return item
    raise AssertionError(f"no {type} with {child_name}")


def tree_by_id(node: dict, node_id: str) -> dict:
    for item in walk_tree(node):
        if item.get("node_id") == node_id and item.get("children"):
            return item
    raise AssertionError(f"missing {node_id}")


def direct_child(node: dict, parent_type: str, child_type: str) -> dict:
    for item in walk_tree(node):
        if not _is_type(item, parent_type):
            continue
        for child in item.get("children") or []:
            if _is_type(child, child_type):
                return child
    raise AssertionError(f"no {child_type} under {parent_type}")


def rule_on(node: dict, slug: str) -> dict:
    return tree_child(tree_child(node, "rules"), slug)


def _rule_names(node: dict) -> list[str]:
    return [child["name"] for child in tree_child(node, "rules")["children"]]


def typed_child(node: dict, holder: str, type: str) -> dict:
    for child in tree_child(node, holder).get("children") or []:
        if child.get("type") == type:
            return child
    raise AssertionError(f"missing {type} under {holder}")


_STORY_FOLDER = "tests/onboard-a-customer/authenticate-user"
_ENTITY_ROOT_FILE = "src/account-credentials/account-credentials.ts"
_STORY_FILE = f"{_STORY_FOLDER}/authenticate_user.story.shared.ts"
_EXAMPLES_FILE = f"{_STORY_FOLDER}/examples/account-credentials.examples.ts"
_SPEC_FILE = f"{_STORY_FOLDER}/authenticate_user.story.server.spec.ts"


def edited_graph(files: list[str]) -> Graph:
    graph = Graph()
    data_of(graph.load_files(str(_SAMPLE), _PRACTICES, files))
    return graph


def _inside(file: str | None, scope: list[str]) -> bool:
    file = (file or "").replace("\\", "/")
    return any(file == item or file.startswith(item + "/") for item in scope)


def _practice_nodes(graph: Graph, practice: str, scope: list[str]) -> list[Node]:
    nodes = [node for group in graph.practice(practice).nodes.values() for node in group]
    return [node for node in nodes if _inside(node.source.file, scope)]


def nodes_in(graph: Graph, practice: str, scope: list[str]) -> set[str]:
    return {node.node_id for node in _practice_nodes(graph, practice, scope)}


def violations_in(graph: Graph, practice: str, scope: list[str]) -> set[tuple[str, str]]:
    return {(slug, node.node_id) for node in _practice_nodes(graph, practice, scope) for slug in node.rules.failed_slugs}


def edges_in(graph: Graph, practice: str, scope: list[str]) -> set[tuple[str, str, str]]:
    edges = [edge for group in graph.practice(practice).edges.values() for edge in group]
    return {
        (edge.parent.node_id, edge.child.node_id, edge.kind)
        for edge in edges
        if _inside(edge.parent.source.file, scope) and _inside(edge.child.source.file, scope)
    }


with description("a graph"):
    with context("with nothing loaded yet"):
        with it("should name every practice it can load, so the explorer loads each one on the folder it opens"):
            expect(Graph().practice_names()).to(equal(["stories", "ddd", "ux", "clean_engineering", "bdd"]))

    with context("loaded from the account credentials working copy"):
        with before.all:
            self.graph = Graph()
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            data_of(self.graph.load_working_copy(str(_ROOT), roots, database=str(_SAMPLE), force=True))

        with context("with clean engineering"):
            with before.all:
                self.clean = self.graph.practice("clean_engineering")
                self.clean_tree = data_of(self.clean.root_node.serialize())
                self.account = tree_named(self.clean_tree, "AccountCredentials", "OoadClass")

            with it("should count three modules"):
                expect(tree_count(self.clean_tree, "Module")).to(equal(3))

            with it("should count fourteen classes"):
                classes = {
                    item.get("node_id")
                    for item in walk_tree(self.clean_tree)
                    if item.get("type") == "OoadClass" and item.get("name") != "_module"
                }
                expect(len(classes)).to(equal(14))

            with it("should hold each file's top-level functions in a _module class"):
                expect(tree_count(self.clean_tree, "OoadClass") - 14).to(equal(2))

            with it("should include module, class, operation, property, and parameter nodes"):
                expect(
                    {"Module", "OoadClass", "Operation", "Property", "Parameter"} <= owned_types(self.clean_tree, "clean_engineering")
                ).to(equal(True))

            with it("should order relative, owns, properties, belongsTo, hasParameter, hasType, invokedBy, and dependsOn"):
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
                            "invokedBy",
                            "returns",
                            "retrievedUsing",
                            "dependsOn",
                            "usedBy",
                        ]
                    )
                )

            with it("should own the account-credentials, customer, and onboarding modules"):
                modules = [child["name"] for child in self.clean_tree["children"] if child.get("type") == "Module"]
                expect(modules).to(equal(["account-credentials", "customer", "onboarding"]))

            with it("should show a package for a folder without a module context"):
                package = tree_named(self.clean_tree, "authenticate-user", "Package")
                expect(package["node_id"]).to(equal("clean_engineering:Package:tests/onboard-a-customer/authenticate-user"))
                expect(tree_names(package)).to(contain("examples"))

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
                    expect(self.register.source.start_line).to(be_above(0))

                with it("should mark the emailValidationCode call"):
                    expect(self.register.source.text).to(contain("/* call:this.emailValidationCode */"))

            with context("with the practice selected"):
                with before.all:
                    self.graph.filter.select_practices(["clean_engineering"])

                with it("should offer the class type named by the class query"):
                    expect(self.graph.filter.node_types).to(contain("OoadClass"))

                with it("should offer the module type named by the module query"):
                    expect(self.graph.filter.node_types).to(contain("Module"))

                with it("should offer the package type named by the package query"):
                    expect(self.graph.filter.node_types).to(contain("Package"))

                with it("should return AccountCredentials"):
                    returned = [node["name"] for node in data_of(self.graph.return_nodes())]
                    expect(returned).to(contain("AccountCredentials"))

                with it("should return the account-credentials module"):
                    returned = [node["name"] for node in data_of(self.graph.return_nodes())]
                    expect(returned).to(contain("account-credentials"))

                with context("with operations selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["Operation"])

                    with it("should offer invokedBy for operations"):
                        expect(self.graph.filter.relationships).to(contain("invokedBy"))

                    with it("should offer the operation parameter rule"):
                        expect(self.graph.filter.rules).to(contain("clean_engineering.Operation.limit-operation-parameters"))

                    with it("should leave the class dependency rule out of the rule filter"):
                        expect("use-explicit-dependencies" in self.graph.filter.rules).to(equal(False))

                    with it("should return the failure operation"):
                        returned = [node["name"] for node in data_of(self.graph.return_nodes())]
                        expect(returned).to(contain("failure"))

                    with it("should leave classes out of the operation results"):
                        returned = {node["type"] for node in data_of(self.graph.return_nodes())}
                        expect("OoadClass" in returned).to(equal(False))

                    with it("should attach the parameter rule to the operation that fails it"):
                        failure = tree_named(self.clean_tree, _OVER_LIMIT, "Operation")
                        rule = rule_on(failure, "limit-operation-parameters")
                        expect(rule["status"]).to(equal("violating"))
                        expect(len(rule["violations"])).to(be_above(0))

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
                        self.violation_tree = data_of(self.graph.practice("clean_engineering").root_node.serialize())

                    with it("should return the operation that fails the rule"):
                        returned = [node["name"] for node in data_of(self.graph.return_nodes())]
                        expect(returned).to(contain(_OVER_LIMIT))

                    with it("should leave the operation that passes the rule out"):
                        returned = [node["name"] for node in data_of(self.graph.return_nodes())]
                        expect("register" in returned).to(equal(False))

                    with it("should attach the violation on the returned operation"):
                        returned = data_of(self.graph.return_nodes())
                        failure = next(node for node in returned if node["name"] == _OVER_LIMIT)
                        attached = [rule for rule in failure["rules"] if rule["name"] == "limit-operation-parameters"]
                        expect(len(attached)).to(equal(1))
                        expect(attached[0]["status"]).to(equal("violating"))
                        expect(len(attached[0]["violations"])).to(be_above(0))

                    with it("should attach that violation on the serialized graph"):
                        failure = tree_named(self.violation_tree, _OVER_LIMIT, "Operation")
                        rule = rule_on(failure, "limit-operation-parameters")
                        expect(rule["status"]).to(equal("violating"))
                        expect(len(rule["violations"])).to(be_above(0))

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
                        expect(self.graph.filter.rules).to(contain("clean_engineering.OoadClass.use-explicit-dependencies"))

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
                        returned = {node["type"] for node in data_of(self.graph.return_nodes())}
                        expect("Module" in returned).to(equal(False))

        with context("with stories"):
            with before.all:
                self.stories = self.graph.practice("stories")
                self.stories_tree = data_of(self.stories.root_node.serialize())
                self.clean_tree = data_of(self.graph.practice("clean_engineering").root_node.serialize())

            with it("should count one epic"):
                expect(tree_count(self.stories_tree, "Epic")).to(equal(1))

            with it("should count six stories"):
                expect(tree_count(self.stories_tree, "Story")).to(equal(6))

            with it("should include epic, sub-epic, story, scenario, background, step, and example nodes"):
                expect(
                    {"Epic", "SubEpic", "Story", "Scenario", "Background", "Given", "When", "Then", "Example"}
                    <= owned_types(self.stories_tree, "stories")
                ).to(equal(True))

            with it("should own Onboard A Customer"):
                expect(tree_names(self.stories_tree)).to(contain("Onboard A Customer"))

            with context("with a story map"):
                with before.all:
                    self.handle_request = tree_named(self.stories_tree, "Handle Request", "Story")
                    self.submit_order = tree_named(self.stories_tree, "Submit Order", "Story")
                    self.create_account = tree_named(self.stories_tree, "Create Account", "Story")
                    self.onboard = tree_named(self.stories_tree, "Onboard A Customer", "Epic")
                    self.authenticate = tree_named(self.stories_tree, "Authenticate User", "SubEpic")

                with it("should list the shared story-node rules"):
                    names = _rule_names(self.handle_request)
                    expect(
                        {
                            "vocabulary-traces-to-domain-source",
                            "read-all-source-context-in-full",
                            "do-not-invent-requirements",
                        }
                        <= set(names)
                    ).to(equal(True))

                with it("should list the epic rules"):
                    expect(
                        {"verb-noun-format", "branch-on-mechanical-uniqueness", "four-to-nine-children"}
                        <= set(_rule_names(self.onboard))
                    ).to(equal(True))

                with it("should list the sub-epic rules"):
                    expect(
                        {"verb-noun-format", "branch-on-mechanical-uniqueness", "four-to-nine-children"}
                        <= set(_rule_names(self.authenticate))
                    ).to(equal(True))

                with it("should list the story rules"):
                    expect(
                        {
                            "verb-noun-format",
                            "story-name-captures-system-mechanic",
                            "right-size-story-nodes",
                            "behaviours-not-one-time-tasks",
                            "story-scenarios-at-most-seven",
                        }
                        <= set(_rule_names(self.handle_request))
                    ).to(equal(True))

                with it("should violate verb-noun format on Handle Request"):
                    hit = rule_on(self.handle_request, "verb-noun-format")
                    expect(hit["status"]).to(equal("violating"))
                    expect(hit["violations"][0]["message"]).to(
                        equal("Story 'Handle Request': name should start with a verb (got generic-verb).")
                    )

                with it("should store the verb-noun span on Handle Request"):
                    hit = rule_on(self.handle_request, "verb-noun-format")["violations"][0]
                    expect(hit["location"]).to(
                        equal("tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts")
                    )
                    expect(hit["line"]).to(equal(444))
                    expect(hit["end_line"]).to(equal(_HANDLE_REQUEST_END))

                with it("should violate the system mechanic on Handle Request"):
                    hit = rule_on(self.handle_request, "story-name-captures-system-mechanic")
                    expect(hit["status"]).to(equal("violating"))
                    expect(hit["violations"][0]["message"]).to(
                        equal(
                            "Story 'Handle Request' names a generic handler; use the system mechanic (e.g. 'Submit Order')."
                        )
                    )

                with it("should store the system-mechanic span on Handle Request"):
                    hit = rule_on(self.handle_request, "story-name-captures-system-mechanic")["violations"][0]
                    expect(hit["line"]).to(equal(444))
                    expect(hit["end_line"]).to(equal(_HANDLE_REQUEST_END))

                with it("should leave verb-noun format passing on Submit Order"):
                    expect(rule_on(self.submit_order, "verb-noun-format")["status"]).to(equal("passing"))

                with it("should violate four to nine children on the epic"):
                    hit = rule_on(self.onboard, "four-to-nine-children")
                    expect(hit["status"]).to(equal("violating"))
                    expect(hit["violations"][0]["message"]).to(
                        equal("epic 'Onboard A Customer': 1 children (target 4-9)")
                    )

                with it("should store the epic child-count hit on the line that names the epic"):
                    hit = rule_on(self.onboard, "four-to-nine-children")["violations"][0]
                    expect({"location": hit["location"], "line": hit["line"], "end_line": hit["end_line"]}).to(
                        equal(
                            {
                                "location": "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts",
                                "line": 1,
                                "end_line": 1,
                            }
                        )
                    )

                with it("should leave four to nine children passing on the sub-epic"):
                    expect(rule_on(self.authenticate, "four-to-nine-children")["status"]).to(equal("passing"))

                with it("should leave do-not-invent-requirements prompt"):
                    expect(rule_on(self.handle_request, "do-not-invent-requirements")["status"]).to(equal("prompt"))

                with context("with a story that repeats a sibling story"):
                    with it("should record that the story is too similar to another story on the same map node"):
                        message = rule_on(self.submit_order, "right-size-story-nodes")["violations"][0]["message"]
                        expect(message).to(
                            equal("Story 'Submit Order' is too similar to another story on the same map node.")
                        )

                    with it("should store that similarity hit on the story line"):
                        hit = rule_on(self.submit_order, "right-size-story-nodes")["violations"][0]
                        expect({"location": hit["location"], "line": hit["line"], "end_line": hit["end_line"]}).to(
                            equal(
                                {
                                    "location": "tests/onboard-a-customer/authenticate-user/authenticate_user.story.shared.ts",
                                    "line": 429,
                                    "end_line": 435,
                                }
                            )
                        )

                with context("with a story whose siblings name distinct interactions"):
                    with it("should leave that story distinct from its siblings"):
                        expect(rule_on(self.create_account, "right-size-story-nodes")["status"]).to(equal("passing"))

                with context("with the story type selected"):
                    with before.all:
                        self.graph.filter.select_practices(["stories"])
                        self.graph.filter.select_node_types(["Story"])

                    with it("should offer the story-node rules"):
                        expect(
                            {
                                "stories.Story.vocabulary-traces-to-domain-source",
                                "stories.Story.read-all-source-context-in-full",
                                "stories.Story.do-not-invent-requirements",
                            }
                            <= set(self.graph.filter.rules)
                        ).to(equal(True))

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
                    expect(direct_child(self.stories_tree, "Scenario", "Step")["type"] in _STEP_TYPES).to(equal(True))

                with it("should list Create account steps in source order"):
                    steps = [
                        child["name"]
                        for child in tree_named(self.stories_tree, "Create account", "Scenario")["children"]
                        if child["type"] in _STEP_TYPES
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

                with it("should place that step back under the operation, under invokedBy"):
                    operation = tree_by_id(self.clean_tree, self.invoked["node_id"])
                    expect(tree_names(tree_child(operation, "invokedBy"))).to(contain(self.invoking_step["name"]))

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
                    expect([node["name"] for node in data_of(self.graph.return_nodes())]).to(contain("Onboard A Customer"))

                with it("should leave classes out of the results"):
                    expect("OoadClass" in {node["type"] for node in data_of(self.graph.return_nodes())}).to(equal(False))

        with context("with domain-driven design"):
            with before.all:
                self.ddd = self.graph.practice("ddd")
                self.ddd_tree = data_of(self.ddd.root_node.serialize())
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

            with it("should identify the bounded context by the folder that contains it"):
                expect(self.bounded_context["node_id"]).to(equal("ddd:BoundedContext:src:bounded context"))

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
                    expect([node["name"] for node in data_of(self.graph.return_nodes())]).to(contain("bounded context"))

                with it("should leave stories out of the results"):
                    expect("Story" in {node["type"] for node in data_of(self.graph.return_nodes())}).to(equal(False))

                with context("with entity roots selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["EntityRoot"])

                    with it("should offer accesses for entity roots"):
                        expect(self.graph.filter.relationships).to(contain("accesses"))

                    with it("should leave owns out of the entity root relationships"):
                        expect("owns" in self.graph.filter.relationships).to(equal(False))

                    with it("should return AccountCredentials"):
                        expect([node["name"] for node in data_of(self.graph.return_nodes())]).to(contain("AccountCredentials"))

                    with it("should leave aggregates out of the entity root results"):
                        expect("Aggregate" in {node["type"] for node in data_of(self.graph.return_nodes())}).to(equal(False))

                with context("with aggregates selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["Aggregate"])

                    with it("should offer owns for aggregates"):
                        expect(self.graph.filter.relationships).to(contain("owns"))

                    with it("should leave accesses out of the aggregate relationships"):
                        expect("accesses" in self.graph.filter.relationships).to(equal(False))

                    with it("should return the account-credentials aggregate"):
                        expect([node["name"] for node in data_of(self.graph.return_nodes())]).to(contain("account-credentials"))

                    with it("should leave entity roots out of the aggregate results"):
                        expect("EntityRoot" in {node["type"] for node in data_of(self.graph.return_nodes())}).to(equal(False))

        with context("with behavior-driven development that has one story spec without describes"):
            with before.all:
                self.bdd_tree = data_of(self.graph.practice("bdd").root_node.serialize())

            with it("should count one spec"):
                expect(tree_count(self.bdd_tree, "Spec")).to(equal(1))

            with it("should own the server story spec"):
                expect(tree_names(self.bdd_tree)).to(equal(["authenticate_user.story.server.spec"]))

            with it("should count zero descriptions"):
                expect(tree_count(self.bdd_tree, "Description")).to(equal(0))

            with it("should have only the owns edge type"):
                expect(self.graph.practice("bdd").edge_type_kinds).to(equal(["owns"]))

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
                    expect("OoadClass" in {node["type"] for node in data_of(self.graph.return_nodes())}).to(equal(False))

                with context("with specs selected"):
                    with before.all:
                        self.graph.filter.select_node_types(["Spec"])

                    with it("should leave descriptions out of the node filter"):
                        expect("Description" in self.graph.filter.node_types).to(equal(False))

                    with it("should offer only owns"):
                        expect(self.graph.filter.relationships).to(equal(["owns"]))

                    with it("should leave descriptions out of the results"):
                        expect("Description" in {node["type"] for node in data_of(self.graph.return_nodes())}).to(equal(False))

        with context("with experience design that has no map"):
            with before.all:
                self.ux_tree = data_of(self.graph.practice("ux").root_node.serialize())

            with it("should count zero maps"):
                expect(tree_count(self.ux_tree, "UxMap")).to(equal(0))

            with it("should have no edges"):
                expect(tree_names(self.ux_tree)).to(equal([]))

            with it("should have no edge types"):
                expect(self.graph.practice("ux").edge_type_kinds).to(equal([]))

    with context("loaded from only the edited files of a working copy that every graph practice reads"):
        with before.all:
            self.full = Graph()
            roots = {name: str(_SAMPLE) for name in _PRACTICES}
            data_of(self.full.load_working_copy(str(_ROOT), roots, database=str(_SAMPLE), force=True))

        with context("with an edited entity root"):
            with before.all:
                self.scope = [_ENTITY_ROOT_FILE]
                self.edited = edited_graph(self.scope)

            with it("should read the same clean engineering nodes as the full load"):
                expect(nodes_in(self.edited, "clean_engineering", self.scope)).to(
                    equal(nodes_in(self.full, "clean_engineering", self.scope))
                )

            with it("should find the same clean engineering rule violations"):
                expect(violations_in(self.edited, "clean_engineering", self.scope)).to(
                    equal(violations_in(self.full, "clean_engineering", self.scope))
                )

            with it("should keep the edges to classes declared in files that were not edited"):
                expect(edges_in(self.edited, "clean_engineering", self.scope)).to(
                    equal(edges_in(self.full, "clean_engineering", self.scope))
                )

            with it("should place the same ddd building blocks"):
                expect(nodes_in(self.edited, "ddd", self.scope)).to(equal(nodes_in(self.full, "ddd", self.scope)))

            with it("should find the same ddd rule violations"):
                expect(len(violations_in(self.edited, "ddd", self.scope))).to(be_above(0))
                expect(violations_in(self.edited, "ddd", self.scope)).to(equal(violations_in(self.full, "ddd", self.scope)))

        with context("with an edited story file"):
            with before.all:
                self.scope = [_STORY_FILE]
                self.edited = edited_graph(self.scope)

            with it("should read the same story nodes as the full load"):
                expect(nodes_in(self.edited, "stories", self.scope)).to(equal(nodes_in(self.full, "stories", self.scope)))

            with it("should find the same story rule violations"):
                expect(len(violations_in(self.edited, "stories", self.scope))).to(be_above(0))
                expect(violations_in(self.edited, "stories", self.scope)).to(equal(violations_in(self.full, "stories", self.scope)))

        with context("with an edited story examples file"):
            with before.all:
                self.scope = [_EXAMPLES_FILE]
                self.edited = edited_graph(self.scope)

            with it("should read the examples the story declares from that file"):
                expected = nodes_in(self.full, "stories", self.scope)
                expect(len(expected)).to(be_above(0))
                expect(nodes_in(self.edited, "stories", self.scope)).to(equal(expected))

        with context("with an edited spec file"):
            with before.all:
                self.scope = [_SPEC_FILE]
                self.edited = edited_graph(self.scope)

            with it("should read the same bdd nodes as the full load"):
                expect(nodes_in(self.edited, "bdd", self.scope)).to(equal(nodes_in(self.full, "bdd", self.scope)))

            with it("should find the same bdd rule violations"):
                expect(len(violations_in(self.edited, "bdd", self.scope))).to(be_above(0))
                expect(violations_in(self.edited, "bdd", self.scope)).to(equal(violations_in(self.full, "bdd", self.scope)))

            with it("should leave the files that were not edited out"):
                expect(nodes_in(self.edited, "clean_engineering", ["src"])).to(equal(set()))


def _node(practice: PracticeGraph, type: str, name: str, line: int) -> Node:
    return Node(practice, type, f"{type}:{line}:{name}", name, Source("story.ts", line, line))


with description("a node's fidelity"):
    with context("with a story node"):
        with it("should be the fidelity the stories schema gives a story"):
            expect(_node(Graph().practice("stories"), "Story", "Create account", 1).fidelity.name).to(equal("story_map"))

        with it("should be that fidelity of the practice the node belongs to"):
            node = _node(Graph().practice("stories"), "Story", "Create account", 1)
            expect(node.fidelity).to(be(node.practice.guidance.fidelities["story_map"]))

    with context("with a scenario node"):
        with it("should be the fidelity the stories schema gives a scenario"):
            expect(_node(Graph().practice("stories"), "Scenario", "Create account", 1).fidelity.name).to(equal("scenarios"))

    with context("with a class node"):
        with it("should match its graph type to the schema's class type"):
            expect(_node(Graph().practice("clean_engineering"), "OoadClass", "Order", 1).fidelity.name).to(equal("model"))

    with context("with a node created at a low fidelity"):
        with before.each:
            self.entity = _node(Graph().practice("ddd"), "Entity", "Order", 1)

        with it("should be the fidelity that first creates it"):
            expect(self.entity.fidelity.name).to(equal("model"))

        with it("should also belong to every higher fidelity of its practice"):
            expect([fidelity.name for fidelity in self.entity.fidelities]).to(equal(["model", "tactics"]))

        with it("should reach implementation from the first fidelity of its practice"):
            story = _node(Graph().practice("stories"), "Story", "Create account", 1)
            expect([fidelity.name for fidelity in story.fidelities]).to(equal(["story_map", "scenarios", "acceptance_tests"]))

    with context("with a type the schema gives no fidelity"):
        with it("should have none"):
            expect(_node(Graph().practice("stories"), "Unmapped", "Create account", 1).fidelity).to(be_none)


with description("a scenario"):
    with context("with steps recorded in query order"):
        with before.each:
            self.practice = Graph().practice("stories")
            self.scenario = _node(self.practice, "Scenario", "Create account", 139)
            self.given = _node(self.practice, "Step", "given the account exists", 10)
            self.when = _node(self.practice, "Step", "when the User creates their account", 20)
            self.then = _node(self.practice, "Step", "then the account is unconfirmed", 30)
            owns = EdgeType("owns", 1, "direct")
            self.practice.record(owns, self.scenario, self.then)
            self.practice.record(owns, self.scenario, self.when)
            self.practice.record(owns, self.scenario, self.given)
            self.scenario.populate()

        with it("should list the steps in source order"):
            names = tree_names(data_of(self.scenario.serialize()))
            expect(names).to(equal([self.given.name, self.when.name, self.then.name]))

    with context("with an invoked operation recorded before an earlier definition"):
        with before.each:
            self.practice = Graph().practice("stories")
            self.step = _node(self.practice, "Step", "when the User creates their account", 20)
            self.later = _node(self.practice, "Operation", "register", 80)
            self.earlier = _node(self.practice, "Operation", "save", 5)
            invokes = EdgeType("invokes", 2, "grouped")
            self.practice.record(invokes, self.step, self.later)
            self.practice.record(invokes, self.step, self.earlier)
            self.step.populate()

        with it("should keep that call order under the step"):
            names = tree_names(tree_child(data_of(self.step.serialize()), "invokes"))
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


with description("a scenario row with only a start line"):
    with before.each:
        import tempfile

        self.temp = tempfile.TemporaryDirectory()
        relative = "story.story.shared.ts"
        body = "\n".join(
            [
                "shareStory('Create Account', () => {",
                "  scenario('Display Create Account', ({ when, then }) => {",
                "    when('step', () => {});",
                "    then('done', () => {});",
                "  });",
                "});",
            ]
        )
        path = Path(self.temp.name) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        self.source = Source(relative, 2, 2, self.temp.name)
        self.source.widen_to_call_close()

    with it("should include the full scenario through its closing brace"):
        expect(len(self.source.text.splitlines())).to(be_above(1))
        expect(self.source.text).to(contain("when("))
        expect(self.source.text).to(contain("then("))


with description("an example a story test imports"):
    with before.each:
        import tempfile

        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        files = {
            "examples/account.examples.ts": "\n".join(
                [
                    "export function accountWith(name: string) {",
                    "  return { name }",
                    "}",
                    "",
                    "export const VERIFIED = {",
                    "  status: 'verified',",
                    "}",
                    "",
                    "export const STAGES = [",
                    "  'Discovery',",
                    "  'Specification',",
                    "]",
                ]
            ),
            "verify-account/verify_account_story.test.ts": "\n".join(
                [
                    "import { accountWith, STAGES, VERIFIED } from '../examples/account.examples'",
                    "const LOCAL = 'only here'",
                    "story('Verify Account', () => {",
                    "  given('a verified account', () => accountWith(VERIFIED.status))",
                    "})",
                ]
            ),
        }
        for relative, body in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
        self.story_test = "verify-account/verify_account_story.test.ts"

    with after.each:
        self.temp.cleanup()

    def _aligned(self, name: str) -> Source:
        source = Source(self.story_test, 4, 4, self.temp.name)
        source.align_to_example_export(self.temp.name, name)
        return source

    with context("that is a fixture function"):
        with it("should sit in its examples file"):
            expect(self._aligned("accountWith").file).to(equal("examples/account.examples.ts"))

    with context("that is an exported constant"):
        with it("should sit in its examples file"):
            expect(self._aligned("VERIFIED").file).to(equal("examples/account.examples.ts"))

        with it("should span the whole object it declares"):
            source = self._aligned("VERIFIED")
            expect((source.start_line, source.end_line)).to(equal((5, 7)))

    with context("that is an exported list"):
        with it("should span the whole list it declares"):
            source = self._aligned("STAGES")
            expect((source.start_line, source.end_line)).to(equal((9, 12)))

    with context("that is a constant the story test declares itself"):
        with it("should stay at the story test"):
            expect(self._aligned("LOCAL").file).to(equal(self.story_test))


with description("a graph's practice"):
    with before.each:
        self.graph = Graph()
        self.practice = self.graph.practice("stories")
        self.story = self.practice.add_named("Story", "stories:Story:Create account", "Create account", Source("story.md", 1, 1))

    with it("should hold the practice's guidance"):
        expect(self.practice.guidance.key).to(equal("stories"))

    with it("should hold a guidance that knows the graph"):
        expect(self.practice.guidance.graph).to(be(self.graph))

    with it("should hold a guidance at no fidelity, since a fidelity belongs to a call"):
        expect(self.practice.guidance.fidelities.current).to(be_none)

    with it("should keep the same guidance when the graph asks for the practice again"):
        expect(self.graph.practice("stories").guidance).to(be(self.practice.guidance))

    with it("should give a node its practice by reference"):
        expect(self.story.practice.guidance).to(be(self.practice.guidance))

    with it("should give the practice its nodes through the graph it holds"):
        expect(self.practice.guidance.graph.nodes_of(self.practice.guidance)).to(equal([self.story]))


with description("a node's rules"):
    with context("on a story"):
        with before.each:
            self.story = _node(Graph().practice("stories"), "Story", "Create account", 1)

        with it("should hold the rules the stories schema gives a story"):
            expect(self.story.rules.slugs).to(contain("story-scenarios-at-most-seven"))

        with it("should run a rule whose check applies to a story"):
            expect([rule.runs for rule in self.story.rules if rule.slug == "story-scenarios-at-most-seven"]).to(equal([True]))

    with context("on a DDD entity"):
        with before.each:
            self.entity = _node(Graph().practice("ddd"), "Entity", "Order", 1)

        with it("should carry the rules of the Clean Engineering class it is anchored to"):
            expect(self.entity.rules.slugs).to(contain("keep-classes-single-responsibility"))

    with context("on a node whose graph applies a pattern overlay"):
        with before.each:
            graph = Graph()
            graph.overlays = PatternOverlays(["lern_domain_driven"]).paths
            self.root = _node(graph.practice("ddd"), "NodeRoot", "order-node", 1)

        with it("should carry the rules the pattern adds"):
            expect(self.root.rules.slugs).to(contain("node-decides-next-page"))


with description("a graph a session holds"):
    with before.each:
        import tempfile

        self.folder = Path(tempfile.mkdtemp())
        self.session_folder = self.folder / ".sessions" / "main"
        (self.folder / "src").mkdir()
        self.source = self.folder / "src" / "order.py"
        self.source.write_text("class Order:\n    pass\n", encoding="utf-8")
        self.graph = Graph.of_session(self.session_folder, self.folder)

    with after.each:
        import shutil

        shutil.rmtree(self.folder, ignore_errors=True)

    with it("should be the same graph each time the session asks"):
        expect(Graph.of_session(self.session_folder, self.folder)).to(be(self.graph))

    with it("should read no file until a call loads or refreshes it"):
        expect(_class_names_in(self.graph)).to(equal([]))

    with it("should open every practice on the session's root"):
        expect(self.graph.practice("clean_engineering").source_root).to(equal(str(self.folder.resolve())))

    with context("that is refreshed with a file an action wrote"):
        with before.each:
            data_of(self.graph.refresh([str(self.source)]))

        with it("should read the classes of that file"):
            expect(_class_names_in(self.graph)).to(equal(["Order"]))

        with context("and refreshed again after the file changed"):
            with before.each:
                self.source.write_text("class Invoice:\n    pass\n", encoding="utf-8")
                data_of(self.graph.refresh([str(self.source)]))

            with it("should hold only what the file holds now"):
                expect(_class_names_in(self.graph)).to(equal(["Invoice"]))

        with context("and a second file is written and refreshed"):
            with before.each:
                other = self.folder / "src" / "cart.py"
                other.write_text("class Cart:\n    pass\n", encoding="utf-8")
                data_of(self.graph.refresh([str(other)]))

            with it("should keep the first file's classes and add the second's"):
                expect(_class_names_in(self.graph)).to(equal(["Cart", "Order"]))

        with context("and the file is deleted and refreshed"):
            with before.each:
                self.source.unlink()
                data_of(self.graph.refresh([str(self.source)]))

            with it("should drop its classes"):
                expect(_class_names_in(self.graph)).to(equal([]))

    with context("that is refreshed with a file in a session's folder"):
        with before.each:
            report = self.session_folder / "report.md"
            report.parent.mkdir(parents=True)
            report.write_text("# report\n", encoding="utf-8")
            self.message = data_of(self.graph.refresh([str(report)]))["message"]

        with it("should read nothing, since no practice reads a session's folder"):
            expect(self.message).to(contain("nothing was refreshed"))


def _class_names_in(graph: Graph) -> list[str]:
    return sorted(node.name for node in graph.practice("clean_engineering").nodes.get("OoadClass", []))
