"""A refresh of Stories files nobody changed: the graph holds after it what it held before, whichever of the story map,
one story test, or the story tests' folder the refresh names."""

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.bookshop_project import BookshopProject

_PACK_ORDER = "story_tests/fulfil-order/pack-order/pack_order_story.test.py"


def _refreshed(paths: list[str]):
    """What the graph of the whole Bookshop project held before a refresh of paths, and what it holds after."""
    project = BookshopProject()
    before_refresh = project.held()
    project.graph.refresh(paths)
    return before_refresh, project.held()


with description("a graph that holds a story map with its scenarios and story tests") as self:
    with context("that is refreshed with the story map, which nobody changed"):
        with before.all:
            self.held_before, self.held_after = _refreshed([".context/story-map.md"])

        with it("should hold the nodes it held"):
            expect(self.held_after[0] ^ self.held_before[0]).to(equal(set()))

        with it("should keep each story's scenarios on it"):
            expect(self.held_after[1] ^ self.held_before[1]).to(equal(set()))

    with context("that is refreshed with one story test in code, which nobody changed"):
        with before.all:
            self.held_before, self.held_after = _refreshed([_PACK_ORDER])

        with it("should hold the story and its epic once, as the map names them"):
            expect(self.held_after[0] ^ self.held_before[0]).to(equal(set()))

        with it("should hold the edges it held"):
            expect(self.held_after[1] ^ self.held_before[1]).to(equal(set()))

    with context("that is refreshed with the folder of its story tests, which nobody changed"):
        with before.all:
            self.held_before, self.held_after = _refreshed(["story_tests"])

        with it("should keep the scenarios written in markdown and those written in code"):
            expect(self.held_after[0] ^ self.held_before[0]).to(equal(set()))

        with it("should hold the edges it held"):
            expect(self.held_after[1] ^ self.held_before[1]).to(equal(set()))
