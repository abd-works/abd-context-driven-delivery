"""Mamba spec: scenarios files rendered to code, and story tests rendered to scenarios files, are named as their
fidelity declares them, and hold only the stories the named files specify."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.pack_orders_project import PACK_ORDERS_FILES, PACK_ORDERS_STORY_MAP
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

_ADD_BOOK_PYTHON = "story_tests/fill-cart/add-books/add-book-to-cart/add_book_to_cart_story.test.py"


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
        stories.work_in(Sessions(self.project).named("main").practice("stories"))
        self.fidelity = stories.fidelities.current

    with context("that are rendered to Python by their folder"):
        with before.each:
            self.files = self.fidelity.render_files("python", ["story_tests/fill-cart/add-books"], "markdown")["content"]

        with it("should write the story's test in its own folder, under the epic and sub-epic the map gives it"):
            expect(list(self.files)).to(equal([_ADD_BOOK_PYTHON]))

        with it("should hold the story the scenarios file specifies"):
            expect(self.files[_ADD_BOOK_PYTHON]).to(contain('with story("Add Book To Cart"):'))

        with it("should hold no story of the map that has no scenarios in the folder"):
            expect(self.files[_ADD_BOOK_PYTHON]).not_to(contain("Change Cart Line Quantity"))

    with context("that are rendered to TypeScript by one file"):
        with before.each:
            named = ["story_tests/fill-cart/add-books/add_book_to_cart_story.test.md"]
            self.files = self.fidelity.render_files("typescript", named, "markdown")["content"]

        with it("should write the story's test in its own folder, and the step library at the root of the story tests"):
            expect(sorted(self.files)).to(equal(["story_tests/fill-cart/add-books/add-book-to-cart/add_book_to_cart_story.test.ts", "story_tests/story-test.ts"]))


def _fidelity_in(project: Path, name: str):
    """The Stories fidelity called name, working in a session of project, which a render reads its paths from."""
    stories = Stories(fidelity=name)
    stories.work_in(Sessions(project).named("main").practice("stories"))
    return stories.fidelities.current


with description("the story tests of Pack Orders, in a project with their story map") as self:
    with before.each:
        self.project = Path(tempfile.mkdtemp())
        for file, text in {".context/story-map.md": PACK_ORDERS_STORY_MAP, **PACK_ORDERS_FILES["typescript"]}.items():
            path = self.project / file
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    # Exploratory testing, r3-sparky-07: a render of one shared story file wrote a story test for every story of the map.
    with context("whose shared story file alone is rendered to Python"):
        with before.each:
            named = ["story_tests/fulfil-order/pack-orders/pack-orders.story.shared.ts"]
            self.files = _fidelity_in(self.project, "acceptance_tests").render_files("python", named, "typescript")["content"]

        with it("should write a story test only for the story that file holds"):
            expect(list(self.files)).to(equal(["story_tests/fulfil-order/pack-orders/cancel-order/cancel_order_story.test.py"]))

    with context("that are rendered to markdown scenarios by their folder"):
        with before.each:
            fidelity = _fidelity_in(self.project, "scenarios")
            self.declared = fidelity.declared
            self.files = fidelity.render_files("markdown", ["story_tests"], "typescript")["content"]

        with it("should answer a scenarios file for each story, in its sub-epic's folder"):
            expect(sorted(self.files)).to(equal([
                "story_tests/fulfil-order/pack-orders/cancel_order_story.test.md",
                "story_tests/fulfil-order/pack-orders/pack_order_story.test.md",
            ]))

        with it("should name each file as the scenarios fidelity declares it"):
            expect([path for path in self.files if not self.declared.includes(path, "markdown")]).to(equal([]))

        with it("should write a story's scenarios into its own file"):
            expect(self.files["story_tests/fulfil-order/pack-orders/cancel_order_story.test.md"]).to(contain("Scenario: Cancel a paid order"))
