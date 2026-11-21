"""Specs for a render written onto a code file that is already there: the file takes the new shape and loses nothing.
The behaviours are written once and run for Python, TypeScript and JavaScript, each on a cart written in that
language; what only one language does has its own examples after them. The Render action that calls it is in
render_spec.py."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_empty, contain, equal, expect, raise_error
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.actions.render.reshaped_code import ReshapedCode, RenderWouldLoseContent
from harness.guidance.practice_formats import Reshaped
from harness.markdown.format import Format


# How each language writes the class around its operations, and one empty operation.
_SHELLS = {
    "python": ("class Cart:\n", ""),
    "typescript": ("class Cart {\n", "}\n"),
    "javascript": ("class Cart {\n", "}\n"),
}
_EMPTY = {
    "python": "    def NAME(self) -> None:\n        raise NotImplementedError\n",
    "typescript": '  NAME(): void {\n    throw new Error("not implemented");\n  }\n',
    "javascript": '  NAME() {\n    throw new Error("not implemented");\n  }\n',
}


_PROPERTY = {"python": "    NAME: str", "typescript": "  NAME: string;", "javascript": "  NAME;"}
_TOTAL_TAKING_TAX = {
    "python": "def total(self, tax: int) -> None:",
    "typescript": "total(tax: number): void {",
    "javascript": "total(tax) {",
}


def _shape(language: str, *operations: str) -> str:
    opening, closing = _SHELLS[language]
    separator = "\n"
    return opening + separator.join(_EMPTY[language].replace("NAME", name) for name in operations) + closing


PYTHON_CART = '''\
import decimal

TAX = decimal.Decimal("0.2")


class Cart:
    def total(self) -> None:
        subtotal = sum(line.price for line in self.lines)
        return subtotal * (1 + TAX)

    # emptying a cart keeps its customer
    def empty(self) -> None:
        self.lines.clear()
'''
TYPESCRIPT_CART = '''\
import { Decimal } from "decimal.js";

const TAX = new Decimal("0.2");

class Cart {
  total(): void {
    const subtotal = this.lines.reduce((sum, line) => sum.plus(line.price), new Decimal(0));
    return subtotal.times(TAX.plus(1));
  }

  // emptying a cart keeps its customer
  empty(): void {
    this.lines.length = 0;
  }
}
'''
JAVASCRIPT_CART = '''\
import { Decimal } from "decimal.js";

const TAX = new Decimal("0.2");

class Cart {
  total() {
    const subtotal = this.lines.reduce((sum, line) => sum.plus(line.price), new Decimal(0));
    return subtotal.times(TAX.plus(1));
  }

  // emptying a cart keeps its customer
  empty() {
    this.lines.length = 0;
  }
}
'''
# Each language's cart, with the line of total's body and the comment only the file holds.
CARTS = {
    "python": (PYTHON_CART, "        return subtotal * (1 + TAX)", "    # emptying a cart keeps its customer"),
    "typescript": (TYPESCRIPT_CART, "    return subtotal.times(TAX.plus(1));", "  // emptying a cart keeps its customer"),
    "javascript": (JAVASCRIPT_CART, "    return subtotal.times(TAX.plus(1));", "  // emptying a cart keeps its customer"),
}


def _onto(language: str, existing: str, *operations: str) -> Reshaped:
    return ReshapedCode(Format(language)).onto(existing, _shape(language, *operations))


def _lines_after(text: str, marked: str) -> list[str]:
    """The lines of text from the first line holding marked."""
    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if marked in line)
    return lines[start:]


class Cart:
    """A cart written in one language, as a person filled it with code: the file, the line of total's body and the
    comment only the file holds, and the cart as a render writes it from a model."""

    def __init__(self, language: str) -> None:
        self.language = language
        self.existing, self.body_line, self.comment = CARTS[language]

    def onto(self, existing: str, *operations: str, property: str = "") -> Reshaped:
        """existing in the shape of a model holding operations, and a property when one is named."""
        shape = _shape(self.language, *operations)
        opening = _SHELLS[self.language][0]
        if property:
            shape = shape.replace(opening, opening + self.property_line(property) + "\n\n", 1)
        return ReshapedCode(Format(self.language)).onto(existing, shape)

    def property_line(self, name: str) -> str:
        return _PROPERTY[self.language].replace("NAME", name)

    def total_taking_tax(self) -> str:
        """The opening line of total as a model writes it once total takes a tax."""
        return _TOTAL_TAKING_TAX[self.language]

    def shape_with_total_taking_tax(self) -> str:
        opening = _EMPTY[self.language].replace("NAME", "total").splitlines()[0]
        return _shape(self.language, "total", "empty").replace(opening, self.property_indent() + self.total_taking_tax(), 1)

    def property_indent(self) -> str:
        return "    " if self.language == "python" else "  "

    def reshaped(self, *operations: str) -> Reshaped:
        return self.onto(self.existing, *operations)

    def empty(self, operation: str) -> str:
        return _EMPTY[self.language].replace("NAME", operation)

    def with_order(self) -> Reshaped:
        """The file in the shape of a model that holds the cart and a class Order beside it."""
        order = _shape(self.language, "total", "empty").replace("Cart", "Order")
        return ReshapedCode(Format(self.language)).onto(self.existing, _shape(self.language, "total", "empty") + "\n\n" + order)


with shared_context("a cart that a person filled with code"):
    with context("whose model gained the operation add_line, rendered again"):
        with before.each:
            self.reshaped = self.cart.reshaped("total", "empty", "add_line")

        with it("should put the code back in total"):
            expect(self.reshaped.text.splitlines()).to(contain(self.cart.body_line))

        with it("should add add_line empty"):
            expect(self.reshaped.text).to(contain(self.cart.empty("add_line")))

        with it("should name add_line as added and nothing as kept"):
            expect((self.reshaped.added, self.reshaped.kept)).to(equal((["Cart.add_line"], [])))

        with it("should keep the import and the constant above the class"):
            expect(self.reshaped.text.splitlines()[:3]).to(equal(self.cart.existing.splitlines()[:3]))

        with it("should keep the comment between the members"):
            expect(self.reshaped.text.splitlines()).to(contain(self.cart.comment))

    with context("whose model gained the property customer_id, rendered again"):
        with before.each:
            self.reshaped = self.cart.onto(self.cart.existing, "total", "empty", property="customer_id")
            self.lines = self.reshaped.text.splitlines()

        with it("should add the property to the class, above its operations"):
            written = self.cart.property_line("customer_id")
            expect((written in self.lines, self.lines.index(written) < self.lines.index(self.cart.body_line))).to(equal((True, True)))

        with it("should name the property as added"):
            expect(self.reshaped.added).to(equal(["Cart.customer_id"]))

        with context("and rendered a second time"):
            with it("should change nothing"):
                twice = self.cart.onto(self.reshaped.text, "total", "empty", property="customer_id")
                expect((twice.text, twice.added)).to(equal((self.reshaped.text, [])))

    with context("whose model changed what total takes, rendered again"):
        with before.each:
            self.reshaped = ReshapedCode(Format(self.cart.language)).onto(self.cart.existing, self.cart.shape_with_total_taking_tax())

        with it("should keep the file's own opening line of total, since a person may have written it"):
            expect(self.reshaped.text).to(equal(self.cart.existing))

        with it("should say the model's opening line of total now differs, and give it"):
            expect(self.reshaped.changed).to(equal({"Cart.total": self.cart.total_taking_tax()}))

    with context("whose model lost the operation empty, rendered again"):
        with before.each:
            self.reshaped = self.cart.reshaped("total")
            self.apart = _lines_after(self.reshaped.text, "no longer in the model")

        with it("should mark empty as no longer in the model, by its class and name"):
            expect(self.apart[0]).to(contain("Cart.empty"))

        with it("should keep empty in the class under that line, with the comment written above it"):
            expect((self.cart.comment in self.apart, any("self.lines" in line or "this.lines" in line for line in self.apart))).to(equal((True, True)))

        with it("should name empty as kept"):
            expect(self.reshaped.kept).to(equal(["Cart.empty"]))

        with it("should hold every line the file held"):
            held = self.reshaped.text.splitlines()
            expect([line for line in self.cart.existing.splitlines() if line.strip() and line not in held]).to(be_empty)

    with context("whose model renamed total to total_price, rendered again"):
        with before.each:
            self.reshaped = self.cart.reshaped("total_price", "empty")

        with it("should name total as kept and total_price as added, for whoever migrates the body"):
            expect((self.reshaped.kept, self.reshaped.added)).to(equal((["Cart.total"], ["Cart.total_price"])))

        with it("should keep total's body under the line saying it is no longer in the model"):
            expect(_lines_after(self.reshaped.text, "no longer in the model")).to(contain(self.cart.body_line))

    with context("rendered a second time from the same model"):
        with before.each:
            self.once = self.cart.reshaped("total", "add_line").text
            self.twice = self.cart.onto(self.once, "total", "add_line")

        with it("should change nothing"):
            expect(self.twice.text).to(equal(self.once))

        with it("should still name what waits to be migrated"):
            expect(self.twice.kept).to(equal(["Cart.empty"]))

    with context("whose model holds a class the file lacks"):
        with before.each:
            self.reshaped = self.cart.with_order()

        with it("should name the class and its operations as added"):
            expect(self.reshaped.added).to(equal(["Order", "Order.empty", "Order.total"]))

        with it("should add the class after the classes the file holds"):
            expect(self.reshaped.text.index("class Order") > self.reshaped.text.index("class Cart")).to(equal(True))


with description("a render written onto a code file that is already there") as self:
    with context("in Python"):
        with before.each:
            self.cart = Cart("python")

        with included_context("a cart that a person filled with code"):
            pass

    with context("in TypeScript"):
        with before.each:
            self.cart = Cart("typescript")

        with included_context("a cart that a person filled with code"):
            pass

    with context("in JavaScript"):
        with before.each:
            self.cart = Cart("javascript")

        with included_context("a cart that a person filled with code"):
            pass

    with context("a Python class whose operation's opening line runs over several lines"):
        with it("should keep the whole operation, its opening lines and its body"):
            existing = "class Cart:\n    def total(\n        self,\n        tax: int = 2,\n    ) -> None:\n        return self.subtotal * tax\n"
            expect(_onto("python", existing, "total", "empty").text.splitlines()[:6]).to(equal(existing.splitlines()))

    with context("a class holding a helper whose name starts with an underscore, which the model does not hold"):
        with it("should leave the helper where it is, since a model names no private helper"):
            existing = "class Cart:\n    def total(self) -> None:\n        return self._rounded(5)\n\n    def _rounded(self, value):\n        return round(value)\n"
            expect(_onto("python", existing, "total")).to(equal(Reshaped(existing, [], [])))

    with context("a file that holds no class or function the render names, such as a spec of nested blocks"):
        with it("should write the rendered shape and set the file's own lines apart below it, as comments"):
            existing = 'with description("a cart"):\n    with it("should total its lines"):\n        expect(cart.total()).to(equal(5))\n'
            rendered = 'with description("a cart"):\n    with it("should total its lines"):\n        pass\n'
            reshaped = ReshapedCode(Format("python")).onto(existing, rendered)
            expect(reshaped.text).to(contain(rendered, "no longer in the model", "#         expect(cart.total()).to(equal(5))"))

        with context("rendered a second time"):
            with it("should change nothing"):
                existing = 'with description("a cart"):\n    with it("should total its lines"):\n        expect(cart.total()).to(equal(5))\n'
                rendered = 'with description("a cart"):\n    with it("should total its lines"):\n        pass\n'
                once = ReshapedCode(Format("python")).onto(existing, rendered).text
                expect(ReshapedCode(Format("python")).onto(once, rendered).text).to(equal(once))

    with context("a format that writes onto the existing text itself"):
        with it("should take what the format answers"):
            answered = Reshaped("class Cart:\n    pass\n", ["Cart.empty"], [])
            reshaped = ReshapedCode(Format("python"), lambda rendered, existing: answered).onto("class Cart:\n    pass\n", "class Cart:\n    pass\n")
            expect(reshaped).to(equal(answered))

        with context("that drops a line the file held"):
            with it("should fail, naming the line it cannot find"):
                lossy = lambda rendered, existing: Reshaped(rendered, [], [])
                onto = lambda: ReshapedCode(Format("python"), lossy).onto(PYTHON_CART, _shape("python", "total"))
                expect(onto).to(raise_error(RenderWouldLoseContent, contain("return subtotal * (1 + TAX)")))
