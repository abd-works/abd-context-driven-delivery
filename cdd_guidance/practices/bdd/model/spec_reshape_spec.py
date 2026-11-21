"""Specs for a rendered describe tree written onto a spec file that is already there: the file takes the tree's shape
and keeps every body, setup, helper and comment it holds. The behaviours are written once and run for Python,
TypeScript and JavaScript, each on a cart's spec written in that language."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_empty, contain, equal, expect
from mamba import before, context, description, included_context, it, shared_context

from cdd_guidance.practices.bdd.bdd import Bdd
from harness.guidance.practice_formats import Reshaped

PYTHON_SPEC = '''\
from mamba import before, description, context, it
from expects import expect, equal


def _cart_with(*prices):
    return Cart(prices)


with description("a cart") as self:
    with before.each:
        self.cart = _cart_with(2, 3)

    # totals include every line
    with it("should total its lines"):
        expect(self.cart.total()).to(equal(5))

    with context("that is empty"):
        with it("should total zero"):
            expect(_cart_with().total()).to(equal(0))
'''
SCRIPT_SPEC = '''\
import { beforeEach, describe, expect, it } from "vitest";

function cartWith(...prices) {
  return new Cart(prices);
}

describe("a cart", () => {
  let cart;

  beforeEach(() => {
    cart = cartWith(2, 3);
  });

  // totals include every line
  it("should total its lines", () => {
    expect(cart.total()).toBe(5);
  });

  describe("that is empty", () => {
    it("should total zero", () => {
      expect(cartWith().total()).toBe(0);
    });
  });
});
'''
# The describe tree as a render writes it, each observation holding only its signature marker.
PYTHON_TREE = {
    "open": 'with description("a cart"):\n',
    "it": '    with it("{name}"):\n        pass  # BDD: SIGNATURE\n',
    "context": '    with context("that is empty"):\n        with it("should total zero"):\n            pass  # BDD: SIGNATURE\n',
    "close": "",
}
SCRIPT_TREE = {
    "open": 'describe("a cart", () => {\n',
    "it": '  it("{name}", () => {\n    // BDD: SIGNATURE\n  });\n',
    "context": '  describe("that is empty", () => {\n    it("should total zero", () => {\n      // BDD: SIGNATURE\n    });\n  });\n',
    "close": "});\n",
}
SPECS = {
    "python": (PYTHON_SPEC, PYTHON_TREE, "        expect(self.cart.total()).to(equal(5))", "    # totals include every line", "        self.cart = _cart_with(2, 3)"),
    "typescript": (SCRIPT_SPEC, SCRIPT_TREE, "    expect(cart.total()).toBe(5);", "  // totals include every line", "    cart = cartWith(2, 3);"),
    "javascript": (SCRIPT_SPEC, SCRIPT_TREE, "    expect(cart.total()).toBe(5);", "  // totals include every line", "    cart = cartWith(2, 3);"),
}
REFUSES = "should refuse a book out of stock"


class CartSpec:
    """A cart's spec written in one language, as a person filled it: the file, a line of an observation's body, the
    comment and the setup line only the file holds, and the describe tree as a render writes it."""

    def __init__(self, language: str) -> None:
        self.language = language
        self.existing, self._tree, self.body_line, self.comment, self.setup_line = SPECS[language]

    def tree(self, *observations: str, with_context: bool = True) -> str:
        """The cart's describe tree holding observations, and its empty-cart context unless left out."""
        written = "\n".join(self._tree["it"].replace("{name}", name) for name in observations)
        nested = ("\n" + self._tree["context"]) if with_context else ""
        return self._tree["open"] + written + nested + self._tree["close"]

    def onto(self, existing: str, rendered: str) -> Reshaped:
        return Bdd().formats.adapter(self.language).reshape(rendered, existing)

    def marker(self) -> str:
        return "BDD: SIGNATURE"


def _lines_from(text: str, marked: str) -> list[str]:
    lines = text.splitlines()
    start = next(index for index, line in enumerate(lines) if marked in line)
    return lines[start:]


