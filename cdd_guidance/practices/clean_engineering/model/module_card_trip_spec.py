"""Module cards taken from the markdown a person wrote to a drawing or a whiteboard and back, through the adapters one
practice keeps: the Bookshop's three cards, each written after `templates/modules.md`, read one after another as a
render of several files reads them."""

from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel

BOOKSHOP = Path(__file__).resolve().parent / "fixtures" / "bookshop"
MODULES = ("catalogue", "ordering", "fulfilment")


def _card(module: str) -> str:
    return (BOOKSHOP / f"{module}-module-context.md").read_text(encoding="utf-8")


CARDS = "\n\n".join(_card(module) for module in MODULES)


def _dependencies(markdown: str) -> dict:
    """The modules each module of a modules document depends on, by its name."""
    return {module.name: list(module.dependencies) for module in MarkdownCleanEngineeringModel().parse(markdown).modules}


with description("module cards rendered to markdown") as self:
    with before.each:
        self.practice = CleanEngineering(fidelity="modules")

    with context("read by the markdown model"):
        with before.each:
            self.ordering = MarkdownCleanEngineeringModel().parse(_card("ordering")).modules[0]

        with it("should keep the card's language, the lines that open it"):
            expect(self.ordering.language).to(contain("*Cart* is what a customer fills while browsing"))
            expect(self.ordering.language).to(contain("*Order* is the cart's lines as bought"))

        with it("should keep the card's constraint"):
            expect(self.ordering.constraint).to(equal("Make an *Order* only through `Cart.check_out`; an order built by hand has no authorised payment."))

        with it("should read the Constraint section as no class"):
            expect([oclass.name for oclass in self.ordering.classes]).to(equal([]))

    with context("from their drawing, with no markdown to write over"):
        with before.each:
            drawn = self.practice.render("drawio", CARDS, source="markdown").content
            self.back = self.practice.render("markdown", drawn, source="drawio").content

        with it("should hold the three modules the cards name, and no module that only groups them"):
            expect(list(_dependencies(self.back))).to(equal(["src/catalogue", "src/ordering", "src/fulfilment"]))

        with it("should hold the three dependencies the cards name, none on the folder that holds the modules"):
            expect(_dependencies(self.back)).to(equal({
                "src/catalogue": [],
                "src/ordering": ["src/catalogue"],
                "src/fulfilment": ["src/ordering", "src/catalogue"],
            }))

        with it("should write each module's purpose once"):
            expect(self.back.count("let a customer fill a cart with books and check it out into a paid order")).to(equal(1))

    with context("from their drawing, over the markdown it was made from"):
        with before.each:
            drawn = self.practice.render("drawio", CARDS, source="markdown").content
            self.back = self.practice.render("markdown", drawn, source="drawio", previous=CARDS).content

        with it("should write each card as the person wrote it: its language, its bullets and its constraint"):
            for module in MODULES:
                expect(self.back).to(contain(_card(module).rstrip("\n")))

    with context("from their drawing, where a module gained a dependency, over the markdown it was made from"):
        with before.each:
            model = MarkdownCleanEngineeringModel().parse(CARDS)
            model.modules[0].dependencies = ["src/fulfilment"]
            drawn = CleanEngineering(fidelity="modules").render("drawio", model).content
            self.back = self.practice.render("markdown", drawn, source="drawio", previous=CARDS).content

        with it("should write the new dependency on its card"):
            expect(_dependencies(self.back)["src/catalogue"]).to(equal(["src/fulfilment"]))

        with it("should keep that card's language and constraint, which the drawing does not hold"):
            expect(self.back).to(contain("*Book* is a title the bookshop sells"))
            expect(self.back).to(contain("## Constraint\n\nTake stock only through `Book.reserve`; a caller never writes the number of copies itself."))

        with it("should leave the other cards as the person wrote them"):
            expect(self.back).to(contain(_card("ordering").rstrip("\n")))

    with context("from their whiteboard, with no markdown to write over"):
        with before.each:
            drawn = self.practice.render("whiteboard", CARDS, source="markdown").content
            self.back = self.practice.render("markdown", drawn, source="whiteboard").content

        with it("should hold the three modules the cards name, and no module that only groups them"):
            expect(list(_dependencies(self.back))).to(equal(["src/catalogue", "src/ordering", "src/fulfilment"]))

        with it("should hold the three dependencies the cards name, none on the folder that holds the modules"):
            expect(_dependencies(self.back)).to(equal({
                "src/catalogue": [],
                "src/ordering": ["src/catalogue"],
                "src/fulfilment": ["src/ordering", "src/catalogue"],
            }))

        with it("should write each module's purpose once"):
            expect(self.back.count("let a customer fill a cart with books and check it out into a paid order")).to(equal(1))

    with context("from their whiteboard, over the markdown it was made from"):
        with before.each:
            drawn = self.practice.render("whiteboard", CARDS, source="markdown").content
            self.back = self.practice.render("markdown", drawn, source="whiteboard", previous=CARDS).content

        with it("should write each card as the person wrote it: its language, its bullets and its constraint"):
            for module in MODULES:
                expect(self.back).to(contain(_card(module).rstrip("\n")))

    with context("from their whiteboard, where a module gained a dependency, over the markdown it was made from"):
        with before.each:
            model = MarkdownCleanEngineeringModel().parse(CARDS)
            model.modules[0].dependencies = ["src/fulfilment"]
            drawn = CleanEngineering(fidelity="modules").render("whiteboard", model).content
            self.back = self.practice.render("markdown", drawn, source="whiteboard", previous=CARDS).content

        with it("should write the new dependency on its card"):
            expect(_dependencies(self.back)["src/catalogue"]).to(equal(["src/fulfilment"]))

        with it("should keep that card's language and constraint, which the drawing does not hold"):
            expect(self.back).to(contain("*Book* is a title the bookshop sells"))
            expect(self.back).to(contain("## Constraint\n\nTake stock only through `Book.reserve`; a caller never writes the number of copies itself."))

        with it("should leave the other cards as the person wrote them"):
            expect(self.back).to(contain(_card("ordering").rstrip("\n")))
