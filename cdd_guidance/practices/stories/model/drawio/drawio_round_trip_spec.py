"""Mamba spec: a story map drawn in draw.io reads back as the same map.

A draw.io story map holds epics, stories, their kind, and their actors; scenarios live in the story files."""

from expects import be_a, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel, StoryType


def _nested_four_levels() -> StoryModel:
    """A top-level epic with sub-epics nested three deep, each epic holding one story with its own actor."""
    story_map = StoryModel()
    holder = Epic("Top", 1)
    story_map.append_epic(holder)
    for level, name in enumerate(["Top", "Level One", "Level Two", "Level Three"]):
        if level:
            child = Epic(name, 1)
            holder.append_epic(child)
            holder = child
        story = Story(f"{name} Story", 1, StoryType.USER)
        story.actors = [f"Actor {level}"]
        holder.append_story(story)
    return story_map


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

    with context("that nests sub-epics four levels deep"):
        with before.each:
            self.nested = _nested_four_levels()
            self.nested_read = DrawIOStoryModel().load(DrawIOStoryModel().render(self.nested))

        with it("should draw the actor above the story of the deepest sub-epic"):
            expect('value="Actor 3"' in DrawIOStoryModel().render(self.nested)).to(equal(True))

        with it("should read back every level's epic, story, and actor"):
            expect(outline(self.nested_read, with_scenarios=False)).to(equal(outline(self.nested, with_scenarios=False)))
