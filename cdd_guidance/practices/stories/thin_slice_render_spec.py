"""Mamba spec: a thin slice rendered to a drawing draws the story map's increments."""

import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from expects import be_empty, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.actions.render.rendered_file import RenderedFile
from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryMap
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryMap
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryMap
from cdd_guidance.practices.stories.stories import Stories
from harness.drawio import DrawioFile
from harness.markdown.format import Format

_STORY_MAP = """# Story Map — Bookshop

# (E) Fill Cart
## (E) Add Books
### (S) Customer --> Add Book To Cart
### (S) Customer --> Change Cart Line Quantity
# (E) Check Out
## (E) Place Order
### (S) Customer --> Submit Order
"""

_THIN_SLICE = """# Thin slicing

## Product / context

The Bookshop sells Books from a Cart.

## Increments

### Increment 1: Walking skeleton

**Outcome:** a Customer orders one Book.

**Stories in this increment:**

- *Add Book To Cart*
- *Submit Order*

### Increment 2: Quantities

**Stories in this increment:**

- *Change Cart Line Quantity*
"""


_NOTED_THIN_SLICE = _THIN_SLICE.replace("- *Submit Order*", "- *Submit Order* (partly built: one book per order,\n  never more)")

# The story map with a sub-epic added between two the thin slice drawing already holds.
_STORY_MAP_WITH_DISCOUNTS = _STORY_MAP.replace(
    "# (E) Check Out", "## (E) Apply Discounts\n### (S) Customer --> Apply Discount Code\n# (E) Check Out"
)

# The sub-epic each story of the bookshop map sits under.
_SUB_EPIC_OF = {
    "Add Book To Cart": "Add Books",
    "Change Cart Line Quantity": "Add Books",
    "Submit Order": "Place Order",
    "Apply Discount Code": "Apply Discounts",
}


def _boxes(drawn: str) -> dict:
    """Each vertex of a drawing by its id: its words and its box."""
    return {cell.id: (cell.label, cell.box) for cell in DrawioFile.from_text(drawn).whole.cells if cell.is_vertex and cell.box}


def _cards(drawn: str) -> list:
    """Each story card a thin slice drawing holds: its words and its box."""
    return [(label, box) for name, (label, box) in _boxes(drawn).items() if name.startswith("inc-lane/") and name.count("/") == 2 and not name.endswith("/bg")]


def _bar_of(drawn: str, sub_epic: str):
    return next(box for label, box in _boxes(drawn).values() if label == sub_epic)


def _cards_outside_their_bars(drawn: str) -> list:
    """Each card whose box does not sit within the width of its sub-epic's bar."""
    outside = []
    for label, box in _cards(drawn):
        bar = _bar_of(drawn, _SUB_EPIC_OF[label])
        if not bar.x <= box.x <= box.x + box.w <= bar.x + bar.w:
            outside.append(label)
    return outside


def _overlapping_bars(drawn: str) -> list:
    """Each pair of sub-epic bars that share any width."""
    bars = sorted((box.x, box.x + box.w, label) for label, box in _boxes(drawn).values() if label in set(_SUB_EPIC_OF.values()))
    return [(left[2], right[2]) for left, right in zip(bars, bars[1:]) if left[1] > right[0]]


def _overlapping_cards(drawn: str) -> list:
    cards = _cards(drawn)
    return [(a, b) for index, (a, one) in enumerate(cards) for b, other in cards[index + 1:]
            if one.x < other.x + other.w and other.x < one.x + one.w and one.y < other.y + other.h and other.y < one.y + one.h]


def _laid_out_by_a_person(drawn: str) -> str:
    """drawn with the Add Books bar widened to 400 and the Quantities lane's card moved 300 right of the bar's start,
    as a person lays a drawing out by hand."""
    page = ET.fromstring(drawn)
    geometry = {cell.get("id"): cell.find("mxGeometry") for cell in page.iter("mxCell")}
    bar = next(cell.get("id") for cell in page.iter("mxCell") if cell.get("value") == "Add Books")
    geometry[bar].set("width", "400")
    geometry["inc-lane/quantities/change-cart-line-quantity"].set("x", str(float(geometry[bar].get("x")) + 300))
    return ET.tostring(page, encoding="unicode")


def _lanes(read) -> list:
    return [(increment.name, [story.name for story in increment.stories]) for increment in read.increments]


