"""Mamba spec: a story map drawn in draw.io reads back as the same map.

A draw.io story map holds epics, stories, their kind, and their actors; scenarios live in the story files."""

from expects import be_a, equal, expect
from mamba import before, description, it

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map


with description("a story map drawn in draw.io") as self:
    with before.each:
        self.story_map = round_trip_story_map()
        self.drawing = DrawIOStoryModel().render(self.story_map)
        self.read = DrawIOStoryModel().load(self.drawing)

    with it("should draw each story with its own kind"):
        expect('style="story:system;' in self.drawing).to(equal(True))

    with it("should read back every epic, story held by any epic, kind, and actor"):
        expect(outline(self.read, with_scenarios=False)).to(equal(outline(self.story_map, with_scenarios=False)))

    with it("should copy itself as a draw.io story map"):
        expect(self.read.clone()).to(be_a(DrawIOStoryModel))
