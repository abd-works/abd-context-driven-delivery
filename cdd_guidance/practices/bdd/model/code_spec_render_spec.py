"""A BDD spec rendered to code keeps every test body and setup it can, in every language, through one render."""

import ast
import sys
from pathlib import Path

from expects import be_true, contain, equal, expect
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

    with context("that has been created"):
        with it("should hold no items"):
            expect(self.cart.items).to(equal([]))

    with context("with an item added"):
        with before.each:
            self.cart.add("apple")

        with it("should hold the item"):
            expect(self.cart.items).to(equal(["apple"]))
'''

_CART_TYPESCRIPT = """\
import { beforeEach, describe, expect, it } from "vitest";

import { Cart } from "../src/cart";

describe("a cart", () => {
  let cart: Cart;

  beforeEach(() => {
    cart = new Cart();
  });

  describe("that has been created", () => {
    it("should hold no items", () => {
      expect(cart.items).toEqual([]);
    });
  });
});
"""

_HAND_WRITTEN_PYTHON = '''\
from mamba import description, it


with description("a receipt") as self:
    with it(
        "should print the store name "
        "above the lines"
    ):
        expect(render()).to(start_with(_HEADER))
    with it("should be empty when nothing was bought"): pass


_HEADER = """\\
SHOP
----
"""


with description("a refund"):

    # the refund reuses the receipt layout
    with description("that has been printed"):
        with it("should say refund"):
            expect(render()).to(contain("REFUND"))
'''

_HAND_WRITTEN_TYPESCRIPT = """\
import { expect, it } from "vitest";

it("loads the fixtures", () => {
  expect(fixtures()).toBeTruthy();
});

describe('a receipt', () => {
  it('should print the store name', () => { expect(render()).toContain('SHOP'); });
  host.it('is not a test block', () => {});
})
"""

_CART_SKETCH = """\
a cart
  that has been created
    it should hold no items
  with an item added
    it should hold the item
    it should count one item
"""

_CART_REALIZATION = """\
a cart
  that has been created
    ```
    -> cart.items
    it should hold no items
    ```
"""

_PYTHON_ASSERT = "expect(self.cart.items).to(equal([]))"


def _render(target: str, content: str, source: str, previous: str = "") -> str:
    return Bdd().render(target, content, source=source, previous=previous)["content"]


with description("a spec rendered to code"):
    with context("that was read from a python spec"):
        with context("that is rendered back to python"):
            with before.each:
                self.rendered = _render("python", _CART_PYTHON, "python")

            with it("should write the spec back as it was read"):
                expect(self.rendered).to(equal(_CART_PYTHON))

        with context("that is rendered to typescript"):
            with before.each:
                self.rendered = _render("typescript", _CART_PYTHON, "python")

            with it("should carry each python test body commented out inside its it"):
                expect(self.rendered).to(contain(f"      // {_PYTHON_ASSERT}"))

            with it("should carry each python setup commented out inside its describe"):
                expect(self.rendered).to(contain("  // with before.each:\n  //     self.cart = Cart()"))

            with it("should open with typescript imports, not the python ones"):
                expect(self.rendered.splitlines()[0]).to(equal('import { describe, it } from "vitest";'))

            with it("should mark each it as still to write"):
                expect(self.rendered.count("// BDD: SIGNATURE")).to(equal(2))

        with context("with hand-written openings, code between descriptions, and one-line blocks"):
            with context("that is rendered back to python"):
                with it("should write the spec back as it was read"):
                    expect(_render("python", _HAND_WRITTEN_PYTHON, "python")).to(equal(_HAND_WRITTEN_PYTHON))

    with context("that was read from a typescript spec"):
        with context("that is rendered back to typescript"):
            with it("should write the spec back as it was read"):
                expect(_render("typescript", _CART_TYPESCRIPT, "typescript")).to(equal(_CART_TYPESCRIPT))

        with context("with a test outside every describe, one-line blocks, and a member call named it"):
            with context("that is rendered back to typescript"):
                with it("should write the spec back as it was read"):
                    expect(_render("typescript", _HAND_WRITTEN_TYPESCRIPT, "typescript")).to(
                        equal(_HAND_WRITTEN_TYPESCRIPT)
                    )

    with context("that was read from a sketch"):
        with context("that is rendered to python"):
            with before.each:
                self.rendered = _render("python", _CART_SKETCH, "markdown")

            with it("should be python that parses"):
                ast.parse(self.rendered)
                expect(True).to(be_true)

            with it("should mark each it as still to write"):
                expect(self.rendered.count("pass  # BDD: SIGNATURE")).to(equal(3))

        with context("with a realization call graph that is rendered to python"):
            with it("should write the call graph as comments above the marker"):
                expect(_render("python", _CART_REALIZATION, "markdown")).to(
                    contain("            # -> cart.items\n            pass  # BDD: SIGNATURE")
                )

        with context("that is rendered to python with the previous python spec"):
            with before.each:
                self.rendered = _render("python", _CART_SKETCH, "markdown", previous=_CART_PYTHON)

            with it("should keep the previous file's body for an it the sketch still has"):
                expect(self.rendered).to(contain(f"            {_PYTHON_ASSERT}"))

            with it("should keep the previous file's setup for a context the sketch still has"):
                expect(self.rendered).to(contain('            self.cart.add("apple")'))

            with it("should mark an it new to the sketch as still to write"):
                expect(self.rendered).to(
                    contain('        with it("should count one item"):\n            pass  # BDD: SIGNATURE')
                )
