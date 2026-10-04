from pathlib import Path
from tempfile import TemporaryDirectory

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph
from harness.knowledge_graph.model.knowledge_graph_node import (
    KnowledgeGraphCallSource,
    KnowledgeGraphFilter,
    KnowledgeGraphNode,
    KnowledgeGraphNodeType,
    KnowledgeGraphSourceFold,
    WebKnowledgeGraphNode,
    editor_height,
    is_story_node,
    practice_root_labels,
    retained_tree,
    restored_branches,
    database_build_required,
    database_graph_from_scratch,
    extraction_progress,
    rules_for_filters,
    rules_from_guidance,
    retag_practice,
    step_members,
    step_callouts,
    tagged_practice,
)
from practices.stories.model.story_model import Epic, StoryModel

_STORY_NODE_TYPES = {
    "Increment",
    "Epic",
    "SubEpic",
    "Story",
    "Scenario",
    "Background",
    "Step",
    "Example",
    "StoryModel",
}


def _node(name, semantic, practice="", children=None):
    node = KnowledgeGraphNode()
    node.name = name
    node.nodeId = f"{semantic}:{name}"
    node.practice = practice
    node.nodeType = KnowledgeGraphNodeType(semantic, practice, "")
    node.children = list(children or [])
    node.relationships = []
    return node


def _mixed_practice_tree():
    operation = _node("submitFeedback", "Operation", "clean_engineering")
    step = _node("When they send a feedback note", "Step", "stories")
    step.relationships = [{"kind": "invokes", "nodeId": operation.nodeId, "name": operation.name}]
    return [
        _node(
            "domain",
            "Module",
            "clean_engineering",
            [
                _node("Customer", "OoadClass", "clean_engineering", [operation]),
                _node("customer.ts", "File", "clean_engineering"),
                _node("Onboard A Customer", "Story", "stories"),
                _node("Given a plan", "Step", "stories"),
                _node("Ordering", "BoundedContext", "ddd"),
            ],
        ),
        _node(
            "tests",
            "Package",
            "stories",
            [
                _node("Select Plan", "Story", "stories", [step]),
                _node("select-plan.e2e.ts", "File", "stories"),
            ],
        ),
        _node("Customer is known", "Description", "bdd"),
    ]


def _flatten(nodes):
    found = []

    def walk(items):
        for node in items:
            found.append(node)
            walk(getattr(node, "children", []) or [])

    walk(nodes)
    return found


def _graph(folder):
    source = StoryModel()
    source.epics.append(Epic("Onboard", 1))
    graph = KnowledgeGraph(source, None, None, None)
    graph.folder = folder
    return graph


