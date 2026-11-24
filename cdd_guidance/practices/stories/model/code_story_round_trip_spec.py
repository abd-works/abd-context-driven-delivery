"""Mamba spec: a scenarios file written after the template, rendered to a code format and back to its scenarios file.

What a person wrote around the scenarios, which no step or example holds, comes back with them: the front matter, the
story's kind, the link to the story map, the domain terms and the sentences under the story's heading, each domain
term's link in the steps, and the realization under a When."""

from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownStory, MarkdownStoryMap
from cdd_guidance.practices.stories.model.python.python_story_map import PythonStoryMap
from cdd_guidance.practices.stories.model.typescript.typescript_story_map import TypeScriptStoryMap

_ADD_BOOK = Path(__file__).resolve().parent / "fixtures" / "bookshop" / "story_tests" / "fill-cart" / "add-books" / "add_book_to_cart_story.test.md"
_DOMAIN_MODEL = "../../../.context/domain-model.md"
_BOOK = f"++[Book]({_DOMAIN_MODEL}#book-aggregate-root-entity)++"
_CART = f"++[Cart]({_DOMAIN_MODEL}#cart-aggregate-root-entity)++"


def _back_from(format: type) -> str:
    """The scenarios file of Add Book To Cart, written from the story read back from the code format writes it in."""
    code = format(tests_root="tests")
    files = code.render(MarkdownStoryMap().parse(_ADD_BOOK.read_text(encoding="utf-8")))
    story = format(tests_root="tests").parse(files).descendants.stories()[0]
    return MarkdownStory.copy_of(story).scenarios_text()


with description("a scenarios file written after the template") as self:
    with context("that is rendered to Python and read back into its scenarios file"):
        with before.all:
            self.back = _back_from(PythonStoryMap)

        with it("should open with the front matter"):
            expect(self.back.startswith("---\nfidelity: [scenarios]\nartifact: [story-scenarios]\nformat: md\n---\n\n## Story: Add Book To Cart\n")).to(equal(True))

        with it("should keep the story's kind"):
            expect(self.back).to(contain("**Story type:** website"))

        with it("should keep the link to the story map"):
            expect(self.back).to(contain("See the [story map](../../../.context/story-map.md#s-customer----add-book-to-cart) for where this story sits."))

        with it("should keep the domain terms, each with its link"):
            expect(self.back).to(contain(f"### Domain terms\n\n- {_BOOK} — a title the Bookshop sells at a price\n"))

        with it("should link each domain term a step names"):
            expect(self.back).to(contain(f"*When* the Customer adds {_BOOK} ++Tiny Tales++ to the {_CART}"))

        with it("should keep the realization under the When"):
            expect(self.back).to(contain("```realization\nCart.addBook(book, 1)\n  -> Book.reserve(1)\n  <- CartLine\n```"))

        with it("should write each examples table once"):
            expect(self.back.count("| book | Tiny Tales | 978-1 | Tiny Tales | 5 | 10 |")).to(equal(1))

    with context("that is rendered to TypeScript and read back into its scenarios file"):
        with before.all:
            self.back = _back_from(TypeScriptStoryMap)

        with it("should open with the front matter"):
            expect(self.back.startswith("---\nfidelity: [scenarios]\nartifact: [story-scenarios]\nformat: md\n---\n\n## Story: Add Book To Cart\n")).to(equal(True))

        with it("should keep the story's kind"):
            expect(self.back).to(contain("**Story type:** website"))

        with it("should keep the link to the story map"):
            expect(self.back).to(contain("See the [story map](../../../.context/story-map.md#s-customer----add-book-to-cart) for where this story sits."))

        with it("should keep the domain terms, each with its link"):
            expect(self.back).to(contain(f"### Domain terms\n\n- {_BOOK} — a title the Bookshop sells at a price\n"))

        with it("should link each domain term a step names"):
            expect(self.back).to(contain(f"*When* the Customer adds {_BOOK} ++Tiny Tales++ to the {_CART}"))

        with it("should keep the realization under the When"):
            expect(self.back).to(contain("```realization\nCart.addBook(book, 1)\n  -> Book.reserve(1)\n  <- CartLine\n```"))

        with it("should write each examples table once"):
            expect(self.back.count("| book | Tiny Tales | 978-1 | Tiny Tales | 5 | 10 |")).to(equal(1))
