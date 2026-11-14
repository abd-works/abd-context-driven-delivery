"""Practice-wide rules read every module folder and class in the graph at once."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it


from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    ce_rule_by_slug,
    files_rule_pair,
    practice_from_files,
)


def _hits(slug: str, fixture) -> list[str]:
    return fixture.hits(ce_rule_by_slug(slug))


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
    # Each fixture builds a graph, so every context builds its fixtures once, before its examples, which only run the rules.
    with context("one-way-deps"):
        with before.all:
            self.three_module_cycle = practice_from_files(
                {
                    "orders/order.py": "import billing.invoice\n",
                    "billing/invoice.py": "import ledger.entry\n",
                    "ledger/entry.py": "import orders.order\n",
                }
            )
            self.one_way = practice_from_files(
                {
                    "orders/order.py": "import billing.invoice\n",
                    "billing/invoice.py": "import ledger.entry\n",
                    "ledger/entry.py": "TAX_RATE = 1\n",
                }
            )
            self.spec_import = practice_from_files(
                {
                    "orders/order.py": "import billing.invoice\n",
                    "billing/invoice.py": "TAX_RATE = 1\n",
                    "billing/invoice_spec.py": "import orders.order\n",
                }
            )
            self.examples_import = practice_from_files(
                {
                    "orders/order.py": "import billing.invoice\n",
                    "billing/invoice.py": "TAX_RATE = 1\n",
                    "billing/_examples/faulty/invoice.py": "import orders.order\n",
                }
            )
            self.function_import = practice_from_files(
                {
                    "orders/order.py": "from orders.line import Line\n",
                    "orders/line.py": "def total():\n    from orders.order import Order\n    return Order\n",
                }
            )
            self.importlib_string = practice_from_files(
                {
                    "orders/order.py": "import billing.invoice\n",
                    "billing/invoice.py": (
                        "import importlib\n\n_ORDERS = 'orders'\n\n\n"
                        "def order_module(name):\n    return importlib.import_module(f'{_ORDERS}.{name}')\n"
                    ),
                }
            )

        with it("should report every import of a three-module cycle"):
            expect(len(_hits("one-way-deps", self.three_module_cycle))).to(equal(3))

        with it("should accept imports that flow one way"):
            expect(_hits("one-way-deps", self.one_way)).to(equal([]))

        with it("should not count a spec's import as its module's dependency"):
            expect(_hits("one-way-deps", self.spec_import)).to(equal([]))

        with it("should not read the imports of an _examples folder"):
            expect(_hits("one-way-deps", self.examples_import)).to(equal([]))

        with it("should report a cycle between two files of one folder that an import inside a function closes"):
            expect(_hits("one-way-deps", self.function_import)).to(
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
            expect(len(_hits("one-way-deps", self.importlib_string))).to(equal(2))

    with context("deep-module"):
        with before.all:
            self.mostly_imported = files_rule_pair(
                "deep-module",
                _shop_importing("Cart", "Line", "Price"),
                _shop_importing("Cart"),
            )
            importing = _module("shop", {"checkout.py": "from sketch.outline import SketchOutline, DiscoveryDocument\n"})
            classes = "class SketchOutline:\n    def lines(self) -> list:\n        return []\n\n\nclass DiscoveryDocument:\n    pass\n\n\n"
            self.private_record = files_rule_pair(
                "deep-module",
                {**_module("sketch", {"outline.py": classes + "class Section:\n    pass\n"}), **importing},
                {**_module("sketch", {"outline.py": classes + "class _Section:\n    pass\n"}), **importing},
            )
            tree = _module("cart", {"cart.py": "class Cart:\n    pass\n"})
            tree["cart/pricing/pricing.py"] = "class Price:\n    pass\n\n\nclass Tax:\n    pass\n"
            tree.update(_module("shop", {"checkout.py": "from cart.pricing.pricing import Price, Tax\n"}))
            self.nested_folder = practice_from_files(tree)
            tree = _module("cart", {"cart.py": _CART_CLASSES})
            tree.update(_module("shop", {"checkout_spec.py": "from cart.cart import Cart, Line, Price, Discount, Tax\n"}))
            self.test_imports = practice_from_files(tree)
            tree = _module("cart", {"cart.py": "class Cart:\n    pass\n\n\nclass Line:\n    pass\n\n\nclass Price:\n    pass\n"})
            tree["cart/fixtures.py"] = "".join(f"class Fake{name}:\n    pass\n\n\n" for name in ("Cart", "Line", "Price", "Tax"))
            tree.update(_module("shop", {"checkout.py": "from cart.cart import Cart, Line\n"}))
            self.test_fixture_classes = practice_from_files(tree)
            names = [f"Part{index}" for index in range(109)]
            tree = _module("cart", {"cart.py": "".join(f"class {name}:\n    pass\n\n\n" for name in names)})
            tree.update(_module("shop", {"checkout.py": f"from cart.cart import {', '.join(names[:44])}\n"}))
            self.just_over = practice_from_files(tree)
            self.outside_scope = practice_from_files(_shop_importing("Cart", "Line", "Price"))
            self.outside_scope.read_only(["cart"])

        with it("should flag a module whose classes other modules mostly import, and accept one with one public class"):
            self.mostly_imported.check()

        with it("should flag a module of three classes with two public and accept two public classes beside a private record"):
            self.private_record.check()

        with it("should roll a nested folder without a card up into its module"):
            expect(_hits("deep-module", self.nested_folder)).to(
                equal(["Module 'cart' exposes 2 of 3 classes to other modules, more than the 1 that 40% allows: Price, Tax. Keep most classes behind a few public ones."])
            )

        with it("should not count imports from tests"):
            expect(_hits("deep-module", self.test_imports)).to(equal([]))

        with it("should not count a test fixture's classes among the module's classes"):
            expect(_hits("deep-module", self.test_fixture_classes)).to(
                equal(["Module 'cart' exposes 2 of 3 classes to other modules, more than the 1 that 40% allows: Cart, Line. Keep most classes behind a few public ones."])
            )

        with it("should name the allowed count when the share is just over 40%, which rounds to 40"):
            expect(_hits("deep-module", self.just_over)[0].split(":")[0]).to(
                equal("Module 'cart' exposes 44 of 109 classes to other modules, more than the 43 that 40% allows")
            )

        with it("should count a caller outside the validated scope"):
            expect(_hits("deep-module", self.outside_scope)).to(
                equal(["Module 'cart' exposes 3 of 5 classes to other modules, more than the 2 that 40% allows: Cart, Line, Price. Keep most classes behind a few public ones."])
            )

    with context("source-parses"):
        with before.all:
            self.pair = files_rule_pair(
                "source-parses",
                _module("cart", {"cart.py": "class Cart(:\n    pass\n"}),
                _module("cart", {"cart.py": "class Cart:\n    pass\n"}),
            )
            self.nested_package = practice_from_files(_module("cart", {"lines/line.py": "class Line(:\n    pass\n"}))

        with it("should report a module's Python file that does not parse"):
            self.pair.check()

        with it("should report a file that does not parse in a package inside the module"):
            expect(len(_hits("source-parses", self.nested_package))).to(equal(1))
