"""Practice-wide rules read every module folder and class in the graph at once."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    assert_files_rule_pair,
    ce_rule_by_slug,
    practice_from_files,
)


def _hits(slug: str, files: dict[str, str]) -> list[str]:
    return practice_from_files(files).hits(ce_rule_by_slug(slug))


def _module(folder: str, files: dict[str, str]) -> dict[str, str]:
    """A first-class module: a folder with its module card plus the given source files."""
    tree = {f"{folder}/.context/module-context.md": "# module\n"}
    tree.update({f"{folder}/{name}": text for name, text in files.items()})
    return tree


_CART_CLASSES = "".join(
    f"class {name}:\n    def run(self) -> int:\n        return 1\n\n\n" for name in ("Cart", "Line", "Price", "Discount", "Tax")
)


def _shop_importing(*names: str) -> dict[str, str]:
    tree = _module("cart", {"cart.py": _CART_CLASSES})
    tree.update(_module("shop", {"checkout.py": f"from cart.cart import {', '.join(names)}\n"}))
    return tree


with description("modules across the graph"):
    with context("one-way-deps"):
        with it("should report every import of a three-module cycle"):
            hits = _hits(
                "one-way-deps",
                {
                    "orders/order.py": "import billing.invoice\n",
                    "billing/invoice.py": "import ledger.entry\n",
                    "ledger/entry.py": "import orders.order\n",
                },
            )
            expect(len(hits)).to(equal(3))

        with it("should accept imports that flow one way"):
            expect(
                _hits(
                    "one-way-deps",
                    {
                        "orders/order.py": "import billing.invoice\n",
                        "billing/invoice.py": "import ledger.entry\n",
                        "ledger/entry.py": "TAX_RATE = 1\n",
                    },
                )
            ).to(equal([]))

        with it("should not count a spec's import as its module's dependency"):
            expect(
                _hits(
                    "one-way-deps",
                    {
                        "orders/order.py": "import billing.invoice\n",
                        "billing/invoice.py": "TAX_RATE = 1\n",
                        "billing/invoice_spec.py": "import orders.order\n",
                    },
                )
            ).to(equal([]))

        with it("should not read the imports of an _examples folder"):
            expect(
                _hits(
                    "one-way-deps",
                    {
                        "orders/order.py": "import billing.invoice\n",
                        "billing/invoice.py": "TAX_RATE = 1\n",
                        "billing/_examples/faulty/invoice.py": "import orders.order\n",
                    },
                )
            ).to(equal([]))

        with it("should report a cycle between two files of one folder that an import inside a function closes"):
            hits = _hits(
                "one-way-deps",
                {
                    "orders/order.py": "from orders.line import Line\n",
                    "orders/line.py": "def total():\n    from orders.order import Order\n    return Order\n",
                },
            )
            expect(hits).to(
                equal(
                    [
                        "Circular import in 'orders': 'line.py' imports 'order.py', which imports back into 'line.py' "
                        "through a cycle of 2 files; move the shared code to the file that owns it so dependencies flow one way.",
                        "Circular import in 'orders': 'order.py' imports 'line.py', which imports back into 'order.py' "
                        "through a cycle of 2 files; move the shared code to the file that owns it so dependencies flow one way.",
                    ]
                )
            )

        with it("should report a cycle that an importlib string closes"):
            hits = _hits(
                "one-way-deps",
                {
                    "orders/order.py": "import billing.invoice\n",
                    "billing/invoice.py": (
                        "import importlib\n\n_ORDERS = 'orders'\n\n\n"
                        "def order_module(name):\n    return importlib.import_module(f'{_ORDERS}.{name}')\n"
                    ),
                },
            )
            expect(len(hits)).to(equal(2))

    with context("deep-module"):
        with it("should flag a module whose classes other modules mostly import, and accept one with one public class"):
            assert_files_rule_pair(
                "deep-module",
                _shop_importing("Cart", "Line", "Price"),
                _shop_importing("Cart"),
            )

        with it("should roll a nested folder without a card up into its module"):
            tree = _module("cart", {"cart.py": "class Cart:\n    pass\n"})
            tree["cart/pricing/pricing.py"] = "class Price:\n    pass\n\n\nclass Tax:\n    pass\n"
            tree.update(_module("shop", {"checkout.py": "from cart.pricing.pricing import Price, Tax\n"}))
            expect(_hits("deep-module", tree)).to(
                equal(["Module 'cart' exposes 2 of 3 classes (67%, max 40%) to other modules: Price, Tax. Keep most classes behind a few public ones."])
            )

        with it("should not count imports from tests"):
            tree = _module("cart", {"cart.py": _CART_CLASSES})
            tree.update(_module("shop", {"checkout_spec.py": "from cart.cart import Cart, Line, Price, Discount, Tax\n"}))
            expect(_hits("deep-module", tree)).to(equal([]))

        with it("should not count a test fixture's classes among the module's classes"):
            tree = _module("cart", {"cart.py": "class Cart:\n    pass\n\n\nclass Line:\n    pass\n\n\nclass Price:\n    pass\n"})
            tree["cart/fixtures.py"] = "".join(f"class Fake{name}:\n    pass\n\n\n" for name in ("Cart", "Line", "Price", "Tax"))
            tree.update(_module("shop", {"checkout.py": "from cart.cart import Cart, Line\n"}))
            expect(_hits("deep-module", tree)).to(
                equal(["Module 'cart' exposes 2 of 3 classes (67%, max 40%) to other modules: Cart, Line. Keep most classes behind a few public ones."])
            )

        with it("should count a caller outside the validated scope"):
            practice, root = practice_from_files(_shop_importing("Cart", "Line", "Price"))
            graph = Graph()
            graph.load_files(str(root), ["clean_engineering"], ["cart"])
            scoped = graph.practice("clean_engineering")
            expect(violations_for_rule(ce_rule_by_slug("deep-module"), scoped, root)).to(
                equal(["Module 'cart' exposes 3 of 5 classes (60%, max 40%) to other modules: Cart, Line, Price. Keep most classes behind a few public ones."])
            )

    with context("source-parses"):
        with it("should report a module's Python file that does not parse"):
            assert_files_rule_pair(
                "source-parses",
                _module("cart", {"cart.py": "class Cart(:\n    pass\n"}),
                _module("cart", {"cart.py": "class Cart:\n    pass\n"}),
            )

        with it("should report a file that does not parse in a package inside the module"):
            hits = _hits("source-parses", _module("cart", {"lines/line.py": "class Line(:\n    pass\n"}))
            expect(len(hits)).to(equal(1))