with description("a thin slice written in thin-slice.md beside its story map") as self:
    with before.each:
        self.context = Path(tempfile.mkdtemp()) / ".context"
        self.context.mkdir()
        (self.context / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
        (self.context / "thin-slice.md").write_text(_THIN_SLICE, encoding="utf-8")
        self.story_map = MarkdownStoryMap().parse(_STORY_MAP)
        self.fidelity = Stories(fidelity="story_map").fidelities.current

    with context("that is rendered to drawio"):
        with before.each:
            self.drawn = self.fidelity.render_files("drawio", [str(self.context / "thin-slice.md")], "markdown").content

        with it("should draw each increment as a lane of the stories it delivers"):
            read = DrawIOStoryMap().copy_of(self.story_map).load_thin_slice(self.drawn)
            expect(_lanes(read)).to(equal([("Walking skeleton", ["Add Book To Cart", "Submit Order"]), ("Quantities", ["Change Cart Line Quantity"])]))

        with it("should draw no heading of the thin slice as an epic"):
            expect([heading for heading in ("Product / context", "Increments") if f'value="{heading}"' in self.drawn]).to(be_empty)

    with context("that is rendered to whiteboard"):
        with before.each:
            self.board = self.fidelity.render_files("whiteboard", [str(self.context / "thin-slice.md")], "markdown").content

        with it("should draw each increment as a lane of the stories it delivers"):
            read = WhiteboardStoryMap().copy_of(self.story_map).load_thin_slice(self.board)
            expect(_lanes(read)).to(equal([("Walking skeleton", ["Add Book To Cart", "Submit Order"]), ("Quantities", ["Change Cart Line Quantity"])]))

    with context("whose story map is rendered to drawio"):
        with before.each:
            self.drawn = self.fidelity.render_files("drawio", [str(self.context / "story-map.md")], "markdown").content

        with it("should draw the story map, not the thin slice's lanes"):
            expect(self.drawn).not_to(contain("inc-lane/"))

    # Seen on main, 2026-11-23: a bullet that said more after its story's name dropped the story from the lane.
    with context("whose story bullet says more after the story's name, rendered to drawio"):
        with before.each:
            (self.context / "thin-slice.md").write_text(_NOTED_THIN_SLICE, encoding="utf-8")
            self.drawn = self.fidelity.render_files("drawio", [str(self.context / "thin-slice.md")], "markdown").content

        with it("should draw the story in its increment's lane"):
            read = DrawIOStoryMap().copy_of(self.story_map).load_thin_slice(self.drawn)
            expect(_lanes(read)).to(equal([("Walking skeleton", ["Add Book To Cart", "Submit Order"]), ("Quantities", ["Change Cart Line Quantity"])]))

    # Seen on main, 2026-11-23: rendered onto the thin slice drawing a person laid out, the cards kept their places while
    # the sub-epic bars were drawn anew, so cards stood outside the bars that hold them.
    with context("that is rendered to drawio onto the thin slice drawing a person laid out"):
        with before.each:
            first = self.fidelity.render_files("drawio", [str(self.context / "thin-slice.md")], "markdown").content
            self.drawing = self.context / "thin-slice.drawio"
            self.drawing.write_text(_laid_out_by_a_person(first), encoding="utf-8")
            self.laid_out = self.drawing.read_text(encoding="utf-8")
            (self.context / "thin-slice.md").write_text(_THIN_SLICE.replace("- *Change Cart Line Quantity*", "- *Change Cart Line Quantity*\n- *Add Book To Cart*"), encoding="utf-8")
            saved = RenderedFile(self.drawing, Format("drawio"), Format("markdown"))
            saved.save(self.fidelity.render_files("drawio", [str(self.context / "thin-slice.md")], "markdown", saved.previous))
            self.drawn = self.drawing.read_text(encoding="utf-8")

        with it("should keep the card the person moved where they put it"):
            card = "inc-lane/quantities/change-cart-line-quantity"
            expect(_boxes(self.drawn)[card][1]).to(equal(_boxes(self.laid_out)[card][1]))

        with it("should keep every card under the bar of the sub-epic that holds it"):
            expect(_cards_outside_their_bars(self.drawn)).to(be_empty)

        with it("should lay no card over another"):
            expect(_overlapping_cards(self.drawn)).to(be_empty)

    # Seen on main, 2026-11-23: a sub-epic the drawing did not hold was drawn over the bars to its right, since the save
    # put each of them back where the drawing had it.
    with context("whose story map gained a sub-epic between two the thin slice drawing a person laid out holds"):
        with before.each:
            first = self.fidelity.render_files("drawio", [str(self.context / "thin-slice.md")], "markdown").content
            self.drawing = self.context / "thin-slice.drawio"
            self.drawing.write_text(_laid_out_by_a_person(first), encoding="utf-8")
            self.laid_out = self.drawing.read_text(encoding="utf-8")
            (self.context / "story-map.md").write_text(_STORY_MAP_WITH_DISCOUNTS, encoding="utf-8")
            (self.context / "thin-slice.md").write_text(_THIN_SLICE.replace("- *Change Cart Line Quantity*", "- *Change Cart Line Quantity*\n- *Apply Discount Code*"), encoding="utf-8")
            saved = RenderedFile(self.drawing, Format("drawio"), Format("markdown"))
            saved.save(self.fidelity.render_files("drawio", [str(self.context / "thin-slice.md")], "markdown", saved.previous))
            self.drawn = self.drawing.read_text(encoding="utf-8")

        with it("should draw the new sub-epic's bar over no other bar"):
            expect(_overlapping_bars(self.drawn)).to(be_empty)

        with it("should keep every card under the bar of the sub-epic that holds it"):
            expect(_cards_outside_their_bars(self.drawn)).to(be_empty)

        with it("should keep the card the person moved, left of the new sub-epic, where they put it"):
            card = "inc-lane/quantities/change-cart-line-quantity"
            expect(_boxes(self.drawn)[card][1]).to(equal(_boxes(self.laid_out)[card][1]))

        with it("should lay no card over another"):
            expect(_overlapping_cards(self.drawn)).to(be_empty)
