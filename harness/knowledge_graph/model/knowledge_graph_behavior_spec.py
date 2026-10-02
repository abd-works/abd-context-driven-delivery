from pathlib import Path
from tempfile import TemporaryDirectory

from expects import contain, equal, expect
from mamba import before, context, description, it

from harness.knowledge_graph.model.knowledge_graph import KnowledgeGraph
from harness.knowledge_graph.model.knowledge_graph_node import (
    KnowledgeGraphCallSource,
    KnowledgeGraphFilter,
    KnowledgeGraphNode,
    KnowledgeGraphSourceFold,
    editor_height,
    practice_root_labels,
    step_members,
)
from practices.stories.model.story_model import Epic, StoryModel


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

    with context("that has refreshed the master"):
        with it("should be the document that was just saved"):
            self.graph.saveKnowledgeGraph()
            self.graph.refreshMaster()
            expect((Path(self.temp.name) / "story-map.kg").read_text(encoding="utf-8")).to(
                contain("Onboard")
            )

    with context("that has reloaded the working copy"):
        with it("should be the document that was just saved"):
            self.graph.saveKnowledgeGraph()
            self.graph.reloadWorkingCopy()
            expect((Path(self.temp.name) / "story-map.kg").read_text(encoding="utf-8")).to(
                contain("Onboard")
            )

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

    with context("that selects clean engineering"):
        with it("should leave stories and domain driven design out of the class model"):
            cascade = KnowledgeGraphFilter(["CleanEngineering"])
            expect(cascade.nodeFilter.choices).to(contain("OoadClass"))
            expect(cascade.nodeFilter.choices).not_to(contain("Story"))
            expect(cascade.nodeFilter.choices).not_to(contain("BoundedContext"))
            expect(cascade.nodeFilter.choices).not_to(contain("Description"))

    with context("that selects domain driven design"):
        with it("should include clean engineering plus domain driven design stereotypes"):
            cascade = KnowledgeGraphFilter(["Ddd"])
            expect(cascade.nodeFilter.choices).to(contain("BoundedContext"))
            expect(cascade.nodeFilter.choices).to(contain("OoadClass"))
            expect(cascade.nodeFilter.choices).to(contain("Module"))
            expect(cascade.nodeFilter.choices).not_to(contain("Story"))
            expect(cascade.nodeFilter.choices).not_to(contain("Description"))

    with context("that selects behavior driven development"):
        with it("should leave stories and clean engineering out"):
            cascade = KnowledgeGraphFilter(["Bdd"])
            expect(cascade.nodeFilter.choices).to(contain("Observation"))
            expect(cascade.nodeFilter.choices).not_to(contain("Story"))
            expect(cascade.nodeFilter.choices).not_to(contain("OoadClass"))


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
