"""Mamba spec: a story map drawn in draw.io reads back as the same map.

A draw.io story map holds epics, stories, their kind, and their actors; scenarios live in the story files."""

from expects import be_a, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel
from cdd_guidance.practices.stories.model.story_model import Epic, Story, StoryModel, StoryType


def _nested_four_levels() -> StoryModel:
    """A top-level epic with sub-epics nested three deep, each epic holding one story with its own actor."""
    story_map = StoryModel()
    holder = Epic("Top", 1)
    story_map.epics.append(holder)
    for level, name in enumerate(["Top", "Level One", "Level Two", "Level Three"]):
        if level:
            child = Epic(name, 1)
            holder.epics.append(child)
            holder = child
        story = Story(f"{name} Story", 1, StoryType.USER)
        story.actors = [f"Actor {level}"]
        holder.stories.append(story)
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


_FIRST_MAP = """# (E) Sell Books
## (E) Take Orders
### (S) Customer --> Place Order
### (S) Customer --> Cancel Order
"""

_GROWN_MAP = """# (E) Sell Books
## (E) Take Orders
### (S) Customer --> Place Order
### (S) Customer --> Cancel Order
### (S) Customer --> Track Order
## (E) Ship Orders
### (S) Clerk --> Pack Order
"""


def _drawn(markdown: str, previous: str | None = None) -> str:
    return DrawIOStoryModel().render(MarkdownStoryModel().parse(markdown), previous=previous)


with description("a story map in markdown drawn again after it grew") as self:
    with before.each:
        self.grown = MarkdownStoryModel().parse(_GROWN_MAP)
        self.redrawn = _drawn(_GROWN_MAP, previous=_drawn(_FIRST_MAP))
        self.read = DrawIOStoryModel().load(self.redrawn)

    with context("with a story added to a sub-epic the first drawing already held"):
        with it("should read the added story back under the sub-epic it was written in"):
            expect(outline(self.read, with_scenarios=False)).to(equal(outline(self.grown, with_scenarios=False)))

        with it("should widen the kept sub-epic to cover its added story"):
            placed = {cell.cell_id: cell for cell in DrawIOStoryModel().placed_cells(self.redrawn)}
            expect(placed["sell-books/take-orders"].spans(placed["sell-books/take-orders/track-order"].center)).to(equal(True))

    with context("with the added story left outside every sub-epic, as a drawing made before the fix has it"):
        with before.each:
            narrow = self.redrawn.replace('width="170"', 'width="110"', 1)
            self.read_narrow = DrawIOStoryModel().load(narrow)

        with it("should place the story under the sub-epic its cell's id names"):
            expect(outline(self.read_narrow, with_scenarios=False)).to(equal(outline(self.grown, with_scenarios=False)))

    with context("with a story a person dragged under another sub-epic"):
        with before.each:
            cells = {cell.cell_id: cell for cell in DrawIOStoryModel().placed_cells(self.redrawn)}
            pack = cells["sell-books/ship-orders/pack-order"]
            cancel = cells["sell-books/take-orders/cancel-order"]
            moved = self.redrawn.replace(f'x="{int(cancel.x)}" y="{int(cancel.y)}"', f'x="{int(pack.x) + 5}" y="{int(pack.y)}"')
            ship = DrawIOStoryModel().load(moved).epics[0].epics[1]
            self.ship_stories = [story.name for story in ship.stories]

        with it("should read the story under the sub-epic it was dragged to"):
            expect(self.ship_stories).to(equal(["Pack Order", "Cancel Order"]))
