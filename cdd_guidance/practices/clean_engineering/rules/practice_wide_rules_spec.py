"""Practice-wide rules read every module folder and class in the graph at once."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    assert_files_rule_pair,
    ce_rule_by_slug,
    practice_from_files,
    violations_for_rule,
)


def _hits(slug: str, files: dict[str, str]) -> list[str]:
    return violations_for_rule(ce_rule_by_slug(slug), *practice_from_files(files))


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
