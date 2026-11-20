"""Mamba spec: a thin slice rendered to a drawing draws the story map's increments."""

import tempfile
from pathlib import Path

from expects import be_empty, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStoryModel
from cdd_guidance.practices.stories.model.whiteboard.nodes import WhiteboardStoryModel
from cdd_guidance.practices.stories.stories import Stories

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


def _lanes(read) -> list:
    return [(increment.name, [story.name for story in increment.stories]) for increment in read.increments]


with description("a thin slice written in thin-slice.md beside its story map") as self:
    with before.each:
        self.context = Path(tempfile.mkdtemp()) / ".context"
        self.context.mkdir()
        (self.context / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
        (self.context / "thin-slice.md").write_text(_THIN_SLICE, encoding="utf-8")
        self.story_map = MarkdownStoryModel().parse(_STORY_MAP)
        self.fidelity = Stories(fidelity="story_map").fidelities.current

    with context("that is rendered to drawio"):
        with before.each:
            self.drawn = self.fidelity.render_files("drawio", [str(self.context / "thin-slice.md")], "markdown")["content"]

        with it("should draw each increment as a lane of the stories it delivers"):
            read = DrawIOStoryModel(self.story_map).load_thin_slice(self.drawn)
            expect(_lanes(read)).to(equal([("Walking skeleton", ["Add Book To Cart", "Submit Order"]), ("Quantities", ["Change Cart Line Quantity"])]))

        with it("should draw no heading of the thin slice as an epic"):
            expect([heading for heading in ("Product / context", "Increments") if f'value="{heading}"' in self.drawn]).to(be_empty)

    with context("that is rendered to whiteboard"):
        with before.each:
            self.board = self.fidelity.render_files("whiteboard", [str(self.context / "thin-slice.md")], "markdown")["content"]

        with it("should draw each increment as a lane of the stories it delivers"):
            read = WhiteboardStoryModel(self.story_map).load_thin_slice(self.board)
            expect(_lanes(read)).to(equal([("Walking skeleton", ["Add Book To Cart", "Submit Order"]), ("Quantities", ["Change Cart Line Quantity"])]))

    with context("whose story map is rendered to drawio"):
        with before.each:
            self.drawn = self.fidelity.render_files("drawio", [str(self.context / "story-map.md")], "markdown")["content"]

        with it("should draw the story map, not the thin slice's lanes"):
            expect(self.drawn).not_to(contain("inc-lane/"))
