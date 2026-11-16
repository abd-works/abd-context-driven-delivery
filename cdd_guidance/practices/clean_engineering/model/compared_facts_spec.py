"""The facts that compare a node with the rest of the graph are recorded when the graph is built, saved with it, and
recorded again over the whole practice when a refresh reads only some files."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph
from harness.graph.saved_graph import SavedGraph

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files

_CARD = "# module\n"
_CART = "".join(f"class {name}:\n    def run(self) -> int:\n        return 1\n\n\n" for name in ("Cart", "Line", "Price"))
_EXPOSURE = ("subtree_class_count", "public_classes", "public_class_count", "private_class_count")


def _shop(*names: str) -> dict[str, str]:
    return {
        "cart/.context/module-context.md": _CARD,
        "cart/cart.py": _CART,
        "shop/.context/module-context.md": _CARD,
        "shop/checkout.py": f"from cart.cart import {', '.join(names)}\n",
    }


def _module(fixture, name: str):
    return next(node for node in fixture.practice.reading.in_graph.nodes("Module") if node.name == name)


def _exposure(module) -> dict:
    return {key: module.get_fact(key) for key in _EXPOSURE}


def _read_back(graph: Graph):
    """A graph opened from the saved text of graph, as a session opens its saved graph."""
    restored = Graph()
    restored.practices.of(CleanEngineering)
    restored.restored_from(SavedGraph.from_text(SavedGraph.from_graph(graph).text))
    return restored.practices.of(CleanEngineering).reading.in_graph


with description("compared facts"):
    with context("with a module two of whose classes another module imports"):
        with before.all:
            self.fixture = practice_from_files(_shop("Cart", "Line"))
            self.cart = _module(self.fixture, "cart")
            self.restored = next(node for node in _read_back(self.fixture.practice.reading.graph).nodes("Module") if node.name == "cart")

        with it("should record on the module its classes, its public classes with the modules that name them, and its counts"):
            expect(_exposure(self.cart)).to(
                equal(
                    {
                        "subtree_class_count": 3,
                        "public_classes": {"Cart": ["shop"], "Line": ["shop"]},
                        "public_class_count": 2,
                        "private_class_count": 1,
                    }
                )
            )

        with it("should keep the facts in a graph read back from its saved file"):
            expect(_exposure(self.restored)).to(equal(_exposure(self.cart)))

    with context("with a refresh of the importing file alone"):
        with before.all:
            self.fixture = practice_from_files(_shop("Cart", "Line"))
            (self.fixture.root / "shop/checkout.py").write_text("from cart.cart import Cart\n", encoding="utf-8")
            self.fixture.practice.reading.graph.refresh([str(self.fixture.root / "shop/checkout.py")])
            self.cart = _module(self.fixture, "cart")

        with it("should record again the facts of the module the refresh did not read"):
            expect(self.cart.get_fact("public_classes")).to(equal({"Cart": ["shop"]}))

    with context("with a class whose operations only forward to another class"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    "shop/cart.py": "class Cart:\n    def total(self) -> int:\n        return 1\n",
                    "shop/till.py": "class Till:\n    def total(self, cart) -> int:\n        return cart.total()\n",
                }
            )
            self.till = next(node for node in self.fixture.practice.reading.in_graph.nodes("OoadClass") if node.name == "Till")
            restored = _read_back(self.fixture.practice.reading.graph)
            self.restored = next(node for node in restored.nodes("OoadClass") if node.name == "Till")

        with it("should record on the class the class it forwards to"):
            expect(self.till.get_fact("forwards_to")).to(equal("Cart"))

        with it("should keep it in a graph read back from its saved file"):
            expect(self.restored.get_fact("forwards_to")).to(equal("Cart"))
