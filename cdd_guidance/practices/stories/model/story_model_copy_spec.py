"""Mamba spec: a story map copied into another format's model keeps what a clone keeps."""

from expects import equal, expect
from mamba import before, description, it

from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.json.nodes import JsonStoryModel


with description("a story map copied into another format's model") as self:
    with before.each:
        self.story_map = round_trip_story_map()
        self.story_map.examples["open account"] = {"balance": "120"}
        self.story_map.epics[0].examples["due bill"] = {"amount": "40"}
        self.copied = JsonStoryModel(self.story_map)

    with it("should keep every epic, story, background, and scenario"):
        expect(outline(self.copied)).to(equal(outline(self.story_map)))

    with it("should keep the examples an epic shares"):
        expect(self.copied.epics[0].examples["due bill"].cells()).to(equal({"amount": "40"}))

    with it("should keep the examples the story map shares"):
        expect(self.copied.examples["open account"].cells()).to(equal({"balance": "120"}))

    with it("should keep the same examples as a clone of the story map"):
        expect(sorted(self.copied.examples)).to(equal(sorted(self.story_map.clone().examples)))
