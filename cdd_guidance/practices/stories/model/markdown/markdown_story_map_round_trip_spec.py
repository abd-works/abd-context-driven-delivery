"""Mamba spec: a story map written as story-map.md reads back as the same map.

The outline holds epics, stories, their kind, and their actors; each story's scenarios read from its own story file."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownParseError, MarkdownStoryModel
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryModel


with description("a story map saved as story-map.md") as self:
    with before.each:
        self.story_map = round_trip_story_map()
        self.read = MarkdownStoryModel().parse(MarkdownStoryModel().render(self.story_map))

    with it("should read back every epic, story held by any epic, kind, and actor"):
        expect(outline(self.read, with_scenarios=False)).to(equal(outline(self.story_map, with_scenarios=False)))

    with context("that has no story map structure on disk"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp())
            (self.folder / "story-map.md").write_text("plain prose with no headings\n", encoding="utf-8")

        with it("should fail naming the file rather than read as no story map"):
            expect(lambda: MarkdownStoryModel.from_workspace(self.folder)).to(raise_error(MarkdownParseError))


_BOOKSHOP_MAP = (
    "# Story Map — Bookshop\n"
    "\n"
    "# (E) Sell Books\n"
    "\n"
    "## (E) Take Orders\n"
    "\n"
    "### (S) Customer --> Place Order\n"
    "### (S) Customer --> Cancel Order\n"
)


with description("a story map a person wrote in story-map.md, drawn in draw.io and written back over that file") as self:
    with before.each:
        drawn = DrawIOStoryModel().render(MarkdownStoryModel().parse(_BOOKSHOP_MAP))
        self.back = MarkdownStoryModel().render(DrawIOStoryModel().load(drawn), previous=_BOOKSHOP_MAP)

    with it("should keep the title the person wrote above the first epic"):
        expect(self.back.splitlines()[0]).to(equal("# Story Map — Bookshop"))

    with it("should add no sources or scope the person did not write"):
        expect([line for line in self.back.splitlines() if line.startswith(("**", "---", "## Scope"))]).to(equal([]))

    with it("should bring back every epic, sub-epic, and story with its actor"):
        expect([line for line in self.back.splitlines() if "(E)" in line or "(S)" in line]).to(
            equal([line for line in _BOOKSHOP_MAP.splitlines() if "(E)" in line or "(S)" in line])
        )


_DESCRIBED_MAP = (
    "# Story Map — Bookshop\n"
    "\n"
    "**Sources:** the bookshop brief\n"
    "\n"
    "# (E) Fill Cart\n"
    "\n"
    "A Customer gathers the Books to buy.\n"
    "\n"
    "## (E) Add Books\n"
    "\n"
    "Each Book goes into the Cart as a Cart Line.\n"
    "\n"
    "### (S) Customer --> [Add Book To Cart](../story_tests/fill-cart/add-books/add_book_to_cart_story.test.md)\n"
    "### (S:system) Cart --> Total Cart\n"
    "\n"
    "# (E) Check Out\n"
    "\n"
    "## (E) Place Order\n"
    "\n"
    "### (S) Customer --> Submit Order\n"
    "\n"
    "The Order is taken once the Cart holds a Cart Line.\n"
    "\n"
    "---\n"
    "\n"
    "## Scope boundary\n"
    "\n"
    "**In scope:** carts and orders\n"
    "**Out of scope:** payment\n"
)


def _back_through(diagram) -> str:
    """The described map drawn by diagram, a diagram format's story model, and written back over its own file."""
    drawn = diagram().render(MarkdownStoryModel().parse(_DESCRIBED_MAP))
    return MarkdownStoryModel().render(diagram().load(drawn), previous=_DESCRIBED_MAP)


with description("a story map with descriptions, a story linked to its scenarios file, and a scope boundary") as self:
    with context("that is drawn in draw.io and written back over its file by nobody who edited the drawing"):
        with it("should come back as the person wrote it"):
            expect(_back_through(DrawIOStoryModel)).to(equal(_DESCRIBED_MAP))

    with context("that is drawn on a whiteboard and written back over its file by nobody who edited the board"):
        with it("should come back as the person wrote it"):
            expect(_back_through(WhiteboardStoryModel)).to(equal(_DESCRIBED_MAP))

    with context("that has a story added in the drawing before it is written back"):
        with before.each:
            drawn = DrawIOStoryModel().load(DrawIOStoryModel().render(MarkdownStoryModel().parse(_DESCRIBED_MAP)))
            drawn.epics[0].epics[0].stories.append(type(drawn.epics[0].epics[0].stories[0])("Remove Book From Cart", 3))
            self.back = MarkdownStoryModel().render(drawn, previous=_DESCRIBED_MAP)

        with it("should write the added story under its sub-epic"):
            expect(self.back).to(contain("### (S) --> Remove Book From Cart\n"))

        with it("should keep the description the person wrote under the sub-epic"):
            expect(self.back).to(contain("Each Book goes into the Cart as a Cart Line.\n"))
