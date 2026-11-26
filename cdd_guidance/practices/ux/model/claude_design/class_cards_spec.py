"""Mamba spec for the class card a step's domain term opens in the story explorer: the class's heading and the section
under it, shown as plain text, so a class model written from the Clean Engineering template (a bold class name, italic
terms, bold responsibility names) reads as words, not as markdown marks."""

from expects import equal, expect
from mamba import before, description, it

from cdd_guidance.practices.ux.model.claude_design.class_cards import ClassCard

_TEMPLATE_SECTION = [
    "### **Cart** <<Aggregate Root>>",
    "",
    "The *Cart* is the books a customer means to buy.",
    "",
    "- **Lines.** The Cart adds a *CartLine* for each book.",
    "",
    "---",
    "+ add(book: Book) -> CartLine",
]


with description("a class card of a class written from the Clean Engineering template") as self:
    with before.all:
        self.card = ClassCard.from_section(_TEMPLATE_SECTION)

    with it("should title the card with the class's name and its stereotypes, without the bold marks"):
        expect(self.card.title).to(equal("Cart «Aggregate Root»"))

    with it("should show the class's language without its bold and italic marks, keeping its bullets and members"):
        expect(self.card.text).to(equal(
            "The Cart is the books a customer means to buy.\n\n- Lines. The Cart adds a CartLine for each book.\n\n– – –\n+ add(book: Book) -> CartLine"))
