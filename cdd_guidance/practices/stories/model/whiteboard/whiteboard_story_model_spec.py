"""Mamba spec: a story map drawn on a Claude Whiteboard reads back as the same map.

A whiteboard story map holds epics, stories, their kind, and their actors; scenarios live in the story files, as they
do for drawio and miro."""

from expects import be_a, be_below, equal, expect, raise_error
from mamba import before, context, description, it

from harness.whiteboard import UnreadableBoard, Whiteboard
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryModel


def drawn(story_map: WhiteboardStoryModel, prefix: str) -> list:
    return [element for element in story_map.board().elements if element.id.startswith(prefix)]


with description("a story map drawn on a Claude whiteboard") as self:
    with before.each:
        self.story_map = WhiteboardStoryModel(round_trip_story_map())
        self.read = WhiteboardStoryModel().load(self.story_map.save())

    with it("should read back every epic, story held by any epic, kind, and actor"):
        expect(outline(self.read, with_scenarios=False)).to(equal(outline(self.story_map, with_scenarios=False)))

    with it("should copy itself as a whiteboard story map"):
        expect(self.read.clone()).to(be_a(WhiteboardStoryModel))

    with context("with a story under a sub-epic"):
        with before.each:
            self.sub_epic = self.story_map.epics[0].epics[0]
            self.story = self.sub_epic.stories[0]
            self.card = self.story_map.board().element(self.story.board_elements()[-1].id)
            self.bar = self.story_map.board().element(self.sub_epic.board_elements()[0].id)

        with it("should draw the story as a card below its sub-epic's bar"):
            expect(self.bar.y + self.bar.h).to(be_below(self.card.y))

        with it("should draw the story's actor above the card"):
            actor = self.story.board_elements()[0]
            expect((actor.text, actor.y + actor.h)).to(equal((self.story.actors[0], self.card.y - self.story.actor_gap)))

    with context("that is drawn twice"):
        with it("should give each epic and story the same element id both times"):
            again = WhiteboardStoryModel(round_trip_story_map())
            expect(again.board().order).to(equal(self.story_map.board().order))

    with context("that is read from a board with no story-map elements"):
        with it("should refuse the board"):
            expect(lambda: WhiteboardStoryModel().load(Whiteboard("Empty").save())).to(raise_error(UnreadableBoard))
