"""A Then observes an Example, and an example shows a class, only where a domain model or a class model is written for
the story's area of the story map: the stories under one sub-epic or epic."""

from expects import be_empty, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.fixtures.bookshop_project import BookshopWorkingCopy

_ADD_BOOK = "story_tests/fill-cart/add-books/add_book_to_cart_story.test.md"
_CHANGE_QUANTITY = "story_tests/fill-cart/add-books/change_cart_line_quantity_story.test.md"
_SEARCH_BOOKS = "story_tests/browse-books/search-books/search_books_story.test.ts"
_DOMAIN_MODEL = ".context/domain-model.md"
_BOOK_LINK = "[Book](../../../.context/domain-model.md#book-aggregate-root-entity)"
_THEN_RULE = "then-observes-an-example"
_NO_EXAMPLE_NAMED = (
    "Then 'the Bookshop refuses with \"order 9999 is not found\"' observes no Example, though a model is written for "
    "its area of the story map; name an example in it, or in a Given of its scenario or of its story's Background."
)


def _example_gaps(project: BookshopWorkingCopy) -> list[str]:
    """Each finding that an example shows no class, or nothing that retrieves it."""
    gaps = project.findings("conforms-to-schema")
    return [gap for gap in gaps if " has no demonstrates relationship " in gap or " has no retrievedUsing relationship " in gap]


def _findings_on(project: BookshopWorkingCopy, file: str, words: str) -> list[str]:
    """Every rule's findings on the steps of file whose text holds words."""
    project.stories.rule_run.check()
    steps = [node for node in project.stories.nodes() if node.source.file == file and words in node.name]
    return [violation.message for step in steps for entry in step.rules.entries.values() for violation in getattr(entry, "violations", [])]


with description("scenarios checked against the Stories rules") as self:
    with context("with no domain model and no class model in the graph"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories",))

        with it("should hold no Then to observe an Example"):
            expect(self.project.findings(_THEN_RULE)).to(be_empty)

        with it("should hold no Then to an observes relationship its schema requires"):
            expect([gap for gap in self.project.findings("conforms-to-schema") if " observes " in gap]).to(be_empty)

        with it("should hold no example to show a class"):
            expect(_example_gaps(self.project)).to(be_empty)

        # Seen 2026-11-21 (r3-sparky-04): a row of a markdown examples table was asked to sit in an examples file.
        with it("should ask no example of a markdown examples table to sit in an examples file"):
            expect(self.project.findings("domain-fixture-example-files")).to(be_empty)

        with it("should keep the names an outline's examples table gives its rows"):
            examples = [node.name for node in self.project.stories.nodes("Example") if node.source.file == _CHANGE_QUANTITY]
            expect(examples).to(equal(["cart with Tiny Tales", "one copy", "two copies", "three copies"]))

        # Seen 2026-11-21 (r3-sparky-04): "the Cart Line of Tiny Tales" names the book, and the step was joined to the
        # example Tiny Tales of another story's scenarios file.
        with it("should have no step observe an example of another story's markdown scenarios file"):
            observed = [
                edge.child.source.file
                for step in self.project.stories.nodes()
                if step.source.file == _CHANGE_QUANTITY
                for edge in self.project.graph.edges.from_parent("observes", step)
            ]
            expect(set(observed)).to(equal({_CHANGE_QUANTITY}))

    with context("with steps that link their domain terms to a model document that is not there"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "ddd"), removed=(_DOMAIN_MODEL,))

        with it("should hold no Then to observe an Example"):
            expect(self.project.findings(_THEN_RULE)).to(be_empty)

        with it("should record no edge for a link that reaches no class"):
            expect(self.project.edges("names")).to(be_empty)

        with it("should report nothing on the steps that hold those links"):
            expect(_findings_on(self.project, _ADD_BOOK, "++Cart++")).to(be_empty)

    with context("with code read as a class model, and scenarios in markdown that no step joins to it"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "clean_engineering"), removed=(_DOMAIN_MODEL,))

        with it("should hold no example of those scenarios to show a class"):
            expect([gap for gap in _example_gaps(self.project) if "'Tiny Tales'" in gap]).to(be_empty)

    with context("with a domain model the steps of a sub-epic's stories link their terms to"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "ddd"))

        with it("should have a Then observe the example its own text names, with no code read"):
            expect(self.project.observed_by('then the Bookshop refuses with "Grand Atlas is out of stock"', _ADD_BOOK)).to(contain("Grand Atlas"))

        with it("should have a Then that names no example observe those its story's Background names"):
            expect(self.project.observed_by("and the Cart total is *5*", _ADD_BOOK)).to(equal(["Tiny Tales", "empty cart"]))

        with it("should find every Then of that sub-epic's scenarios observing an Example"):
            expect([found for found in self.project.findings(_THEN_RULE) if "Cart" in found]).to(be_empty)

        with it("should report a Then of a modelled area that names no example"):
            expect(self.project.findings(_THEN_RULE)).to(contain(_NO_EXAMPLE_NAMED))

    with context("with a domain model written, and one epic whose scenarios link no term to it"):
        with before.all:
            self.project = BookshopWorkingCopy(("stories", "ddd"), rewritten={_SEARCH_BOOKS: (_BOOK_LINK, "Book")})

        with it("should hold no Then of that epic's stories to observe an Example"):
            expect([found for found in self.project.findings(_THEN_RULE) if "the Customer sees" in found and "Book" in found]).to(be_empty)

        with it("should still hold the Thens of the areas whose steps link to the model"):
            expect(self.project.findings(_THEN_RULE)).to(contain(_NO_EXAMPLE_NAMED))
