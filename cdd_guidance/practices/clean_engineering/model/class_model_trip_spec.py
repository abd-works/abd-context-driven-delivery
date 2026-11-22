"""A class model taken from the markdown a person wrote to another format and back, through the adapters one practice
keeps: the Bookshop's three models, each written after `templates/class-model.md`."""

from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

BOOKSHOP = Path(__file__).resolve().parent / "fixtures" / "bookshop"


def _model(module: str) -> str:
    return (BOOKSHOP / f"{module}-model.md").read_text(encoding="utf-8")


def _class_headings(markdown: str) -> list:
    """The class each card heading names, in file order."""
    return [line.split("**")[1] if "**" in line else line.lstrip("# ").split(" ")[0] for line in markdown.splitlines() if line.startswith(("## ", "### **"))]


with description("a class model rendered to markdown") as self:
    with before.each:
        self.practice = CleanEngineering(fidelity="model")

    with context("by a practice that rendered another model to markdown before"):
        with before.each:
            other = CleanEngineering(fidelity="model")
            ordering = other.render("python", _model("ordering"), source="markdown").content
            drawing = other.render("drawio", _model("fulfilment"), source="markdown").content
            self.practice.render("markdown", ordering, source="python")
            self.second = self.practice.render("markdown", drawing, source="drawio").content

        with it("should name the second model's own classes, none of the first's"):
            expect(_class_headings(self.second)).to(equal(["Shipment", "ExpressShipment"]))

        with it("should keep the base the second model's class extends"):
            expect(self.second).to(contain("ExpressShipment <<Entity>> : Shipment"))

    with context("from its drawing, over the markdown the drawing was made from"):
        with before.each:
            self.written = _model("ordering")
            drawing = self.practice.render("drawio", self.written, source="markdown").content
            self.back = self.practice.render("markdown", drawing, source="drawio", previous=self.written).content

        with it("should write the file as the person wrote it: front matter, descriptions, group headings, notes and calls"):
            expect(self.back).to(equal(self.written))

    with context("from its whiteboard, over the markdown the whiteboard was made from"):
        with before.each:
            self.written = _model("fulfilment")
            board = self.practice.render("whiteboard", self.written, source="markdown").content
            self.back = self.practice.render("markdown", board, source="whiteboard", previous=self.written).content

        with it("should write the file as the person wrote it"):
            expect(self.back).to(equal(self.written))

    with context("from its drawing, where a person added an operation to one class"):
        with before.each:
            self.written = _model("fulfilment")
            drawing = self.practice.render("drawio", self.written, source="markdown").content
            changed = drawing.replace("+ dispatch(): None", "+ dispatch(): None&lt;br&gt;+ recall(): None", 1)
            self.changed = changed != drawing
            self.back = self.practice.render("markdown", changed, source="drawio", previous=self.written).content

        with it("should write the added operation on its class"):
            expect(self.back).to(contain("+ recall(): None"))

        with it("should keep the note and the call the drawing does not hold on the operations it had"):
            expect(self.back).to(contain("+ dispatch(): None\n\t-> Order.total\n\t// an order whose payment is not authorised is refused"))

        with it("should keep the front matter and the module's description"):
            expect(self.back).to(contain("---\nfidelity: [model]"))
            expect(self.back).to(contain("The parcels the shop sends for paid orders."))

    with context("from the Python it was rendered to"):
        with before.each:
            self.written = _model("ordering")
            python = self.practice.render("python", self.written, source="markdown").content
            self.back = self.practice.render("markdown", python, source="python").content

        with it("should keep the relationship written on a property"):
            expect(self.back).to(contain("+ << composition >> lines: list[CartLine]"))
            expect(self.back).to(contain("+ << association >> book: Book"))

        with it("should keep the note under a property"):
            expect(self.back).to(contain("+ customer_id: str\n\t// who is filling the cart"))

        with it("should keep the class each call is made on, and the note under the operation"):
            expect(self.back).to(contain("+ add(book: Book, quantity: int): CartLine\n\t-> Book.is_in_stock\n\t// a book out of stock is refused"))

        with it("should write the constructor with its own parameters, and no __init__ operation"):
            expect(self.back).to(contain("+ Cart(customer_id: str)\n"))
            expect(self.back).not_to(contain("__init__"))

    with context("from the Python it was rendered to, over the markdown the Python was made from"):
        with before.each:
            self.written = _model("ordering")
            python = self.practice.render("python", self.written, source="markdown").content
            self.back = self.practice.render("markdown", python, source="python", previous=self.written).content

        with it("should write the file as the person wrote it"):
            expect(self.back).to(equal(self.written))


with description("a class model rendered to code") as self:
    with before.each:
        self.practice = CleanEngineering(fidelity="model")

    with context("in TypeScript, from a model written with Python's types"):
        with before.each:
            self.typescript = self.practice.render("typescript", _model("ordering"), source="markdown").content

        with it("should spell a list as TypeScript's array"):
            expect(self.typescript).to(contain("  lines: CartLine[];"))

        with it("should spell a parameter's type and name as TypeScript does"):
            expect(self.typescript).to(contain("  add(book: Book, quantity: number): CartLine {"))

        with it("should call an operation by the name the file itself gives it"):
            expect(self.typescript).to(contain("    Book.isInStock();"))

    with context("in Python, from the TypeScript the model was rendered to"):
        with before.each:
            typescript = self.practice.render("typescript", _model("ordering"), source="markdown").content
            self.python = self.practice.render("python", typescript, source="typescript").content

        with it("should spell TypeScript's types as Python's"):
            expect(self.python).to(contain("    def authorise(self) -> bool:"))
            expect(self.python).to(contain("    lines: list[CartLine]"))

        with it("should keep the relationship written on a property"):
            expect(self.python).to(contain("    # << composition >>\n    lines: list[CartLine]"))
