"""Mamba spec: a story map drawn for a Miro board reads back as the same map.

A Miro story map holds epics, stories, their kind, and their actors; scenarios live in the story files."""

from expects import be_a, contain, equal, expect
from mamba import before, description, it

from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.miro.nodes import MiroIncrement, MiroStoryModel


with description("a story map drawn for a Miro board") as self:
    with before.each:
        self.story_map = MiroStoryModel(round_trip_story_map())
        self.read = MiroStoryModel().load(self.story_map.save())

    with it("should read back every epic, story held by any epic, kind, and actor"):
        expect(outline(self.read, with_scenarios=False)).to(equal(outline(self.story_map, with_scenarios=False)))

    with it("should copy itself as a Miro story map"):
        expect(self.read.clone()).to(be_a(MiroStoryModel))

    with it("should head a nested epic's thin-slice column with a plain ellipsis"):
        self.story_map.epics[0].epics[0].append_epic(type(self.story_map.epics[0])("Confirm Payment", 1))
        self.story_map.append_increment(MiroIncrement("First slice", 1))
        expect(MiroIncrement.save(self.story_map)).to(contain("Pay Bills / … / Confirm Payment"))
