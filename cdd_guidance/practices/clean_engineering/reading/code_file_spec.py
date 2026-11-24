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
from cdd_guidance.practices.clean_engineering.model import MODULE_FUNCTION_HOLDER  # noqa: E402
from cdd_guidance.practices.clean_engineering.reading.code_file import CodeSpan  # noqa: E402
from cdd_guidance.practices.source_code import ClassReference  # noqa: E402

_CART = """\
from typing import Any


class Till:
    def open(self) -> None:
        pass


class CartLine:
    def __init__(self, sku: str) -> None:
        self.sku = sku

    @property
    def quantity(self) -> int:
        return 1

    @property
    def parent(self) -> "Cart":
        return Cart()


class Cart:
    def __init__(self) -> None:
        self.lines: list[CartLine] = []
        self.till = Till()

    @property
    def total(self) -> int:
        return 0

    def add(self, sku: str) -> CartLine:
        line = CartLine(sku)
        self.lines.append(line)
        return line

    def emptied(self):
        self.lines = []
        return self

    def anything(self) -> Any:
        return self

    def __getitem__(self, index: int) -> CartLine:
        return self.lines[index]


class GiftCart(Cart):
    def wrap(self) -> None:
        pass


class _Basket:
    def weigh(self) -> int:
        return 0


# A class that writes the same names, so a name alone does not say which class's member a call reaches.
class Crate:
    def add(self, sku: str) -> None:
        pass

    @property
    def quantity(self) -> int:
        return 2

    def open(self) -> None:
        pass

    def weigh(self) -> int:
        return 9


def filled_cart():
    cart = Cart()
    cart.add("a")
    return cart


def opened_shop():
    return Cart(), CartLine("a")


CART = Cart()
"""

# A package that passes on a class its own module declares.
_PACKAGE = """\
from shop.cart import Cart
"""

_CART_SCRIPT = """\
export class Till {
  open(): void {}
}

export class Cart {
  readonly till = new Till();

  add(sku: string): void {}
}

export class Crate {
  add(sku: string): void {}

  open(): void {}
}
"""

# A script spec's own helpers: one whose return type is an object of named fields, one that writes no return type.
_CART_SCRIPT_SPEC = """\
import { Cart } from './cart'

async function opened(): Promise<{ cart: Cart; stop: () => void }> {
  return { cart: new Cart(), stop: () => {} }
}

function filled() {
  const cart = new Cart()
  return { cart }
}
"""

# A spec that declares a helper inside its describe block, which the code read does not index.
_CART_SPEC = """\
from pathlib import Path

from shop.cart import Cart

with description("a cart"):
    def filled(self) -> Cart:
        return Cart()
"""

_FILES = {
    "shop/cart.py": _CART,
    "shop/__init__.py": _PACKAGE,
    "shop/cart.ts": _CART_SCRIPT,
    "shop/cart.spec.ts": _CART_SCRIPT_SPEC,
    "shop/cart_spec.py": _CART_SPEC,
}


def _named(members) -> list[str]:
    """Each member as its owner and name, `Cart.add`, and a module's function by its name alone."""
    return [member.name if member.get_fact("owner") == MODULE_FUNCTION_HOLDER else f"{member.get_fact('owner')}.{member.name}" for member in members]


