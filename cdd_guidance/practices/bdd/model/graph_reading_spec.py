"""A spec read into the graph is linked to the code its own imports name: each observation to the operations and
properties it drives, each describe to the class it describes."""

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

_BOOK = """\
class Book:
    def __init__(self, title: str, price: int) -> None:
        self.title = title
        self.price = price
"""

_CART = """\
from src.catalogue.book import Book


class CartLine:
    def __init__(self, book: Book) -> None:
        self._book = book
        self._quantity = 1

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def total(self) -> int:
        return self._book.price * self._quantity


class Cart:
    def __init__(self) -> None:
        self._lines: list[CartLine] = []

    @property
    def lines(self) -> list[CartLine]:
        return list(self._lines)

    @property
    def total(self) -> int:
        return sum(line.total for line in self._lines)

    def add(self, book: Book) -> CartLine:
        line = CartLine(book)
        self._lines.append(line)
        return line
"""

_ORDER = """\
from src.ordering.cart import Cart, CartLine


class Order:
    def __init__(self, cart: Cart) -> None:
        self._lines = cart.lines
        self._paid = False

    @property
    def lines(self) -> list[CartLine]:
        return list(self._lines)

    @property
    def is_paid(self) -> bool:
        return self._paid

    def pay(self, amount: int) -> None:
        self._paid = True
"""

# A class of the same name in another folder, as a domain model's code sits beside the production code.
_OTHER_ORDER = """\
class Order:
    @property
    def is_paid(self) -> bool:
        return False

    def pay(self, amount: int) -> None:
        pass
"""

_CHECKOUT_VIEW = """\
def pay(amount: int) -> None:
    pass
"""

_CART_SPEC = """\
from mamba import description, context, it, before
from expects import equal, expect, have_length

from src.catalogue.book import Book
from src.ordering.cart import Cart

with description('a cart'):
    with before.each:
        self.cart = Cart()
        self.book = Book('Dune', 12)

    with context('that is new'):
        with it('should total zero'):
            expect(self.cart.total).to(equal(0))

    with context('with a book added'):
        with before.each:
            self.line = self.cart.add(self.book)

        with it("should count one of the book"):
            expect(self.line.quantity).to(equal(1))
"""

_ORDER_SPEC = """\
from mamba import description, context, it, before
from expects import be_true, expect, have_length

from src.catalogue.book import Book
from src.ordering.cart import Cart
from src.ordering.order import Order

with description('an order'):
    with before.each:
        self.cart = Cart()
        self.cart.add(Book('Dune', 12))

    with context('that has been placed from a cart'):
        with before.each:
            self.order = Order(self.cart)

        with it('should hold a line for each cart line'):
            expect(self.order.lines).to(have_length(1))

        with context('with a payment taken'):
            with before.each:
                self.order.pay(12)

            with it('should be paid'):
                expect(self.order.is_paid).to(be_true)
"""

# A spec whose describe cleans up after each observation, as a teardown does, in a block of its own.
_UNPAID_ORDER_SPEC = """\
from mamba import after, before, description, it
from expects import be_false, expect

from src.ordering.cart import Cart
from src.ordering.order import Order

with description('an unpaid order'):
    with before.each:
        self.order = Order(Cart())

    with after.each:
        self.order.pay(0)

    with it('should not be paid'):
        expect(self.order.is_paid).to(be_false)
"""

_ORDER_SCRIPT = """\
export class Order {
  private paid = false;

  get isPaid(): boolean {
    return this.paid;
  }

  pay(amount: number): void {
    this.paid = true;
  }
}
"""

_ORDER_SCRIPT_SPEC = """\
import { beforeEach, describe, expect, it } from "vitest";
import { Order } from "./order";

describe("an order", () => {
  let order: Order;

  beforeEach(() => {
    order = new Order();
  });

  describe("with a payment taken", () => {
    beforeEach(() => {
      order.pay(12);
    });

    it("should be paid", () => {
      expect(order.isPaid).toBe(true);
    });
  });
});
"""

# Test support that drives the code under test, and a spec whose observation only calls it.
_ORDER_EXAMPLES = """from src.ordering.cart import Cart
from src.ordering.order import Order


def check_paid_order(amount):
    order = Order(Cart())
    order.pay(amount)
    assert order.is_paid
"""

_PAID_ORDER_SPEC = """from mamba import description, it

from src.checks.order_examples import check_paid_order

with description('a paid order'):
    with it('should be paid'):
        check_paid_order(12)
"""

_FILES = {
    "src/catalogue/book.py": _BOOK,
    "src/checks/order_examples.py": _ORDER_EXAMPLES,
    "src/ordering/paid_order_spec.py": _PAID_ORDER_SPEC,
    "src/ordering/cart.py": _CART,
    "src/ordering/order.py": _ORDER,
    "src/ordering/cart_spec.py": _CART_SPEC,
    "src/ordering/order_spec.py": _ORDER_SPEC,
    "src/ordering/unpaid_order_spec.py": _UNPAID_ORDER_SPEC,
    "src/ordering/order.ts": _ORDER_SCRIPT,
    "src/ordering/order.spec.ts": _ORDER_SCRIPT_SPEC,
    "src/checkout_view.py": _CHECKOUT_VIEW,
    "ordering/order/order.py": _OTHER_ORDER,
    "ordering/order/order.ts": _ORDER_SCRIPT,
}


