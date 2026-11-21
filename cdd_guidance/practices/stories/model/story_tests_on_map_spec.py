"""Story tests in code read together with the story map that holds their stories: each story of the map takes the
scenarios every one of its story tests holds, each step keeps the code its story test gives it, and each example the
story test uses is in the graph."""

import tempfile

from expects import contain, equal, expect, have_key
from mamba import before, context, description, it

from harness.graph.graph import Graph
from harness.graph.rule_context import RuleCheckContext
from harness.graph.rule_fixture import SchemaRuleRun

from cdd_guidance.practices.stories.model.fixtures.bookshop_project import PRACTICES, WHOLE_PROJECT, BookshopProject
from cdd_guidance.practices.stories.model.story_tree import StoryTree
from cdd_guidance.practices.stories.rules import BY_SLUG

_PACK_ORDER = "story_tests/fulfil-order/pack-order/pack_order_story.test.py"
_SHARED_CANCEL = "story_tests/check-out/confirm-order/confirm-order.story.shared.ts"
_PYTHON_ORDER = "src/bookshop/order.py"
_VIEW_CONFIRMATION = "story_tests/check-out/confirm-order/view-order-confirmation/view_order_confirmation_story.test.ts"


with description("a story map read into the graph with the story tests in code of its stories") as self:
    with before.all:
        self.project = BookshopProject()
        self.tree = StoryTree(self.project.graph.practices.named("stories").reading)
        self.map_story = lambda name: self.project.node_named("Story", name, ".context/story-map.md")[0]

    with context("with a Python story test whose When calls the operation it tests"):
        with it("should link the When to the operation its body calls"):
            when = self.project.node_named("When", "when the Shop Clerk packs the Order", _PACK_ORDER)[0]
            expect([child for parent, child in self.project.edges("invokes") if parent == when.node_id]).to(
                contain(f"clean_engineering:Operation:{_PYTHON_ORDER}:pack:Order")
            )

        with it("should hold each example the story test imports"):
            expect(sorted(node.name for node in self.project.stories.nodes("Example") if node.source.file == _PACK_ORDER)).to(
                equal(["paid_order", "unpaid_order"])
            )

        with it("should give each step the modules its own story test imports"):
            when = self.project.node_named("When", "when the Shop Clerk packs the Order", _PACK_ORDER)[0]
            expect(when.get_fact("imported_modules")).to(have_key("OrderRepository", "src/bookshop/order"))

    with context("with code that holds an operation of one name in Python, in TypeScript, and in a second Python module"):
        with it("should link a Python step only to the operations of the module its story test imports"):
            invoked = [child for parent, child in self.project.edges("invokes") if f":{_PACK_ORDER}:" in parent]
            expect(sorted({child.split(":")[2] for child in invoked})).to(equal([_PYTHON_ORDER]))

        with it("should link a TypeScript step only to the operations of the module its story test imports"):
            invoked = [child for parent, child in self.project.edges("invokes") if f":{_VIEW_CONFIRMATION}:" in parent]
            expect(sorted({child.split(":")[2] for child in invoked})).to(equal(["src/bookshop/order.ts"]))

    with context("with a story whose scenarios are written in two story files"):
        with it("should give the story the scenarios of both files"):
            expect([scenario.name for scenario in self.tree.scenarios(self.map_story("Cancel Order"))]).to(
                contain("Cancel a submitted order", "Keep the total of a cancelled order")
            )

        with it("should keep each scenario in the file that writes it"):
            expect([node.source.file for node in self.project.node_named("Scenario", "Keep the total of a cancelled order")]).to(equal([_SHARED_CANCEL]))

    with context("with stories the map holds"):
        with it("should hold each story once, as the map names it"):
            expect([node.source.file for node in self.project.stories.nodes("Story") if node.name in {"Pack Order", "Cancel Order"}]).to(
                equal([".context/story-map.md", ".context/story-map.md"])
            )


_SUBMIT_ORDER = "story_tests/check-out/place-order/submit-order/submit_order_story.test.py"
_SUBMIT_ORDER_ENTRY = "### (S) Customer --> Submit Order\n\nThe Cart becomes an Order the moment the Customer submits it.\n"


