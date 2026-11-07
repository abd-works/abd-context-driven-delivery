"""Mamba spec: a story map written to story-graph.json reads back as the same map."""

import tempfile
from pathlib import Path

from expects import equal, expect, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.json.nodes import JsonParseError, JsonStoryModel
from cdd_guidance.practices.stories.model.story_model import StoryModel


with description("a story map saved as story-graph.json") as self:
    with before.each:
        self.story_map = round_trip_story_map()
        self.story_map.examples["open account"] = {"balance": "120"}
        self.story_map.epics[0].examples["due bill"] = {"amount": "40"}
        self.read = JsonStoryModel().parse(JsonStoryModel().render(self.story_map))

    with it("should read back every epic, story, kind, actor, background step, and scenario step"):
        expect(outline(self.read)).to(equal(outline(self.story_map)))

    with it("should read back the examples an epic shares"):
        expect(self.read.epics[0].examples["due bill"].cells()).to(equal({"amount": "40"}))

    with it("should read back the examples the story map shares"):
        expect(self.read.examples["open account"].cells()).to(equal({"balance": "120"}))

    with context("that is corrupt on disk"):
        with before.each:
            self.folder = Path(tempfile.mkdtemp())
            (self.folder / "story-graph.json").write_text("{not json", encoding="utf-8")

        with it("should fail naming the file rather than read as no story map"):
            expect(lambda: JsonStoryModel.from_workspace(self.folder)).to(raise_error(JsonParseError))

    with context("that a folder does not hold"):
        with it("should read as no story map"):
            expect(JsonStoryModel.from_workspace(Path(tempfile.mkdtemp()))).to(equal(None))
