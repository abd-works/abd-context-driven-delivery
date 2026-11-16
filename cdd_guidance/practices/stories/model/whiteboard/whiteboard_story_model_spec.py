"""Mamba spec: a story map drawn on a Claude Whiteboard reads back as the same map.

A whiteboard story map holds epics, stories, their kind, and their actors; scenarios live in the story files, as they
do for drawio and miro."""

from expects import be_a, be_below, equal, expect, raise_error
from mamba import before, context, description, it

from harness.whiteboard.whiteboard import UnreadableBoard, Whiteboard
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.diagram_story_model import DiagramIncrement
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStory, WhiteboardStoryModel


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
            expect(self.bar.box.y + self.bar.box.h).to(be_below(self.card.box.y))

        with it("should write the story's actor in italics above its name on the card"):
            expect(self.card.text).to(equal(f"*{self.story.actors[0]}*\n{self.story.name}"))

    with context("that is drawn on a board"):
        with before.each:
            self.cards = [element for element in self.story_map.board().elements if element.role == "story"]

        with it("should leave no two story cards overlapping"):
            boxes = sorted((card.box for card in self.cards), key=lambda box: (box.y, box.x))
            touching = [(first, second) for first, second in zip(boxes, boxes[1:])
                        if first.y == second.y and second.x < first.x + first.w + 24]
            expect(touching).to(equal([]))

        with it("should size each card for its actor and a name of three lines of small text"):
            letters_per_line = (WhiteboardStory.card_width - 24) // 7.5
            lines_room = (WhiteboardStory.size - 24) // 21
            expect(all(len(story.name) <= 3 * letters_per_line and lines_room >= 4 for story in self.story_map.descendants.stories())).to(equal(True))

    with context("that is drawn twice"):
        with it("should give each epic and story the same element id both times"):
            again = WhiteboardStoryModel(round_trip_story_map())
            expect(again.board().order).to(equal(self.story_map.board().order))

    with context("that is read from a board with no story-map elements"):
        with it("should refuse the board"):
            expect(lambda: WhiteboardStoryModel().load(Whiteboard("Empty").save())).to(raise_error(UnreadableBoard))


with description("a story map's thin slice drawn on a Claude whiteboard") as self:
    with before.each:
        self.story_map = WhiteboardStoryModel(round_trip_story_map())
        stories = self.story_map.descendants.stories()
        self.story_map.increments.append(DiagramIncrement("Walking Skeleton", 1, [stories[0], stories[-1]]))
        self.story_map.increments.append(DiagramIncrement("Next Slice", 2, stories[1:3]))
        self.board = Whiteboard.from_text(self.story_map.save_thin_slice())
        self.lanes = [element for element in self.board.elements if element.role == "lane"]

    with it("should draw one lane per increment, each below the one before it, its name in a label at its left"):
        labels = [element for element in self.board.elements if element.role == "increment"]
        expect([(label.text, lane.holds(label), label.box.x < min(card.box.x for card in self.board.elements if card.role == "story"))
                for lane, label in zip(self.lanes, labels)]).to(equal([("Walking Skeleton", True, True), ("Next Slice", True, True)]))
        expect(self.lanes[0].box.y + self.lanes[0].box.h).to(be_below(self.lanes[1].box.y))

    with it("should put each lane's stories inside it"):
        cards = [element for element in self.board.elements if element.role == "story"]
        expect(sorted(sum(1 for card in cards if lane.holds(card)) for lane in self.lanes)).to(equal([2, 2]))

    with it("should read back each increment with the stories its lane holds"):
        read = WhiteboardStoryModel(round_trip_story_map()).load_thin_slice(self.board.save())
        expect([(increment.name, [story.name for story in increment.stories]) for increment in read.increments]).to(equal(
            [(increment.name, [story.name for story in increment.stories]) for increment in self.story_map.increments]
        ))
