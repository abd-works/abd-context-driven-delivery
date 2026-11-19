"""Mamba spec: a story map written as story-map.md reads back as the same map.

The outline holds epics, stories, their kind, and their actors; each story's scenarios read from its own story file."""

import tempfile
from pathlib import Path

from expects import equal, expect, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownParseError, MarkdownStoryModel


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
