"""A class model rendered to code keeps every body it can, in every language, through one render."""

import sys
from pathlib import Path

from expects import be_true, contain, equal, expect, have_key
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import cdd_guidance.practices  # noqa: F401
from cdd_guidance.practices.source_code import JAVASCRIPT, PYTHON, TYPESCRIPT, CodeBody
from harness.agent_tools.agent_tools import AgentToolSet, ToolsetReference

_TOOLSET = "cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering"

_CART_PYTHON = '''\
from __future__ import annotations

from decimal import Decimal


class Cart:
    """A shopper's cart."""

    items: list

    def __init__(self, items: list) -> None:
        self.items = items

    def total(self) -> Decimal:
        """The sum of the item prices."""
        # an empty cart totals zero
        return sum((item.price for item in self.items), Decimal("0"))

    def add(self, item: object) -> None:
        self.items.append(item)
'''

_CART_TYPESCRIPT = """\
class Cart {
  items: Item[];

  constructor(items: Item[]) {
    this.items = items;
  }

  total(): number {
    // an empty cart totals zero
    return this.items.reduce((sum, item) => sum + item.price, 0);
  }
}
"""

_CART_MARKDOWN = """\
# Shop

*Shop* is the cart module.

## Cart

*Cart* holds line items.

Cart(items: list)
------
items: list
----
total(): Decimal
empty(): None
"""

_ACCOUNT_MARKDOWN = """# Accounts

*Accounts* opens accounts.

## Accounts

*Accounts* opens an account.

------
----
new_account(credentials?: AccountCredentials): AccountCredentials
"""

_PYTHON_TOTAL = 'return sum((item.price for item in self.items), Decimal("0"))'
_TYPESCRIPT_TOTAL = "return this.items.reduce((sum, item) => sum + item.price, 0);"


def _render(target: str, content: str, source: str, previous: str = "") -> str:
    toolset = type(ToolsetReference.parsed(_TOOLSET).made())(fidelity="model")
    return toolset.render(format=target, content=content, source=source, previous=previous).content


def _bodies(language: str, text: str) -> dict:
    from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

    adapter = CleanEngineering(fidelity="model").formats.adapter(language)
    model = adapter.parse(text)
    return {
        f"{oclass.name}.{operation.name}": operation.body.text
        for oclass in model.every_class()
        for operation in oclass.operations
    }


_LANGUAGES = {"python": PYTHON, "typescript": TYPESCRIPT, "javascript": JAVASCRIPT}

with description("an operation body"):
    with context("that was read from python"):
        with before.each:
            self.body = CodeBody("self.items.append(item)", PYTHON)

        with context("that is written back in python"):
            with it("should keep the statements as read"):
                expect(self.body.lines_in(PYTHON, "        ", "raise NotImplementedError")).to(
                    equal(["        self.items.append(item)"])
                )

        with context("that is written in typescript"):
            with before.each:
                typescript = TYPESCRIPT
                self.lines = self.body.lines_in(typescript, "    ", typescript.unfinished)

            with it("should keep the python statements commented out under a note naming python"):
                expect(self.lines[:2]).to(equal(["    // python body to translate:", "    // self.items.append(item)"]))

            with it("should end with the line that fails until the body is written"):
                expect(self.lines[-1]).to(equal(f"    {TYPESCRIPT.unfinished}"))

    with context("that holds a multi-line string starting at the left margin"):
        with it("should move the code lines and leave the string's lines as written"):
            body = CodeBody('    text = """\nfirst\n  second\n"""\n    return text', PYTHON)
            expect(body.lines_in(PYTHON, "        ", "")).to(
                equal(['        text = """', "first", "  second", '"""', "        return text"])
            )

    with context("that is only a placeholder"):
        with it("should be empty"):
            expect(CodeBody("...", PYTHON).is_empty).to(be_true)

    with context("that is empty"):
        with it("should write only the line that marks it still to write"):
            expect(CodeBody("", None).lines_in(TYPESCRIPT, "    ", "// BDD: SIGNATURE")).to(
                equal(["    // BDD: SIGNATURE"])
            )

    with context("that is kept against the previous file's body"):
        with before.each:
            self.python = PYTHON
            self.previous = CodeBody("return 1", self.python)

        with context("with a model body in the target language"):
            with it("should keep the model body"):
                newer = CodeBody("return 2", self.python)
                expect(newer.in_language_of(self.previous, self.python).text).to(equal("return 2"))

        with context("with a model body from another language"):
            with it("should keep the previous file's body"):
                other = CodeBody("return 2;", TYPESCRIPT)
                expect(other.in_language_of(self.previous, self.python).text).to(equal("return 1"))