with description("a file of the code read"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp())
        for path, text in _FILES.items():
            (self.folder / path).parent.mkdir(parents=True, exist_ok=True)
            (self.folder / path).write_text(text, encoding="utf-8")
        graph = Graph()
        graph.load_files(str(self.folder), ["clean_engineering"], ["shop"])
        self.index = graph.practices.named("clean_engineering").reading.code_index
        self.spec_file = self.index.file(
            "shop/cart_spec.py",
            [ClassReference("shop/cart", name) for name in ("Cart", "GiftCart", "_Basket", "filled_cart", "opened_shop", "CART")],
        )
        self.called = lambda text, before="": _named(self.spec_file.members_called_in(CodeSpan(CodeSpan.code_of(text), before=before)))
        self.script = self.index.file("shop/cart.spec.ts", [ClassReference("shop/cart", "Cart")])
        self.script_called = lambda text, before="": _named(self.script.members_called_in(CodeSpan(CodeSpan.code_of(text), before=before)))

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("whose span builds a class by its name"):
        with it("should invoke the class's constructor"):
            expect(self.called("cart = Cart()")).to(equal(["Cart.__init__"]))

    with context("whose span reads a getter"):
        with it("should invoke the getter"):
            expect(self.called("expect(cart.total)", "cart = Cart()")).to(equal(["Cart.total"]))

    with context("whose span uses a local a call answered"):
        with it("should read the local as the class the called operation returns"):
            expect(self.called("line = cart.add('a')\nexpect(line.quantity)", "cart = Cart()")).to(equal(["Cart.add", "CartLine.quantity"]))

    with context("whose code before the span opens a block on the line above a built local"):
        with it("should type the local, not the block's name"):
            expect(self.called("cart.add('a')", "with before.each:\n    cart = Cart()")).to(equal(["Cart.add"]))

    with context("written in a script that imports a module both languages hold"):
        with it("should name the script's class, not the Python one"):
            script = self.index.file("shop/cart.spec.ts", [ClassReference("shop/cart", "Cart")])
            expect(script.class_named("Cart").source.file).to(equal("shop/cart.ts"))

    with context("whose span follows a chain through a call's answer"):
        with it("should reach the member of the class the call answers"):
            expect(self.called("expect(Cart().add('a').quantity)")).to(equal(["Cart.add", "CartLine.quantity", "Cart.__init__"]))

    with context("whose span calls a function that writes no return type"):
        with it("should read the call as what the function's return statement answers"):
            expect(self.called("filled_cart().add('b')")).to(equal(["Cart.add", "filled_cart"]))

    with context("whose span takes a tuple apart"):
        with it("should type each local by its part of the tuple the function returns"):
            expect(self.called("cart, line = opened_shop()\nexpect(line.quantity)")).to(equal(["CartLine.quantity", "opened_shop"]))

    with context("whose span reads a field the constructor assigns without a type hint"):
        with it("should reach the member of the class the constructor assigns it"):
            expect(self.called("cart.till.open()", "cart = Cart()")).to(equal(["Cart.till", "Till.open"]))

    with context("whose span calls a module variable its import names"):
        with it("should reach the member of the class the module assigns it"):
            expect(self.called("CART.add('a')")).to(equal(["Cart.add"]))

    with context("whose span calls an inherited operation that answers its own object"):
        with it("should read the answer as the receiver's own class"):
            expect(self.called("GiftCart().emptied().wrap()")).to(equal(["Cart.emptied", "GiftCart.wrap"]))

    with context("whose span calls an operation whose return type says Any"):
        with it("should reach nothing through its answer"):
            expect(self.called("cart.anything().add('a')", "cart = Cart()")).to(equal(["Cart.anything"]))

    with context("whose span takes an item of an object"):
        with it("should read the item as what the class's __getitem__ returns"):
            expect(self.called("expect(cart[0].quantity)", "cart = Cart()")).to(equal(["CartLine.quantity"]))

    with context("whose span assigns a local the value of a condition"):
        with it("should type the local by the value it holds when the condition holds"):
            expect(self.called("cart = Cart() if ready else None\ncart.add('a')")).to(equal(["Cart.add", "Cart.__init__"]))

    with context("whose span opens a block on an object"):
        with it("should type the block's local by the object"):
            expect(self.called("with Cart() as cart:\n    cart.add('a')")).to(equal(["Cart.add", "Cart.__init__"]))

    with context("whose code writes a comment sign inside a string and a comment on a line of its own"):
        with it("should keep the string and every line after the comment as code"):
            expect(CodeSpan.code_of("label = '# one'\n# the cart\ncart.add('a')")).to(equal("label = '# one'\n\ncart.add('a')"))

    with context("whose span builds a class whose name starts with an underscore"):
        with it("should invoke its constructor's class and type the local by it"):
            expect(self.called("basket = _Basket()\nbasket.weigh()")).to(equal(["_Basket.weigh"]))

    with context("whose span reads a member the local's class neither declares nor inherits"):
        with it("should reach the one member of that name its reach declares"):
            expect(self.called("basket = _Basket()\nbasket.wrap()")).to(equal(["GiftCart.wrap"]))

    with context("whose span follows a chain of three or more parts from a local of no known class"):
        with it("should reach the member one class declares, then follow the chain through what it holds"):
            expect(self.called("cart.till.open()")).to(equal(["Cart.till", "Till.open"]))

        with it("should follow the chain through what that member answers when called"):
            expect(self.called("cart.emptied().till.open()")).to(equal(["Cart.emptied", "Cart.till", "Till.open"]))

        with it("should reach nothing when two classes declare the member the chain opens with"):
            expect(self.called("cart.add('a').quantity")).to(equal([]))

    with context("whose span follows a chain of three or more parts from an object from outside the code read"):
        with it("should reach no member of the code's classes"):
            expect(self.called("folder = Path('shop')\nfolder.parent.till.open()")).to(equal([]))

        with it("should read an operator on that object as an object from outside the code too"):
            expect(self.called("handlers = Path('shop') / 'a.json'\nhandlers.parent.till.open()")).to(equal([]))

    with context("whose span builds a class through the module it imports"):
        with it("should invoke the constructor and reach the class's member"):
            module_file = self.index.file("shop/cart_spec.py", [ClassReference("shop/cart", "Cart")])
            called = module_file.members_called_in(CodeSpan("shop.Cart().add('a')"))
            expect(_named(called)).to(equal(["Cart.__init__", "Cart.add"]))

    with context("whose import names a package that passes the class on"):
        with it("should name the class the package's module declares"):
            through_package = self.index.file("checkout_spec.py", [ClassReference("shop", "Cart")])
            expect(through_package.class_named("Cart").source.file).to(equal("shop/cart.py"))

    with context("whose span calls a helper the spec declares inside its describe block"):
        with it("should read the call as the class the helper's hint names"):
            expect(self.called("filled().add('a')")).to(equal(["Cart.add"]))

    with context("written in a script whose helper answers an object of named fields"):
        with it("should type each local the script takes out of it by its field's type"):
            expect(self.script_called("const { cart } = await opened()\ncart.add('a')")).to(equal(["Cart.add", "opened"]))

    with context("written in a script whose helper returns an object literal with no return type"):
        with it("should type the local by the field's value"):
            expect(self.script_called("const { cart } = filled()\ncart.add('a')")).to(equal(["Cart.add", "filled"]))

    with context("written in a script that reads a field its class starts with a value"):
        with it("should reach the member of the class the field starts as"):
            expect(self.script_called("cart.till.open()", "const cart = new Cart()")).to(equal(["Cart.till", "Till.open"]))