with shared_context("a cart's spec that a person filled with bodies"):
    with context("whose tree gained an observation, rendered again"):
        with before.each:
            self.reshaped = self.spec.onto(self.spec.existing, self.spec.tree("should total its lines", REFUSES))
            self.lines = self.reshaped.text.splitlines()

        with it("should keep the body of the observation both hold"):
            expect(self.lines).to(contain(self.spec.body_line))

        with it("should add the new observation with its signature marker"):
            added = _lines_from(self.reshaped.text, REFUSES)
            expect(self.spec.marker() in added[0] + added[1]).to(equal(True))

        with it("should add it inside the description, before the description ends"):
            expect(self.reshaped.text.index(REFUSES) > self.reshaped.text.index("should total its lines")).to(equal(True))

        with it("should name it as added, by its describe, and nothing as kept"):
            expect((self.reshaped.added, self.reshaped.kept)).to(equal(([f"a cart {REFUSES}"], [])))

        with it("should keep the setup where it was"):
            expect(self.lines.index(self.spec.setup_line) < self.lines.index(self.spec.body_line)).to(equal(True))

        with it("should keep the helper and the imports above the description"):
            expect(self.lines[:6]).to(equal(self.spec.existing.splitlines()[:6]))

        with it("should keep the comment above the observation"):
            expect(self.lines).to(contain(self.spec.comment))

    with context("whose tree lost its empty-cart context, rendered again"):
        with before.each:
            self.reshaped = self.spec.onto(self.spec.existing, self.spec.tree("should total its lines", with_context=False))

        with it("should keep the context where it is, under a line saying it is no longer in the model"):
            marked = _lines_from(self.reshaped.text, "no longer in the model")
            expect(("a cart that is empty" in marked[0], "that is empty" in marked[1])).to(equal((True, True)))

        with it("should name the context as kept"):
            expect(self.reshaped.kept).to(equal(["a cart that is empty"]))

        with it("should hold every line the file held"):
            held = self.reshaped.text.splitlines()
            expect([line for line in self.spec.existing.splitlines() if line.strip() and line not in held]).to(be_empty)

    with context("whose tree renamed an observation, rendered again"):
        with before.each:
            self.reshaped = self.spec.onto(self.spec.existing, self.spec.tree("should total every line"))

        with it("should name the old observation as kept and the new one as added, for whoever migrates the body"):
            expect((self.reshaped.kept, self.reshaped.added)).to(equal((["a cart should total its lines"], ["a cart should total every line"])))

    with context("rendered a second time from the same tree"):
        with before.each:
            self.tree = self.spec.tree(REFUSES, with_context=False)
            self.once = self.spec.onto(self.spec.existing, self.tree).text
            self.twice = self.spec.onto(self.once, self.tree)

        with it("should change nothing"):
            expect(self.twice.text).to(equal(self.once))

        with it("should still name what waits to be migrated"):
            expect(self.twice.kept).to(equal(["a cart should total its lines", "a cart that is empty"]))

    with context("whose tree holds a description the file lacks"):
        with before.each:
            order = self.spec.tree("should total its lines", with_context=False).replace("a cart", "an order")
            self.reshaped = self.spec.onto(self.spec.existing, self.spec.tree("should total its lines") + "\n\n" + order)

        with it("should add the description after the ones the file holds"):
            expect((self.reshaped.added, self.reshaped.text.index("an order") > self.reshaped.text.index("that is empty"))).to(equal((["an order should total its lines"], True)))


with description("a describe tree rendered onto a spec file that is already there") as self:
    with context("in Python"):
        with before.each:
            self.spec = CartSpec("python")

        with included_context("a cart's spec that a person filled with bodies"):
            pass

    with context("in TypeScript"):
        with before.each:
            self.spec = CartSpec("typescript")

        with included_context("a cart's spec that a person filled with bodies"):
            pass

    with context("in JavaScript"):
        with before.each:
            self.spec = CartSpec("javascript")

        with included_context("a cart's spec that a person filled with bodies"):
            pass