with description("a knowledge graph"):
    with before.each:
        self.temp = TemporaryDirectory()
        self.graph = _graph(self.temp.name)

    with it("should keep web nodes as a subtype and the same operations as typescript"):
        expect(issubclass(WebKnowledgeGraphNode, KnowledgeGraphNode)).to(equal(True))
        for name in (
            "saveKnowledgeGraph",
            "loadKnowledgeGraph",
            "createDatabase",
            "copyMasterToWorkingCopy",
            "copyWorkingCopyToMaster",
            "refreshMaster",
            "reloadWorkingCopy",
            "updateWorkingCopy",
            "choose",
            "open",
            "close",
        ):
            expect(callable(getattr(self.graph, name))).to(equal(True))

    with context("that has been saved"):
        with it("should write the knowledge graph models"):
            self.graph.saveKnowledgeGraph()
            written = (Path(self.temp.name) / "story-map.kg").read_text(encoding="utf-8")
            expect(written).to(contain("Onboard"))

    with context("that has been loaded from a presented explorer graph"):
        with it("should rebuild the nodes from that document"):
            folder = Path(self.temp.name)
            (folder / ".context").mkdir()
            (folder / ".context" / "explorer-graph.json").write_text(
                '{"id": "11111111-1111-1111-1111-111111111111", "folder": "", "practice_graphs": [{"id": "p", "name": "ce", "nodes": [{"node_id": "n", "name": "domain", "practice": "clean_engineering", "semantic_type": "Module"}], "relationships": []}]}',
                encoding="utf-8",
            )
            loaded = KnowledgeGraph()
            loaded.loadKnowledgeGraph(folder)
            expect([node.name for node in loaded.nodes]).to(contain("domain"))

    with context("that has been loaded from a path"):
        with it("should rebuild the nodes from that document"):
            self.graph.saveKnowledgeGraph()
            loaded = KnowledgeGraph()
            loaded.loadKnowledgeGraph(self.temp.name)
            expect([node.name for node in loaded.nodes]).to(contain("Onboard"))

    with context("that has created a database"):
        with before.each:
            (Path(self.temp.name) / "hello.py").write_text("x = 1\n", encoding="utf-8")
            self.graph.createDatabase()

        with it("should write master"):
            expect(Path(self.graph._codeql.master).exists()).to(equal(True))

        with it("should copy master to the working copy"):
            expect(Path(self.graph._codeql.working_copy).exists()).to(equal(True))

    with context("that already has a database"):
        with it("should keep the existing master and working copy"):
            ql_root = Path(self.temp.name) / ".codeql"
            (ql_root / "python-master").mkdir(parents=True)
            (ql_root / "python-working-copy").mkdir()
            marker = ql_root / "python-master" / "kept"
            marker.write_text("keep", encoding="utf-8")
            self.graph.createDatabase()
            expect(marker.read_text(encoding="utf-8")).to(equal("keep"))
            expect((ql_root / "python-working-copy").exists()).to(equal(True))

    with context("that merges the working copy into master"):
        with it("should copy the working copy database onto master"):
            ql_root = Path(self.temp.name) / ".codeql"
            working = ql_root / "python-working-copy"
            master = ql_root / "python-master"
            working.mkdir(parents=True)
            master.mkdir()
            (working / "from-working").write_text("working", encoding="utf-8")
            (master / "from-master").write_text("master", encoding="utf-8")
            (Path(self.temp.name) / "hello.py").write_text("x = 1\n", encoding="utf-8")
            self.graph.refreshMaster()
            expect((master / "from-working").read_text(encoding="utf-8")).to(equal("working"))
            expect((master / "from-master").exists()).to(equal(False))
            expect((Path(self.temp.name) / "story-map.kg").exists()).to(equal(False))

    with context("that reloads the working copy"):
        with it("should load the latest files into the working copy"):
            (Path(self.temp.name) / "hello.py").write_text("x = 1\n", encoding="utf-8")
            self.graph.reloadWorkingCopy()
            expect(Path(self.graph._ql().working_copy).exists()).to(equal(True))
            expect((Path(self.temp.name) / "story-map.kg").exists()).to(equal(False))

    with context("that has updated the working copy"):
        with context("with dirty paths"):
            with it("should be the document that was just saved"):
                self.graph.saveKnowledgeGraph()
                self.graph.updateWorkingCopy([])
                expect((Path(self.temp.name) / "story-map.kg").read_text(encoding="utf-8")).to(
                    contain("Onboard")
                )

    with context("with selected practices"):
        with before.each:
            self.cascade = KnowledgeGraphFilter(["Stories"])

        with it("should fill available stages from those practices"):
            expect(self.cascade.stageFilter.choices).to(contain("Discovery"))

        with it("should fill available node types from those practices and stages"):
            expect(self.cascade.nodeFilter.choices).to(contain("Story"))

        with context("with selected node types"):
            with before.each:
                self.cascade.nodeFilter.selected = ["OoadClass", "Operation"]
                self.cascade.relationshipFilter.available(self.cascade.nodeFilter.selected)
                self.cascade.ruleFilter.available(self.cascade.nodeFilter.selected)

            with it("should fill available relationships from those nodes"):
                expect(self.cascade.relationshipFilter.choices).to(contain("invokes"))

            with it("should fill available rules from those nodes"):
                expect(self.cascade.ruleFilter.choices).to(
                    contain("keep-operations-small-focused")
                )

        with context("with a rule set"):
            with it("should offer base and project"):
                expect(self.cascade.ruleSetFilter.available).to(equal(["base", "project"]))

    with context("that tags an epic, sub-epic, or story"):
        with it("should tag them as stories and not as clean engineering or bdd"):
            expect(tagged_practice("Epic", "clean_engineering")).to(equal("stories"))
            expect(tagged_practice("SubEpic", "bdd")).to(equal("stories"))
            expect(tagged_practice("Story", "clean_engineering")).to(equal("stories"))
            expect(tagged_practice("OoadClass", "clean_engineering")).to(equal("clean_engineering"))
            epic = _node("Access Selfcare", "Epic", "clean_engineering")
            tests = _node("tests", "Package", "clean_engineering")
            tests.properties = {"folder": "tests"}
            retag_practice(epic)
            retag_practice(tests)
            expect(epic.practice).to(equal("stories"))
            expect(tests.practice).to(equal("stories"))
            included = _flatten(retained_tree([tests, epic], ["CleanEngineering"]))
            expect("tests" in [node.name for node in included]).to(equal(False))
            expect("Access Selfcare" in [node.name for node in included]).to(equal(False))

    with context("a story node"):
        with it("should leave tests, epics, sub-epics, and stories out of clean engineering"):
            epic = _node("Access Selfcare", "Epic", "clean_engineering")
            sub = _node("manage-services", "SubEpic", "clean_engineering")
            story = _node("onboard-a-customer", "Story", "clean_engineering")
            expect(is_story_node(epic)).to(equal(True))
            expect(is_story_node(sub)).to(equal(True))
            expect(is_story_node(story)).to(equal(True))
            tests = _node(
                "tests",
                "Package",
                "",
                [
                    _node(
                        "access-selfcare",
                        "Package",
                        "",
                        [epic, _node("examples", "Package", "")],
                    ),
                    _node(
                        "manage-billing",
                        "Package",
                        "",
                        [_node("Manage Billing", "Epic", "stories")],
                    ),
                    sub,
                    story,
                ],
            )
            expect(is_story_node(tests)).to(equal(True))
            included = _flatten(
                retained_tree(
                    [
                        _node(
                            "domain",
                            "Module",
                            "clean_engineering",
                            [_node("Customer", "OoadClass", "clean_engineering")],
                        ),
                        tests,
                    ],
                    ["CleanEngineering"],
                )
            )
            names = [node.name for node in included]
            expect(names).to(contain("domain"))
            expect(names).to(contain("Customer"))
            expect("tests" in names).to(equal(False))
            expect("access-selfcare" in names).to(equal(False))
            expect("examples" in names).to(equal(False))
            expect("manage-billing" in names).to(equal(False))
            expect("manage-services" in names).to(equal(False))
            expect("onboard-a-customer" in names).to(equal(False))
            kinds = [node.nodeType.name for node in included]
            expect("Epic" in kinds).to(equal(False))
            expect("SubEpic" in kinds).to(equal(False))
            expect("Story" in kinds).to(equal(False))

    with context("that selects clean engineering"):
        with it("should leave story nodes out of the folders and files"):
            included = _flatten(retained_tree(_mixed_practice_tree(), ["CleanEngineering"]))
            folders_and_files = [
                node for node in included if node.nodeType.name in {"Module", "Package", "File"}
            ]
            expect([node.name for node in folders_and_files]).to(equal(["domain", "customer.ts"]))
            for node in folders_and_files:
                expect(node.nodeType.name in _STORY_NODE_TYPES).to(equal(False))
            for node in included:
                expect(node.nodeType.name in _STORY_NODE_TYPES).to(equal(False))
                expect(node.nodeType.name in {"Description", "Context", "Observation", "BoundedContext"}).to(equal(False))
            names = [node.name for node in included]
            expect(names).to(contain("Customer"))
            expect(names).to(contain("submitFeedback"))
            expect("When they send a feedback note" in names).to(equal(False))
            expect("Onboard A Customer" in names).to(equal(False))
            expect("Select Plan" in names).to(equal(False))
            expect("Given a plan" in names).to(equal(False))
            expect("Customer is known" in names).to(equal(False))
            expect("Ordering" in names).to(equal(False))
            expect("select-plan.e2e.ts" in names).to(equal(False))

    with context("that selects domain driven design"):
        with it("should keep clean engineering folders and files and leave story nodes out"):
            included = _flatten(retained_tree(_mixed_practice_tree(), ["Ddd"]))
            names = [node.name for node in included]
            kinds = [node.nodeType.name for node in included]
            for node in included:
                expect(node.nodeType.name in _STORY_NODE_TYPES).to(equal(False))
                expect(node.nodeType.name in {"Description", "Context", "Observation"}).to(equal(False))
            expect(names).to(contain("domain"))
            expect(names).to(contain("Customer"))
            expect(names).to(contain("customer.ts"))
            expect(names).to(contain("submitFeedback"))
            expect(names).to(contain("Ordering"))
            expect(kinds).to(contain("OoadClass"))
            expect(kinds).to(contain("BoundedContext"))
            expect("Onboard A Customer" in names).to(equal(False))
            expect("When they send a feedback note" in names).to(equal(False))
            expect("Given a plan" in names).to(equal(False))
            expect("Customer is known" in names).to(equal(False))

    with context("that selects stories"):
        with it("should leave class folders and files out"):
            included = _flatten(retained_tree(_mixed_practice_tree(), ["Stories"]))
            names = [node.name for node in included]
            expect("domain" in names).to(equal(False))
            expect("Customer" in names).to(equal(False))
            expect("customer.ts" in names).to(equal(False))
            expect(names).to(contain("Select Plan"))
            expect(names).to(contain("When they send a feedback note"))
            expect("submitFeedback" in names).to(equal(False))
            expect("Ordering" in names).to(equal(False))
            expect("Customer is known" in names).to(equal(False))
            step = next(node for node in included if node.name == "When they send a feedback note")
            expect([link["name"] for link in step.relationships]).to(contain("submitFeedback"))
            for node in included:
                expect(node.practice == "clean_engineering").to(equal(False))
                expect(node.practice == "ddd").to(equal(False))
                expect(node.practice == "bdd").to(equal(False))

    with context("that selects behavior driven development"):
        with it("should leave story nodes and class folders out"):
            included = _flatten(retained_tree(_mixed_practice_tree(), ["Bdd"]))
            expect([node.name for node in included]).to(equal(["Customer is known"]))
            for node in included:
                expect(node.nodeType.name in _STORY_NODE_TYPES).to(equal(False))
                expect(node.nodeType.name in {"Module", "Package", "File", "OoadClass", "Operation", "BoundedContext"}).to(equal(False))

    with context("with a chosen node"):
        with it("should hold that node as selected"):
            node = KnowledgeGraphNode()
            node.name = "Story"
            self.graph.choose(node)
            expect(self.graph.selected).to(equal(node))

    with context("with open branches"):
        with it("should hold those nodes as expanded"):
            node = KnowledgeGraphNode()
            node.name = "Epic"
            self.graph.open(node)
            expect(self.graph.expanded).to(contain(node))

        with it("should start closed and restore only branches that were opened"):
            expect(self.graph.expanded).to(equal([]))
            present = ["practice:clean_engineering", "pkg:domain", "pkg:customer"]
            expect(restored_branches([], present)).to(equal([]))
            expect(restored_branches(["pkg:domain"], present)).to(equal(["pkg:domain"]))
            expect(restored_branches(["pkg:domain", "missing"], present)).to(equal(["pkg:domain"]))

        with it("should create the database from scratch and say extraction is in progress"):
            expect(database_build_required("create-database", True)).to(equal(True))
            expect(database_graph_from_scratch("create-database")).to(equal(True))
            expect(database_graph_from_scratch("refresh-master")).to(equal(False))
            expect(extraction_progress("Create database", "working", 4)).to(
                equal("Database extraction in progress… 4s")
            )
            catalog = rules_from_guidance()
            stories = rules_for_filters(catalog, ["stories"], None, None)
            operations = rules_for_filters(
                catalog, ["clean_engineering"], ["implementation"], ["Operation"]
            )
            expect(len(catalog) > 100).to(equal(True))
            expect("honor-every-rule-in-the-artifact" in stories).to(equal(False))
            expect(operations).to(contain("keep-operations-small-focused"))
            expect("verb-noun-format" in operations).to(equal(False))
            expect(database_build_required("refresh-master", True)).to(equal(True))
            expect(database_build_required("reload-working-copy", True)).to(equal(True))