with description("a class model rendered to code"):
    with context("that was read from a python file"):
        with context("that is rendered back to python"):
            with before.each:
                self.rendered = _render("python", _CART_PYTHON, "python")

            with it("should keep each operation's statements"):
                expect(self.rendered).to(contain(f"        {_PYTHON_TOTAL}"))

            with it("should keep the comments inside an operation"):
                expect(self.rendered).to(contain("        # an empty cart totals zero"))

            with it("should keep the imports above the first class"):
                expect(self.rendered).to(contain("from decimal import Decimal"))

            with it("should read back the same bodies"):
                expect(_bodies("python", self.rendered)).to(equal(_bodies("python", _CART_PYTHON)))

            with it("should render the same text again"):
                expect(_render("python", self.rendered, "python")).to(equal(self.rendered))

        with context("that is rendered to typescript"):
            with before.each:
                self.rendered = _render("typescript", _CART_PYTHON, "python")

            with it("should carry each python body as a commented note inside its operation"):
                expect(self.rendered).to(contain(f"    // {_PYTHON_TOTAL}"))

            with it("should make each operation fail until it is written"):
                expect(self.rendered).to(contain(f"    {TYPESCRIPT.unfinished}"))

    with context("that was read from a typescript file"):
        with context("that is rendered back to typescript"):
            with before.each:
                self.rendered = _render("typescript", _CART_TYPESCRIPT, "typescript")

            with it("should keep each method's statements"):
                expect(self.rendered).to(contain(f"    {_TYPESCRIPT_TOTAL}"))

            with it("should read back the same bodies"):
                expect(_bodies("typescript", self.rendered)).to(equal(_bodies("typescript", _CART_TYPESCRIPT)))

        with context("that is rendered to javascript"):
            with it("should carry each typescript body as a commented note inside its method"):
                expect(_render("javascript", _CART_TYPESCRIPT, "typescript")).to(contain(f"    // {_TYPESCRIPT_TOTAL}"))

    with context("that was read from markdown"):
        with context("that is rendered to python with the previous python file"):
            with before.each:
                self.rendered = _render("python", _CART_MARKDOWN, "markdown", previous=_CART_PYTHON)

            with it("should keep the previous file's body for an operation the model still has"):
                expect(self.rendered).to(contain(f"        {_PYTHON_TOTAL}"))

            with it("should make an operation new to the model fail until it is written"):
                expect(self.rendered).to(contain("    def empty(self) -> None:\n        raise NotImplementedError"))

        with context("with a parameter the model marks as one a caller may leave out"):
            with before.each:
                self.rendered = _render("python", _ACCOUNT_MARKDOWN, "markdown")

            with it("should write the parameter the way Python does, with no value when left out"):
                expect(self.rendered).to(contain("def new_account(self, credentials: AccountCredentials | None = None) -> AccountCredentials:"))

            with it("should write a file Python parses"):
                expect(_bodies("python", self.rendered)).to(have_key("Accounts.new_account"))

        with context("that is rendered to each code language"):
            with it("should make every operation fail until it is written, in each language"):
                languages = tuple(_LANGUAGES)
                unfinished = [
                    _LANGUAGES[language].unfinished in _render(language, _CART_MARKDOWN, "markdown")
                    for language in languages
                ]
                expect(unfinished).to(equal([True] * len(languages)))


