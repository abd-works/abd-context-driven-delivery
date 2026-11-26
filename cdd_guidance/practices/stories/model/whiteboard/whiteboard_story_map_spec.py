"""Mamba spec: a story map drawn on a Claude Whiteboard reads back as the same map.

A whiteboard story map holds epics, stories, their kind, and their actors; scenarios live in the story files, as they
do for drawio and miro."""

from pathlib import Path
from expects import be_a, be_below, equal, expect, raise_error
from mamba import before, context, description, it

from harness.guidance.practice_formats import Written
from harness.whiteboard.whiteboard import UnreadableBoard, Whiteboard
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.diagram_story_map import DiagramIncrement
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStory, WhiteboardStoryMap


with description("a story map drawn on a Claude whiteboard") as self:
    with before.each:
        self.story_map = WhiteboardStoryMap().copy_of(round_trip_story_map())
        self.read = WhiteboardStoryMap().parse(self.story_map.save())

    with it("should read back every epic, story held by any epic, kind, and actor"):
        expect(outline(self.read, with_scenarios=False)).to(equal(outline(self.story_map, with_scenarios=False)))

    with it("should copy itself as a whiteboard story map"):
        expect(self.read.clone()).to(be_a(WhiteboardStoryMap))

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
            again = WhiteboardStoryMap().copy_of(round_trip_story_map())
            expect(again.board().order).to(equal(self.story_map.board().order))

    with context("that is read from a board with no story-map elements"):
        with it("should refuse the board"):
            expect(lambda: WhiteboardStoryMap().parse(Whiteboard("Empty").save())).to(raise_error(UnreadableBoard))


_LINKED_MAP = """# (E) Onboard A Customer
## (E) Get Sim
### (S) Customer --> Select Sim
### (S) Customer --> Activate Sim
"""


def _checkout(files: dict) -> Path:
    """A git checkout on branch main whose origin is github.com/org/shop, holding files."""
    import subprocess
    import tempfile

    root = Path(tempfile.mkdtemp())
    for relative, text in files.items():
        (root / relative).parent.mkdir(parents=True, exist_ok=True)
        (root / relative).write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "remote", "add", "origin", "https://github.com/org/shop.git"], check=True)
    return root


with description("a story map drawn on a Claude whiteboard in a folder of a git checkout") as self:
    with before.all:
        from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryMap

        self.root = _checkout({
            "story-map.md": _LINKED_MAP,
            "onboard/get-sim/select_sim_story.test.md": "## Story: Select Sim\n",
        })
        self.text = WhiteboardStoryMap().render(MarkdownStoryMap().parse(_LINKED_MAP), Written(folder=self.root))
        self.cards = {line.splitlines()[-1]: line for line in (element.text for element in Whiteboard.from_text(self.text).elements if element.role == "story")}

    # A board opens only a web address, so a story's file is linked where its checkout's origin shows it.
    with it("should link a story's name on its card to its scenario file where the checkout's origin shows it"):
        expect(self.cards["[Select Sim](https://github.com/org/shop/blob/main/onboard/get-sim/select_sim_story.test.md)"]).to(equal(
            "*Customer*\n[Select Sim](https://github.com/org/shop/blob/main/onboard/get-sim/select_sim_story.test.md)"))

    with it("should leave the name of a story with no file of its own as words"):
        expect("Activate Sim" in self.cards).to(equal(True))

    with it("should read a linked card back as its story's name"):
        stories = WhiteboardStoryMap().parse(self.text).epics[0].epics[0].stories
        expect([story.name for story in stories]).to(equal(["Select Sim", "Activate Sim"]))


with description("a story map's thin slice drawn on a Claude whiteboard") as self:
    with before.each:
        self.story_map = WhiteboardStoryMap().copy_of(round_trip_story_map())
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
        read = WhiteboardStoryMap().copy_of(round_trip_story_map()).load_thin_slice(self.board.save())
        expect([(increment.name, [story.name for story in increment.stories]) for increment in read.increments]).to(equal(
            [(increment.name, [story.name for story in increment.stories]) for increment in self.story_map.increments]
        ))


def _saved_as(name: str, text: str) -> Whiteboard:
    """text saved by a render as the whiteboard file called name, read back."""
    import tempfile
    from cdd_guidance.actions.render.rendered_file import RenderedFile
    from harness.guidance.practice_formats import Rendered
    from harness.markdown.format import Format

    file = Path(tempfile.mkdtemp(prefix="board-title-")) / name
    RenderedFile(file, Format("whiteboard")).save(Rendered(Format("whiteboard"), text))
    return Whiteboard.from_text(file.read_text(encoding="utf-8"))


with description("a story map's board saved as its file") as self:
    with it("should be titled with the file's name, story-map"):
        expect(_saved_as("story-map.whiteboard", WhiteboardStoryMap().copy_of(round_trip_story_map()).save()).title).to(equal("story-map"))

    with it("should keep a versioned file's version in its title"):
        expect(_saved_as("story-map.version-2.whiteboard", WhiteboardStoryMap().copy_of(round_trip_story_map()).save()).title).to(equal("story-map.version-2"))

    with it("should title the thin slice with its file's name, thin-slice"):
        expect(_saved_as("thin-slice.whiteboard", WhiteboardStoryMap().copy_of(round_trip_story_map()).save_thin_slice()).title).to(equal("thin-slice"))
