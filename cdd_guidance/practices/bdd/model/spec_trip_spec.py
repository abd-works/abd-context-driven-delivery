"""A BDD spec taken to another format and back holds what it held: its order, its call graphs, its test bodies."""

import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import cdd_guidance.practices  # noqa: F401
from cdd_guidance.practices.bdd.bdd import Bdd

_CART_PYTHON = '''\
from expects import equal, expect
from mamba import before, context, description, it

from shop.cart import Cart


with description("a cart"):
    with before.each:
        self.cart = Cart()

    with context("with a book added"):
        with before.each:
            self.cart.add("Dune")

        with it("should hold one line for the book"):
            expect(self.cart.lines).to(equal(["Dune"]))

        with it("should total the book's price"):
            expect(self.cart.total).to(equal(12))

        with context("that has the same book added again"):
            with before.each:
                self.cart.add("Dune")

            with it("should total twice the book's price"):
                expect(self.cart.total).to(equal(24))
'''

_CART_TYPESCRIPT = """\
import { beforeEach, describe, expect, it } from "vitest";

import { Cart } from "../src/cart";

describe("a cart", () => {
  let cart: Cart;

  beforeEach(() => {
    cart = new Cart();
  });

  describe("with a book added", () => {
    it("should hold one line for the book", () => {
      expect(cart.lines).toEqual(["Dune"]);
    });
  });
});
"""

_CART_TREE = """\
a cart
  with a book added
    it should hold one line for the book
    it should total the book's price
    that has the same book added again
      it should total twice the book's price
"""

_STATE_BEFORE_OBSERVATION = """\
a cart
  with a book added
    that has the same book added again
      it should total twice the book's price
    it should hold one line for the book
"""

_ORDER_REALIZATION_TREE = """\
an order
  that has been placed from a cart
    ```
    order.status
      <- str
    it should await payment
    ```
    with a payment taken
      ```
      order.pay(amount)
        -> Payment(amount)
        <- Payment
      order.is_paid
        <- bool
      it should be paid
      ```
"""

_ORDER_REALIZATION_PYTHON = '''\
from mamba import description, context, it
from expects import expect


with description("an order"):
    with context("that has been placed from a cart"):
        with it("should await payment"):
            # order.status
            #   <- str
            pass  # BDD: SIGNATURE

        with context("with a payment taken"):
            with it("should be paid"):
                # order.pay(amount)
                #   -> Payment(amount)
                #   <- Payment
                # order.is_paid
                #   <- bool
                pass  # BDD: SIGNATURE
'''

_ORDER_REALIZATION_TYPESCRIPT_IT = """\
    it("should await payment", () => {
      // order.status
      //   <- str
      // BDD: SIGNATURE
    });
"""

_CART_BEHAVIOR_SKETCH = """\
Fidelity: behavior

## behavior driven development:

### a cart

#### that is new

```
it should hold no lines
it should total zero
```

#### with a book added

```
it should hold one line for the book
```

##### that has the same book added again

```
it should total twice the book's price
```
"""

_CART_REALIZATION_SKETCH = """\
Fidelity: realization

## behavior driven development:

### a cart

#### with a book added

```
-> cart.add(book)
  -> CartLine(book)
  <- CartLine
it should hold one line for the book
```

```
cart.total
  -> line.total
it should total the price of the book
```
"""

_SESSION_SKETCH = """\
# Bookshop sketch

## clean engineering:

### **Cart**

+ add(book: Book): CartLine

## behavior driven development:

### a cart

#### that is new

```
it should hold no lines
```
"""


def _render(target: str, content: str, source: str, fidelity: str = "behavior") -> str:
    return Bdd(fidelity=fidelity).render(target, content, source=source).content


def _observation(content: str, source: str, path: tuple):
    return Bdd.format_adapters[source]().parse(content).node_at(path)