with description("a body written in one language and kept as comments in another") as self:
    with before.each:
        from cdd_guidance.practices.source_code import PYTHON, TYPESCRIPT, CodeBody

        self.python = CodeBody("self.items.append(item)\nreturn item", PYTHON)
        self.kept = "\n".join(self.python.lines_in(TYPESCRIPT, "    ", ""))
        self.read_back = CodeBody.from_written(self.kept, TYPESCRIPT)
        self.own = CodeBody.from_written("// add the item\nthis.items.push(item);", TYPESCRIPT)

    with it("should read back as the body in the language it was written in"):
        expect((self.read_back.language.name, self.read_back.text)).to(equal(("python", "self.items.append(item)\nreturn item")))

    with it("should read a body with comments of its own as that language's body"):
        expect((self.own.language.name, self.own.text)).to(equal(("typescript", "// add the item\nthis.items.push(item);")))


# Seen 2026-11-21 (r3-widget-07): a render of Python code to TypeScript declared no property, imported nothing, called
# no base constructor, and extended Python's ValueError, so the file did not compile.
_BOOKSHOP_CODE = Path(__file__).resolve().parent / "fixtures" / "bookshop" / "code"


def _bookshop_in_typescript(file: str) -> str:
    return _render("typescript", (_BOOKSHOP_CODE / file).read_text(encoding="utf-8"), "python")


with description("Python code rendered to TypeScript"):
    with context("whose constructor assigns fields the class does not declare"):
        with before.all:
            self.rendered = _bookshop_in_typescript("ordering/cart.py")

        with it("should declare a field typed as its assignment writes it, in TypeScript's spelling"):
            expect(self.rendered).to(contain("  lines: CartLine[];"))

        with it("should declare a field typed as the parameter it is assigned from"):
            expect(self.rendered).to(contain("  customerId: string;"))

        with it("should import the classes the file uses from other files"):
            expect(self.rendered).to(contain('import { Book, OutOfStock } from "src/catalogue/book";'))

        with it("should extend TypeScript's Error where Python extends ValueError"):
            expect(self.rendered).to(contain("class EmptyCart extends Error {"))

    with context("whose subclass's constructor calls its base class's constructor"):
        with before.all:
            self.rendered = _bookshop_in_typescript("fulfilment/shipment.py")
            self.express = self.rendered[self.rendered.index("class ExpressShipment"):]

        with it("should call the base class's constructor with the arguments the Python passes"):
            expect(self.express).to(contain("    super(order, address);\n"))

        with it("should assign only the fields the base class does not"):
            expect(self.express).not_to(contain("this.order = order;"))


with description("a markdown class model rendered to TypeScript"):
    with before.all:
        model = (Path(__file__).resolve().parent / "fixtures" / "bookshop" / "ordering-model.md").read_text(encoding="utf-8")
        self.rendered = _render("typescript", model, "markdown")

    with it("should write a list property as a TypeScript array"):
        expect(self.rendered).to(contain("  lines: CartLine[];"))

    with it("should write a parameter's type in TypeScript's spelling"):
        expect(self.rendered).to(contain("  add(book: Book, quantity: number): CartLine {"))

    with it("should write a call the model notes as the operation is named in TypeScript"):
        expect(self.rendered).to(contain("    Book.isInStock();"))


# Requested 2026-11-24 (r3-bolt-07, r3-widget-07): a body written in code is translated into the other language,
# statement by statement, not carried over as a comment; a statement outside what translates is the only one kept so.
_CART_WITH_BODIES = '''\
class OutOfStock(ValueError):
    """A book that cannot be added."""


class Cart:
    """The books a customer has chosen."""

    def __init__(self, customer_id: str) -> None:
        self.customer_id = customer_id
        self.lines: list[CartLine] = []

    def add(self, book: Book, quantity: int) -> CartLine:
        """Add a line for the book; a book out of stock is refused."""
        # a book out of stock is refused
        if quantity <= 0 or not book.is_in_stock(quantity):
            raise OutOfStock(f"{book.title} is out of stock")
        for line in self.lines:
            if line.book is book:
                line.quantity += quantity
                return line
        line = CartLine(book, quantity)
        self.lines.append(line)
        return line

    def is_empty(self) -> bool:
        return len(self.lines) == 0

    def titles(self) -> list[str]:
        return [line.book.title for line in self.lines if line.quantity > 0]

    def total(self) -> int:
        return sum(line.subtotal() for line in self.lines)
'''

