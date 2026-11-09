"""A BDD observation invokes the operations its realization starts from, so the graph can draw that realization."""

import shutil
import sys
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from harness.graph.graph import Graph  # noqa: E402
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_CART = """\
export class Cart {
  add(item: string): void {}

  get count(): number {
    return 0
  }
}
"""

_CART_SPEC = """\
import { beforeEach, describe, expect, it } from 'vitest'

describe('a cart', () => {
  describe('with an item added', () => {
    beforeEach(() => cart.add('apple'))

    it('should count one item', () => {
      expect(cart.count).toBe(1)
    })
  })
})
"""

_BASKET = """\
class Basket:
    def checkout(self) -> None:
        pass
"""

_BASKET_SPEC = """\
from mamba import before, description, it

with description("a basket"):
    with before.each:
        self.receipt = self.tools.call("basket.checkout", basket="b1")

    with it("should give a receipt"):
        pass
"""


def _invoked(graph: Graph, observation: str) -> list[str]:
    node = next(node for node in graph.practice("bdd").reading.in_graph.nodes() if node.type == "Observation" and node.name == observation)
    group = next((child for child in node.children if child.name == "invokes"), None)
    return [child.node_id.rsplit(":", 2)[-2] + ":" + child.node_id.rsplit(":", 1)[-1] for child in (group.children if group else [])]


with description("a bdd observation"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp())
        (self.folder / "src").mkdir()
        for name, text in (("cart.ts", _CART), ("cart.spec.ts", _CART_SPEC), ("basket.py", _BASKET), ("basket_spec.py", _BASKET_SPEC)):
            (self.folder / "src" / name).write_text(text, encoding="utf-8")
        self.graph = Graph()
        self.graph.load_files(str(self.folder), ["bdd", "clean_engineering"], ["src"])

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("under a context whose setup acts"):
        with it("should invoke the setup's operation, then what the observation reads"):
            expect(_invoked(self.graph, "should count one item")).to(equal(["add:Cart", "count:Cart"]))

    with context("that calls a tool by its name"):
        with it("should invoke that toolset's operation, not the call that carries it"):
            expect(_invoked(self.graph, "should give a receipt")).to(equal(["checkout:Basket"]))
