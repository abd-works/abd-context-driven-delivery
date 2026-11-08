"""The describe, context, it, and test calls of a script spec: each call adopts the calls nested in its own callback and
answers which describe-tree block it is."""

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.bdd.model.code_spec_model import DescribeCalls

_SPEC = """import { describe, it } from "vitest";

describe("a cart", () => {
  describe("with one line", () => {
    it("should total the line", () => {
      describe("inside a test body", () => {});
    });
  });
  it("should start empty", () => { expect(cart.total).toBe(0); });
});
"""

with description("the describe calls of a script spec"):
    with before.all:
        self.calls = DescribeCalls(_SPEC)
        self.cart = self.calls.describes[0]

    with it("should hold the outermost describe as the spec's description"):
        expect([call.name for call in self.calls.describes]).to(equal(["a cart"]))

    with it("should have each describe adopt the calls straight inside its callback"):
        expect([call.name for call in self.cart.children]).to(equal(["with one line", "should start empty"]))

    with it("should leave a call inside a test body to that body"):
        expect(self.cart.children[0].children[0].children).to(equal([]))

    with context("with a nested describe"):
        with it("should read as a context"):
            expect(self.cart.children[0].behavior_kind).to(equal("context"))

    with context("with an it"):
        with it("should read as an observation"):
            expect(self.cart.children[1].behavior_kind).to(equal("it"))

        with it("should know its callback opens and closes on one line"):
            expect(self.cart.children[1].is_inline).to(equal(True))

        with it("should span its own lines of the file"):
            expect(self.cart.children[1].whole_lines).to(equal(['  it("should start empty", () => { expect(cart.total).toBe(0); });']))