with description("a spec taken to another format and back"):
    with context("that is a finished python spec taken to typescript"):
        with before.all:
            self.typescript = _render("typescript", _CART_PYTHON, "python", "development")
            self.back = _render("python", self.typescript, "typescript", "development")

        with it("should keep the python imports as a note under the typescript imports"):
            expect(self.typescript).to(contain("// python body to translate:\n// from expects import equal, expect"))

        with it("should come back to python as it was written"):
            expect(self.back).to(equal(_CART_PYTHON))

    with context("that is a finished typescript spec taken to python"):
        with before.all:
            self.python = _render("python", _CART_TYPESCRIPT, "typescript", "development")
            self.back = _render("typescript", self.python, "python", "development")

        with it("should come back to typescript as it was written"):
            expect(self.back).to(equal(_CART_TYPESCRIPT))

    with context("that is a python spec taken to typescript and back twice"):
        with it("should hold the same lines after the second trip as after the first"):
            once = _render("typescript", _CART_PYTHON, "python", "development")
            twice = _render("typescript", _render("python", once, "typescript", "development"), "python", "development")
            expect(twice).to(equal(once))

    with context("that holds two observations before a nested state"):
        with it("should keep the observations above the nested state from the tree to python"):
            rendered = _render("python", _CART_TREE, "markdown")
            expect(rendered.index("should total the book's price") < rendered.index("that has the same book added again")).to(
                equal(True)
            )

        with it("should come back from python as the same tree"):
            expect(_render("markdown", _render("python", _CART_TREE, "markdown"), "python")).to(equal(_CART_TREE))

        with it("should come back from typescript as the same tree"):
            expect(_render("markdown", _render("typescript", _CART_TREE, "markdown"), "typescript")).to(equal(_CART_TREE))

    with context("that holds a nested state before an observation"):
        with it("should keep the state above the observation through python"):
            rendered = _render("markdown", _render("python", _STATE_BEFORE_OBSERVATION, "markdown"), "python")
            expect(rendered).to(equal(_STATE_BEFORE_OBSERVATION))

    with context("that is a realization tree"):
        with it("should write each call graph as comments above the python signature marker"):
            expect(_render("python", _ORDER_REALIZATION_TREE, "markdown", "realization")).to(equal(_ORDER_REALIZATION_PYTHON))

        with it("should come back from python with each call graph under its observation"):
            python = _render("python", _ORDER_REALIZATION_TREE, "markdown", "realization")
            expect(_render("markdown", python, "python", "realization")).to(equal(_ORDER_REALIZATION_TREE))

        with it("should come back from typescript with each call graph under its observation"):
            typescript = _render("typescript", _ORDER_REALIZATION_TREE, "markdown", "realization")
            expect(_render("markdown", typescript, "typescript", "realization")).to(equal(_ORDER_REALIZATION_TREE))

        with it("should come back from a sketch with the call lines no further in"):
            sketch = _render("sketch", _ORDER_REALIZATION_TREE, "markdown", "realization")
            expect(_render("markdown", sketch, "sketch", "realization")).to(equal(_ORDER_REALIZATION_TREE))

    with context("that is a python realization spec"):
        with it("should hold each call graph as the same lines in typescript comments"):
            expect(_render("typescript", _ORDER_REALIZATION_PYTHON, "python", "realization")).to(
                contain(_ORDER_REALIZATION_TYPESCRIPT_IT)
            )

        with it("should come back from typescript as it was written"):
            typescript = _render("typescript", _ORDER_REALIZATION_PYTHON, "python", "realization")
            expect(_render("python", typescript, "typescript", "realization")).to(equal(_ORDER_REALIZATION_PYTHON))

        with it("should be written back to python as it was read"):
            expect(_render("python", _ORDER_REALIZATION_PYTHON, "python", "realization")).to(equal(_ORDER_REALIZATION_PYTHON))


with description("a sketch in the heading notation of the sketch template"):
    with context("that holds a call graph above each observation in its own fence"):
        with before.all:
            self.path = ("a cart", "with a book added")

        with it("should give the first observation the calls of its own fence"):
            first = _observation(_CART_REALIZATION_SKETCH, "sketch", (*self.path, "should hold one line for the book"))
            expect([(entry.depth, entry.kind, entry.text) for entry in first.call_graph]).to(
                equal([(0, "out", "cart.add(book)"), (1, "out", "CartLine(book)"), (1, "in", "CartLine")])
            )

        with it("should give the second observation the calls of its own fence"):
            second = _observation(_CART_REALIZATION_SKETCH, "sketch", (*self.path, "should total the price of the book"))
            expect([(entry.depth, entry.kind, entry.text) for entry in second.call_graph]).to(
                equal([(0, "call", "cart.total"), (1, "out", "line.total")])
            )

        with it("should read no call line as a state"):
            state = _observation(_CART_REALIZATION_SKETCH, "sketch", self.path)
            expect([nested.name for nested in state.contexts]).to(equal([]))

    with context("that is rendered to python and back to a sketch"):
        with it("should come back in the heading notation it was written in"):
            python = _render("python", _CART_BEHAVIOR_SKETCH, "sketch")
            expect(_render("sketch", python, "python")).to(equal(_CART_BEHAVIOR_SKETCH))

    with context("that holds a realization and is rendered to a sketch"):
        with it("should come back with each call graph in a fence above its observation"):
            expect(_render("sketch", _CART_REALIZATION_SKETCH, "sketch", "realization")).to(equal(_CART_REALIZATION_SKETCH))

    with context("that is one section of a session's sketch"):
        with it("should render the behavior section alone, under its own heading"):
            expect(_render("sketch", _SESSION_SKETCH, "sketch")).to(
                equal("Fidelity: behavior\n\n## behavior driven development:\n\n### a cart\n\n#### that is new\n\n```\nit should hold no lines\n```\n")
            )