with description("a practice tree"):
    with it("should root each practice that is not filtered out"):
        expect(practice_root_labels(["clean_engineering"])).to(equal(["Clean Engineering"]))
        expect(practice_root_labels(["stories"])).to(equal(["Stories"]))
        expect(practice_root_labels(["ddd"])).to(equal(["Domain Driven Design"]))
        expect(practice_root_labels(["bdd"])).to(equal(["BDD"]))
        expect(practice_root_labels([])).to(
            equal(["Clean Engineering", "Stories", "Domain Driven Design", "BDD"])
        )


with description("a source panel"):
    with it("should shrink when a fold is closed and grow when that fold opens"):
        folds = [KnowledgeGraphSourceFold(2, 10, "operation")]
        expect(editor_height(12, folds, [])).to(equal(60))
        expect(editor_height(12, folds, [2])).to(equal(240))


with description("a scenario step"):
    with it("should list the fixture examples and the domain operation the test calls"):
        members = step_members(
            "subscriber.feedbackSubject = feedbackSubjectExample\n"
            "subscriber.feedbackMessage = feedbackMessageExample\n"
            "receipt = await subscriber.submitFeedback()"
        )
        expect(members["operations"]).to(equal(["submitFeedback"]))
        expect(members["examples"]).to(equal(["feedbackSubjectExample", "feedbackMessageExample"]))
        text = (
            "subscriber.feedbackSubject = feedbackSubjectExample\n"
            "subscriber.feedbackMessage = feedbackMessageExample\n"
            "receipt = await subscriber.submitFeedback()"
        )
        layout = step_callouts(
            text,
            [
                {"name": "feedbackSubjectExample", "text": "feedbackSubjectExample"},
                {"name": "feedbackMessageExample", "text": "feedbackMessageExample"},
                {"name": "submitFeedback", "text": "submitFeedback()"},
            ],
        )
        expect([fold["kind"] for fold in layout["folds"]]).to(equal(["call", "call", "call"]))
        expect("    feedbackSubjectExample" in layout["text"]).to(equal(True))
        expect("    submitFeedback()" in layout["text"]).to(equal(True))

    with it("should keep the operation a step invokes under that step"):
        operation = _node("submitFeedback", "Operation", "clean_engineering")
        example = _node("feedbackSubjectExample", "Example", "stories")
        step = _node("When they send a feedback note", "Step", "stories", [operation, example])
        step.relationships = [
            {"kind": "invokes", "nodeId": operation.nodeId, "name": operation.name},
            {"kind": "demonstrates", "nodeId": example.nodeId, "name": example.name},
        ]
        included = _flatten(retained_tree([step], ["Stories"]))
        names = [node.name for node in included]
        expect(names).to(contain("submitFeedback"))
        expect(names).to(contain("feedbackSubjectExample"))
        engineering = [node.name for node in _flatten(retained_tree([step], ["CleanEngineering"]))]
        expect("When they send a feedback note" in engineering).to(equal(False))


with description("an operation"):
    with context("that has source"):
        with before.each:
            self.source = KnowledgeGraphCallSource(
                "placeOrder()\nCart.addItem()",
                "Cart.ts",
                1,
                2,
                "typescript",
            )
            self.source.source()

        with it("should load each call at its line and order"):
            expect([(call.line, call.sequentialOrder, call.operation) for call in self.source.calls]).to(
                equal([(1, 1, "placeOrder"), (2, 1, "Cart.addItem")])
            )

        with it("should insert those calls into the text"):
            expect(self.source.text).to(contain("call:placeOrder"))

        with it("should fold each inserted call"):
            expect([fold.kind for fold in self.source.folds]).to(equal(["class", "call"]))

    with context("that calls another class's operation"):
        with it("should use the call glyph"):
            source = KnowledgeGraphCallSource("Cart.addItem()", "Order.ts", 1, 1, "typescript")
            source.source()
            expect(source.folds[0].kind).to(equal("call"))


with description("a property"):
    with context("that has source"):
        with it("behaves like an operation that has source"):
            source = KnowledgeGraphCallSource("total()\n", "Cart.ts", 1, 1, "typescript")
            source.source()
            expect(source.calls[0].operation).to(equal("total"))
