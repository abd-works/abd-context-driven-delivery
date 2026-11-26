"""Practice-wide rules read every module folder and class in the graph at once."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it


from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    files_rule_pair,
    practice_from_files,
)


def _hits(slug: str, fixture) -> list[str]:
    return fixture.hits(BY_SLUG[slug])


def _module(folder: str, files: dict[str, str]) -> dict[str, str]:
    """A first-class module: a folder with its module card plus the given source files."""
    tree = {f"{folder}/.context/module-context.md": "# module\n"}
    tree.update({f"{folder}/{name}": text for name, text in files.items()})
    return tree


def _class_of_methods(name: str, count: int) -> str:
    """A class of count public methods."""
    methods = "".join(f"    def step{index}(self) -> int:\n        return {index}\n\n" for index in range(count))
    return f"class {name}:\n{methods}\n"


def _cart_of_methods(*imported: str) -> dict[str, str]:
    """A cart module of 10 methods (Cart 4, Line 3, Price 3) and a shop module importing the classes named."""
    classes = _class_of_methods("Cart", 4) + _class_of_methods("Line", 3) + _class_of_methods("Price", 3)
    tree = _module("cart", {"cart.py": classes})
    tree.update(_module("shop", {"checkout.py": f"from cart.cart import {', '.join(imported)}\n"}))
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
            # cart holds 10 methods: Cart 4, Line 3, Price 3; shop imports the classes named.
            self.over = practice_from_files(_cart_of_methods("Cart"))
            self.at_limit = practice_from_files(_cart_of_methods("Line"))
            small = _module("cart", {"cart.py": _class_of_methods("Cart", 5) + _class_of_methods("Line", 2) + _class_of_methods("Price", 2)})
            small.update(_module("shop", {"checkout.py": "from cart.cart import Cart, Line, Price\n"}))
            self.under_ten = practice_from_files(small)
            classes = _class_of_methods("Cart", 1) + _class_of_methods("Line", 1) + _class_of_methods("Price", 10)
            shallow_classes = _module("cart", {"cart.py": classes})
            shallow_classes.update(_module("shop", {"checkout.py": "from cart.cart import Cart, Line\n"}))
            self.class_ratio_over = practice_from_files(shallow_classes)

        with it("should fail a module whose seam methods are over 35% of its methods"):
            expect(_hits("deep-module", self.over)).to(
                equal(
                    [
                        "Module 'cart' exposes 4 of its 10 methods to other modules, more than the 3 that 35% allows; "
                        "they are the public methods of its 1 public classes of 3: Cart. Hide more behind fewer public methods."
                    ]
                )
            )

        with it("should pass a module whose seam methods are at the 35% limit, rounded down"):
            expect(_hits("deep-module", self.at_limit)).to(equal([]))

        with it("should not measure a module of fewer than 10 methods"):
            expect(_hits("deep-module", self.under_ten)).to(equal([]))

        with it("should not fail a module for its share of public classes"):
            expect(_hits("deep-module", self.class_ratio_over)).to(equal([]))

    with context("source-parses"):
        with before.all:
            self.pair = files_rule_pair(
                "source-parses",
                _module("cart", {"cart.py": "class Cart(:\n    pass\n"}),
                _module("cart", {"cart.py": "class Cart:\n    pass\n"}),
            )
            self.nested_package = practice_from_files(_module("cart", {"lines/line.py": "class Line(:\n    pass\n"}))
            self.no_module_card = practice_from_files(
                {"src/order.py": "class Order(:\n    def total(self\n", "src/other.py": "class Other:\n    pass\n"}
            )
            self.byte_order_mark = practice_from_files(_module("shop", {"bom.py": "﻿class BomOnly:\n    pass\n"}))

        with it("should report a module's Python file that does not parse"):
            self.pair.check()

        with it("should report a file that does not parse in a package inside the module"):
            expect(len(_hits("source-parses", self.nested_package))).to(equal(1))

        with it("should report a file that does not parse in a folder that has no module card"):
            expect([hit.split(":")[0] for hit in _hits("source-parses", self.no_module_card)]).to(
                equal(["Source file src/order.py"])
            )

        with it("should not report a file that only starts with a byte-order mark"):
            expect(_hits("source-parses", self.byte_order_mark)).to(equal([]))
