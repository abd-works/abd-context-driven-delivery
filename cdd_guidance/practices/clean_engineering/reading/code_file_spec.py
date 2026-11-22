"""A file of the code read resolves what a span of its code calls: the one resolver both Clean Engineering's members and
BDD's observations ask, so an invokes edge means the same member whichever practice draws it."""

import shutil
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph  # noqa: E402

import cdd_guidance.practices  # noqa: E402,F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.clean_engineering.reading.code_file import CodeSpan  # noqa: E402
from cdd_guidance.practices.source_code import ClassReference  # noqa: E402

_CART = """\
class CartLine:
    def __init__(self, sku: str) -> None:
        self.sku = sku

    @property
    def quantity(self) -> int:
        return 1


class Cart:
    def __init__(self) -> None:
        self.lines: list[CartLine] = []

    @property
    def total(self) -> int:
        return 0

    def add(self, sku: str) -> CartLine:
        line = CartLine(sku)
        self.lines.append(line)
        return line
"""

_CART_SCRIPT = """\
export class Cart {
  add(sku: string): void {}
}
"""

_FILES = {"shop/cart.py": _CART, "shop/cart.ts": _CART_SCRIPT}


def _named(members) -> list[str]:
    """Each member as its owner and name: `Cart.add`."""
    return [f"{member.get_fact('owner')}.{member.name}" for member in members]


with description("a file of the code read"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp())
        for path, text in _FILES.items():
            (self.folder / path).parent.mkdir(parents=True, exist_ok=True)
            (self.folder / path).write_text(text, encoding="utf-8")
        graph = Graph()
        graph.load_files(str(self.folder), ["clean_engineering"], ["shop"])
        self.index = graph.practices.named("clean_engineering").reading.code_index
        self.spec_file = self.index.file("shop/cart_spec.py", [ClassReference("shop/cart", "Cart")])

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("whose span builds a class by its name"):
        with it("should invoke the class's constructor"):
            expect(_named(self.spec_file.members_called_in(CodeSpan("cart = Cart()")))).to(equal(["Cart.__init__"]))

    with context("whose span reads a getter"):
        with it("should invoke the getter"):
            span = CodeSpan("expect(cart.total)", before="cart = Cart()")
            expect(_named(self.spec_file.members_called_in(span))).to(equal(["Cart.total"]))

    with context("whose span uses a local a call answered"):
        with it("should read the local as the class the called operation returns"):
            span = CodeSpan("line = cart.add('a')\nexpect(line.quantity)", before="cart = Cart()")
            expect(_named(self.spec_file.members_called_in(span))).to(equal(["Cart.add", "CartLine.quantity"]))

    with context("whose code before the span opens a block on the line above a built local"):
        with it("should type the local, not the block's name"):
            span = CodeSpan("cart.add('a')", before="with before.each:\n    cart = Cart()")
            expect(_named(self.spec_file.members_called_in(span))).to(equal(["Cart.add"]))

    with context("written in a script that imports a module both languages hold"):
        with it("should name the script's class, not the Python one"):
            script = self.index.file("shop/cart.spec.ts", [ClassReference("shop/cart", "Cart")])
            expect(script.class_named("Cart").source.file).to(equal("shop/cart.ts"))
