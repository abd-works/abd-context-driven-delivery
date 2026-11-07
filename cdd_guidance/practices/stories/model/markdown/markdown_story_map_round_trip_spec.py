"""Mamba spec: a story map written as story-map.md reads back as the same map.

The outline holds epics, stories, their kind, and their actors; each story's scenarios read from its own story file."""

import tempfile
from pathlib import Path

from expects import equal, expect, raise_error
from mamba import before, context, description, it

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