_ADD_IN_TYPESCRIPT = """\
  add(book: Book, quantity: number): CartLine {
    // a book out of stock is refused
    if (quantity <= 0 || !book.isInStock(quantity)) {
      throw new OutOfStock(`${book.title} is out of stock`);
    }
    for (const line of this.lines) {
      if (line.book === book) {
        line.quantity += quantity;
        return line;
      }
    }
    const line = new CartLine(book, quantity);
    this.lines.push(line);
    return line;
  }
"""

_CART_IN_TYPESCRIPT = """\
class Cart {
  lines: CartLine[];

  constructor(lines: CartLine[]) {
    this.lines = lines;
  }

  count(): number {
    let counted = 0;
    for (const line of this.lines) {
      if (line.quantity > 0 && line.book !== null) {
        counted += line.quantity;
      }
    }
    return counted;
  }

  named(title: string): CartLine[] {
    return this.lines.filter((line) => line.book.title === title);
  }
}
"""

_COUNT_IN_PYTHON = """\
    def count(self) -> float:
        counted = 0
        for line in self.lines:
            if line.quantity > 0 and line.book is not None:
                counted += line.quantity
        return counted
"""


with description("a body written in code, rendered into the other language"):
    with context("from Python to TypeScript"):
        with before.all:
            self.rendered = _render("typescript", _CART_WITH_BODIES, "python")

        with it("should translate a guard, a loop, a raise, a local and a call, statement by statement"):
            expect(self.rendered).to(contain(_ADD_IN_TYPESCRIPT))

        with it("should translate the constructor's assignments into the constructor"):
            expect(self.rendered).to(contain("  constructor(customerId: string) {\n    this.customerId = customerId;\n    this.lines = [];\n  }\n"))

        with it("should translate len into length"):
            expect(self.rendered).to(contain("    return this.lines.length === 0;\n"))

        with it("should translate a list comprehension into filter and map"):
            expect(self.rendered).to(contain("    return this.lines.filter((line) => line.quantity > 0).map((line) => line.book.title);\n"))

        with it("should keep a statement it cannot translate as Python under a note that names it"):
            expect(self.rendered).to(contain("    // python statement to translate:\n    // return sum(line.subtotal() for line in self.lines)\n"))

        with it("should leave no whole body to translate"):
            expect(self.rendered).not_to(contain("python body to translate"))

    with context("from Python to TypeScript and back"):
        with before.all:
            self.back = _render("python", _render("typescript", _CART_WITH_BODIES, "python"), "typescript")

        with it("should come back as Python statements"):
            expect(self.back).to(contain(
                "        if quantity <= 0 or not book.isInStock(quantity):\n"
                "            raise OutOfStock(f'{book.title} is out of stock')\n"
                "        for line in self.lines:\n"
                "            if line.book == book:\n"
            ))

        with it("should keep the note above the statement it was written over"):
            expect(self.back).to(contain("        # a book out of stock is refused\n        if quantity"))

        with it("should leave no whole body to translate"):
            expect(self.back).not_to(contain("body to translate"))

    with context("from TypeScript to Python"):
        with before.all:
            self.rendered = _render("python", _CART_IN_TYPESCRIPT, "typescript")

        with it("should translate a local, a loop, a guard and an addition"):
            expect(self.rendered).to(contain(_COUNT_IN_PYTHON))

        with it("should translate filter into a list comprehension"):
            expect(self.rendered).to(contain("        return [line for line in self.lines if line.book.title == title]\n"))