def _without_submit_order() -> BookshopProject:
    """The Bookshop project with the story Submit Order taken off its story map, its story test left where it is, and
    loaded again."""
    project = BookshopProject((".context/story-map.md",), ("stories",))
    story_map = project.root / ".context" / "story-map.md"
    story_map.write_text(story_map.read_text(encoding="utf-8").replace(_SUBMIT_ORDER_ENTRY, ""), encoding="utf-8")
    project.graph.load_files(str(project.root), list(PRACTICES), list(WHOLE_PROJECT))
    return project


with description("a story test in code whose story the story map does not hold") as self:
    with before.all:
        self.project = _without_submit_order()
        self.tree = StoryTree(self.project.graph.practices.named("stories").reading)
        self.off_map = self.project.node_named("Story", "Submit Order")

    with it("should keep the story, read from its story test"):
        expect([story.source.file for story in self.off_map]).to(equal([_SUBMIT_ORDER]))

    with it("should keep the story's scenarios under it"):
        expect([scenario.name for story in self.off_map for scenario in self.tree.scenarios(story)]).to(
            equal(["Submit a cart with one book", "Refuse an empty cart"])
        )

    with it("should place the story under the epic its story test's folders name"):
        expect([self.tree.epic_of(story).name for story in self.off_map]).to(equal(["Check Out"]))

    with it("should report the story as not on the story map, naming its story test"):
        expect(SchemaRuleRun(BY_SLUG["scenarios-name-a-story-on-the-map"], RuleCheckContext(self.project.graph.practices.named("stories"))).hits()).to(
            equal([
                f"Story 'Submit Order' has scenarios in {_SUBMIT_ORDER} and is not on the story map; add it to the map or name the story the scenarios belong to."
            ])
        )

    with context("that sits in a folder a story test in another language also names its epic by"):
        with it("should keep every other story of the map where the map has it"):
            expect([node.source.file for node in self.project.stories.nodes("Story") if node.name != "Submit Order"]).to(equal([".context/story-map.md"] * 15))


def _whole_working_copy() -> tuple[BookshopProject, Graph]:
    """The Bookshop project, and a graph that loaded its whole working copy with every practice rooted at the project."""
    project = BookshopProject((".context/story-map.md",), ("stories",))
    graph = Graph()
    graph.load_working_copy(str(project.root), {key: "." for key in PRACTICES}, database=tempfile.mkdtemp(prefix="bookshop-graph-"), force=True)
    return project, graph


with description("the whole working copy of a project with a story map, scenarios in markdown, and story tests in code") as self:
    with before.all:
        self.project, self.graph = _whole_working_copy()
        self.files_load = BookshopProject()
        self.stories = self.graph.practices.named("stories").reading.in_graph

    with it("should hold the scenarios the load of the same files holds, those written in code among them"):
        expect(sorted(node.node_id for node in self.stories.nodes("Scenario"))).to(
            equal(sorted(node.node_id for node in self.files_load.stories.nodes("Scenario")))
        )

    with it("should link the steps of the story tests in code to the operations they call"):
        expect(sorted((edge.parent.node_id, edge.child.node_id) for edge in self.stories.edge_index.of("invokes"))).to(equal(self.files_load.edges("invokes")))


_ADD_BOOK = "story_tests/fill-cart/add-books/add_book_to_cart_story.test.md"


with description("where the graph places the nodes of a story map's story files") as self:
    with before.all:
        self.project = BookshopProject()

    with context("with a step whose text a Python story test writes with escaped quotes"):
        with it("should place the step on the line that writes it"):
            step = self.project.node_named("Then", 'then the Bookshop refuses with "order 1002 is not paid"', _PACK_ORDER)[0]
            expect(step.source.start_line).to(equal(31))

    with context("with a step whose text a TypeScript story test writes with escaped quotes"):
        with it("should place the step on the line that writes it"):
            step = self.project.node_named("Then", 'then the Bookshop refuses with "order 9999 is not found"', _VIEW_CONFIRMATION)[0]
            expect(step.source.start_line).to(equal(42))

    with context("with examples a markdown scenarios file declares in a table"):
        with it("should place each example on its row of the table"):
            placed = {node.name: node.source.start_line for node in self.project.stories.nodes("Example") if node.source.file == _ADD_BOOK}
            expect(placed).to(equal({"Tiny Tales": 25, "Grand Atlas": 26, "empty cart": 32, "cart with Tiny Tales": 33}))
