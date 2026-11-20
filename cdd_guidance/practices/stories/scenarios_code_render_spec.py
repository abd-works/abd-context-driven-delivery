"""Mamba spec: scenarios files rendered to code are named for the epic and sub-epic their story map gives them."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.stories import Stories
from space.session import Session, Sessions

_STORY_MAP = """# Story Map — Bookshop

# (E) Fill Cart
## (E) Add Books
### (S) Customer --> Add Book To Cart
### (S) Customer --> Change Cart Line Quantity
# (E) Check Out
## (E) Place Order
### (S) Customer --> Submit Order
"""

_SCENARIOS = """## Story: Add Book To Cart

### Scenario: Add a first book

*Given* the Cart is empty
*When* the Customer adds Tiny Tales
*Then* the Cart holds Tiny Tales
"""


with description("the scenarios files of one sub-epic, in a project whose story map holds other epics") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp())
        (self.project / ".context").mkdir()
        (self.project / ".context" / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
        self.folder = self.project / "story_tests" / "fill-cart" / "add-books"
        self.folder.mkdir(parents=True)
        (self.folder / "add_book_to_cart_story.test.md").write_text(_SCENARIOS, encoding="utf-8")
        # A render reads its paths from the project of the session the practice works in.
        stories = Stories(fidelity="scenarios")
        stories.work_in(Session(Sessions(self.project)).practice("stories"))
        self.fidelity = stories.fidelities.current

    with context("that are rendered to Python by their folder"):
        with before.each:
            self.files = self.fidelity.render_files("python", ["story_tests/fill-cart/add-books"], "markdown")["content"]

        with it("should write one story test, named for the epic and sub-epic the map gives the stories"):
            expect(list(self.files)).to(equal(["tests/fill-cart/add_books_story.test.py"]))

        with it("should hold the story the scenarios file specifies"):
            expect(self.files["tests/fill-cart/add_books_story.test.py"]).to(contain('with story("Add Book To Cart"):'))

        with it("should hold no story of the map that has no scenarios in the folder"):
            expect(self.files["tests/fill-cart/add_books_story.test.py"]).not_to(contain("Change Cart Line Quantity"))

    with context("that are rendered to TypeScript by one file"):
        with before.each:
            named = ["story_tests/fill-cart/add-books/add_book_to_cart_story.test.md"]
            self.files = self.fidelity.render_files("typescript", named, "markdown")["content"]

        with it("should write the story test named for the epic and sub-epic, beside the step library"):
            expect(sorted(self.files)).to(equal(["tests/fill-cart/add_books_story.test.ts", "tests/story-test.ts"]))