def _member(node) -> str:
    """A code node as its file, name, and class: `src/ordering/order.py:pay:Order`."""
    return node.node_id.split(":", 2)[2]


def _linked(graph: Graph, kind: str, spec: str, block: str) -> list[str]:
    nodes = graph.practices.named("bdd").reading.in_graph.nodes()
    node = next(node for node in nodes if node.name == block and node.source.file == spec)
    return [_member(edge.child) for edge in graph.edges.from_parent(kind, node)]


with description("a spec read into the graph beside the code it drives"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp())
        for path, text in _FILES.items():
            (self.folder / path).parent.mkdir(parents=True, exist_ok=True)
            (self.folder / path).write_text(text, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_files(str(self.folder), ["bdd", "clean_engineering"], ["src", "ordering"])

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("with a class of the same name in another folder"):
        with it("should link an observation to the operation of the class its spec imports"):
            expect(_linked(self.graph, "invokes", "src/ordering/order_spec.py", "should be paid")).to(
                equal(["src/ordering/order.py:pay:Order", "src/ordering/order.py:is_paid:Order"])
            )

        with it("should link a script observation to the operation of the class its spec imports"):
            expect(_linked(self.graph, "invokes", "src/ordering/order.spec.ts", "should be paid")).to(
                equal(["src/ordering/order.ts:pay:Order", "src/ordering/order.ts:isPaid:Order"])
            )

    with context("with a property two of its imported classes name"):
        with it("should link the read to the class the spec built the receiver as"):
            expect(_linked(self.graph, "invokes", "src/ordering/cart_spec.py", "should total zero")).to(
                equal(["src/ordering/cart.py:__init__:Cart", "src/catalogue/book.py:__init__:Book", "src/ordering/cart.py:total:Cart"])
            )

        with it("should link a read whose receiver no setup built to the one class that owns the name"):
            expect(_linked(self.graph, "invokes", "src/ordering/cart_spec.py", "should count one of the book")).to(
                equal(["src/ordering/cart.py:add:Cart", "src/ordering/cart.py:quantity:CartLine"])
            )

    with context("under a state whose setup only constructs"):
        with it("should start from the nearest setup's constructor, not an outer setup's call"):
            expect(_linked(self.graph, "invokes", "src/ordering/order_spec.py", "should hold a line for each cart line")).to(
                equal(["src/ordering/order.py:__init__:Order", "src/ordering/order.py:lines:Order"])
            )

    with context("whose describe cleans up after each observation"):
        with it("should start from the setup's calls, not the cleanup's"):
            expect(_linked(self.graph, "invokes", "src/ordering/unpaid_order_spec.py", "should not be paid")).to(
                equal(["src/ordering/order.py:__init__:Order", "src/ordering/cart.py:__init__:Cart", "src/ordering/order.py:is_paid:Order"])
            )

    with context("whose observation calls only test support that drives the code"):
        with it("should link the observation to the members the test support invokes"):
            expect(_linked(self.graph, "invokes", "src/ordering/paid_order_spec.py", "should be paid")).to(
                equal(["src/ordering/order.py:pay:Order", "src/ordering/order.py:is_paid:Order", "src/ordering/order.py:__init__:Order", "src/ordering/cart.py:__init__:Cart"])
            )

    with context("whose describe names a class its spec imports"):
        with it("should link the describe to that class"):
            expect(_linked(self.graph, "alignsWith", "src/ordering/order_spec.py", "an order")).to(
                equal(["src/ordering/order.py:Order"])
            )

        with it("should link a script describe to the class its spec imports"):
            expect(_linked(self.graph, "alignsWith", "src/ordering/order.spec.ts", "an order")).to(
                equal(["src/ordering/order.ts:Order"])
            )


_STATES_AND_OBSERVATIONS_IN_TURN = """\
from mamba import context, description, it

with description("a shelf"):
    with it("should start empty"):
        pass

    with context("with a book"):
        with it("should hold one book"):
            pass

    with it("should name its section"):
        pass
"""


with description("a describe that writes observations and states in turn, read into the graph"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp())
        (self.folder / "shelf_spec.py").write_text(_STATES_AND_OBSERVATIONS_IN_TURN, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_files(str(self.folder), ["bdd"], ["shelf_spec.py"])

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with it("should list them in the order the spec writes them, not its observations first"):
        shelf = next(node for node in self.graph.practices.named("bdd").reading.in_graph.nodes("Description") if node.name == "a shelf")
        expect([child.name for child in shelf.children]).to(equal(["should start empty", "with a book", "should name its section"]))


with description("a spec saved with a byte that is not UTF-8, read into the graph"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp())
        (self.folder / "cafe_spec.py").write_bytes(
            b"# caf\xe9 menu\nfrom mamba import description, it\n\nwith description('a menu'):\n    with it('should list a dish'):\n        pass\n"
        )
        self.graph = Graph()
        self.graph.load_files(str(self.folder), ["bdd"], ["cafe_spec.py"])

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with it("should still read its describe tree, the byte read as a replacement character"):
        names = [node.name for node in self.graph.practices.named("bdd").reading.in_graph.nodes("Observation")]
        expect(names).to(equal(["should list a dish"]))
