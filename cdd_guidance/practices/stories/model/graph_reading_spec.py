"""How Stories reads a story map and its scenarios files into its graph."""

from expects import equal, expect
from mamba import before, context, description, it

from harness.graph.rule_fixture import RuleFixture

from cdd_guidance.practices.stories.model.fixtures.bookshop_project import BookshopProject
from cdd_guidance.practices.stories.model.story_tree import StoryTree
from cdd_guidance.practices.stories.rules import BY_SLUG
from cdd_guidance.practices.stories.stories import Stories

_STORY_MAP = "# (E) Sell Books\n## (E) Take Orders\n### (S) Customer --> Place Order\n### (S) Customer --> Cancel Order\n"

_SCENARIOS_FILE = "story_tests/sell-books/take-orders/take_orders_story.test.md"


def _scenarios_of(first_story: str, second_story: str) -> str:
    """A scenarios file of the Take Orders sub-epic that specifies two stories, one scenario each."""
    return (
        "# Sub-epic: Take Orders\n\n"
        f"## Story: {first_story}\n\n"
        "#### Scenario: Order one book\n\n"
        "*Given* a Customer with an empty basket\n"
        "*When* the Customer places an order for one book\n"
        "*Then* the order holds one line\n\n"
        f"## Story: {second_story}\n\n"
        "#### Scenario: Cancel an open order\n\n"
        "*Given* a Customer with an open order\n"
        "*When* the Customer cancels the order\n"
        "*Then* the order is cancelled\n"
    )


def _read(first_story: str, second_story: str):
    """The Stories graph of a folder holding the story map and one scenarios file naming the two stories."""
    fixture = RuleFixture(Stories, {"story-map.md": _STORY_MAP, _SCENARIOS_FILE: _scenarios_of(first_story, second_story)})
    return fixture, fixture.practice.reading.in_graph


with description("a story map read into the graph with a scenarios file beside it") as self:
    with context("with a scenarios file that specifies the stories the map holds"):
        with before.all:
            self.fixture, self.read = _read("Place Order", "Cancel Order")

        with it("should give each story of the map its scenarios"):
            expect([node.name for node in self.read.nodes("Scenario")]).to(equal(["Order one book", "Cancel an open order"]))

        with it("should report no story as missing from the map"):
            expect(self.fixture.hits(BY_SLUG["scenarios-name-a-story-on-the-map"])).to(equal([]))

        with it("should keep no story as one the map does not hold"):
            expect([node.name for node in self.read.nodes("Story") if node.get_fact("not_on_story_map")]).to(equal([]))

    with context("with a scenarios file that specifies stories the map does not hold"):
        with before.all:
            self.fixture, self.read = _read("Gift Order", "Wrap Order")
            self.unplaced = [node for node in self.read.nodes("Story") if node.get_fact("not_on_story_map")]

        with it("should keep each of those stories, after the stories of the map"):
            expect([node.name for node in self.read.nodes("Story")]).to(equal(["Place Order", "Cancel Order", "Gift Order", "Wrap Order"]))

        with it("should keep their scenarios under them"):
            tree = StoryTree(self.fixture.practice.reading)
            expect([scenario.name for story in self.unplaced for scenario in tree.scenarios(story)]).to(
                equal(["Order one book", "Cancel an open order"])
            )

        with it("should place them under no epic"):
            tree = StoryTree(self.fixture.practice.reading)
            expect([tree.epic_of(story) for story in self.unplaced]).to(equal([None, None]))

        with it("should name the scenarios file as where each was read"):
            expect({story.source.file for story in self.unplaced}).to(equal({_SCENARIOS_FILE}))

        with it("should report each story the map does not hold, naming its scenarios file"):
            expect(self.fixture.hits(BY_SLUG["scenarios-name-a-story-on-the-map"])).to(equal([
                f"Story 'Gift Order' has scenarios in {_SCENARIOS_FILE} and is not on the story map; add it to the map or name the story the scenarios belong to.",
                f"Story 'Wrap Order' has scenarios in {_SCENARIOS_FILE} and is not on the story map; add it to the map or name the story the scenarios belong to.",
            ]))

        # Hardening regression run (graph_incremental_heavy_spec): a refresh of a scenarios file read the map's epics
        # again and left out the stories the map does not hold, so their scenarios and steps were gone until a full load.
        with context("that is refreshed with the scenarios file"):
            with before.all:
                self.fixture.practice.reading.graph.refresh([_SCENARIOS_FILE])

            with it("should still keep each of those stories, after the stories of the map"):
                expect([node.name for node in self.read.nodes("Story")]).to(equal(["Place Order", "Cancel Order", "Gift Order", "Wrap Order"]))


_ADD_BOOK = "story_tests/fill-cart/add-books/add_book_to_cart_story.test.md"


with description("a story map read into the graph with two scenarios files, one with a Background and one without") as self:
    with before.all:
        self.project = BookshopProject((".context/story-map.md", "story_tests/fill-cart"), ("stories",))
        self.backgrounds = self.project.stories.nodes("Background")

    with it("should hold one Background, in the scenarios file that writes it"):
        expect([node.source.file for node in self.backgrounds]).to(equal([_ADD_BOOK]))

    with it("should place the Background where its steps begin, since its reader names no line for its heading"):
        expect(self.backgrounds[0].source.start_line).to(equal(37))

    with it("should give the Background only to the story whose scenarios file writes it"):
        expect([parent for parent, _child in self.project.edges("background")]).to(equal(["stories:Story:.context/story-map.md:Add Book To Cart"]))

    with it("should give the Background its Given step"):
        given = [edge.child for edge in self.project.graph.edges.from_parent("given", self.backgrounds[0])]
        expect([(step.type, step.source.start_line) for step in given]).to(equal([("Given", 37)]))

    with it("should chain the Given's And onto it"):
        given = self.project.graph.edges.from_parent("given", self.backgrounds[0])[0].child
        expect([edge.child.source.start_line for edge in self.project.graph.edges.from_parent("ands", given)]).to(equal([38]))


with description("the steps and examples of a story map read into the graph") as self:
    with before.all:
        self.fixture, self.read = _read("Place Order", "Cancel Order")
        self.reading = self.fixture.practice.reading

    with it("should name each step a file view shows the calls of"):
        expect(len(self.reading.steps())).to(equal(6))

    with it("should take an example as used from where the story declares it"):
        example = type("Node", (), {"type": "Example"})()
        expect(self.reading.is_used_from_elsewhere(example)).to(equal(True))

    with it("should take a scenario as part of the story above it"):
        expect(self.reading.is_used_from_elsewhere(self.read.nodes("Scenario")[0])).to(equal(False))
