"""Examples for the rules that ask whether code is used and connected: the shop project, whose till rings up a cart,
each rule's failing and repaired shop, read by Clean Engineering as a live load reads a working copy.

Seed: the shop module (`shop/`, with its module card) holds `cart.py`, whose class Cart adds lines and totals them,
and `till.py`, whose class Till holds a cart and rings a line up on it. The orders module (`orders/`) starts the shop:
its `main` is the project's entry point, as the project's config names it."""

from __future__ import annotations

import json

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.clean_engineering.rules.rule_examples import files_rule_pair, practice_from_files

# Seed: the shop project's config, which names its one entry point and the registry its printers are registered with.
SHOP_CONFIG = json.dumps({"code_reach": {"entry_points": ["*.py:main"], "registries": ["PRINTERS.register"]}})
SHOP_CARD = "# shop\n\n- **Purpose:** Ring up a customer's cart.\n- **Seam (terms):** Cart, Till\n"
ORDERS_CARD = "# orders\n\n- **Purpose:** Start the shop.\n- **Seam (terms):** main\n"
CART = '''
class Cart:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def add(self, line: str) -> None:
        self.lines.append(line)

    def total(self) -> int:
        return len(self.lines)
'''
TILL = '''
from shop.cart import Cart


class Till:
    def __init__(self, cart: Cart) -> None:
        self.cart = cart

    def ring(self, line: str) -> int:
        self.cart.add(line)
        return self.cart.total()
'''
MAIN = '''
from shop.cart import Cart
from shop.till import Till


def main() -> int:
    return Till(Cart()).ring("book")
'''
_SHOP = {
    ".context/config.json": SHOP_CONFIG,
    "shop/.context/module-context.md": SHOP_CARD,
    "shop/cart.py": CART,
    "shop/till.py": TILL,
    "orders/.context/module-context.md": ORDERS_CARD,
    "orders/start.py": MAIN,
}

# Interaction: a coupon nobody uses, beside the cart.
COUPON = '''

class Coupon:
    def __init__(self, code: str) -> None:
        self.code = code

    def value(self) -> int:
        return 5
'''
# Interaction: the till takes a coupon off each line it rings up, so the coupon is used.
TILL_WITH_COUPON = TILL.replace("from shop.cart import Cart", "from shop.cart import Cart, Coupon").replace(
    "    def ring(self, line: str) -> int:\n        self.cart.add(line)\n        return self.cart.total()",
    "    def ring(self, line: str, coupon: Coupon) -> int:\n        self.cart.add(line)\n        return self.cart.total() - coupon.value()",
)
MAIN_WITH_COUPON = MAIN.replace("from shop.till import Till", "from shop.cart import Coupon\nfrom shop.till import Till").replace(
    'ring("book")', 'ring("book", Coupon("SPRING"))'
)
# Interaction: a cart that counts its lines with a function of its own file, beside one nothing calls, and that can
# also be cleared, recounted and asked whether it is empty, which nothing does.
_COUNTING = '''
def count_lines(lines: list[str]) -> int:
    return len(lines)
'''
_COUNTING_TWICE = '''

def count_twice(lines: list[str]) -> int:
    return 2 * len(lines)
'''
_COUNTED_CART = CART.replace("        return len(self.lines)", "        return count_lines(self.lines)")
_CLEARING = '''
    def clear(self) -> int:
        dropped = len(self.lines)
        self.lines = []
        return dropped

    def _recount(self) -> int:
        return len(self.lines)

    @property
    def empty(self) -> bool:
        return not self.lines
'''
CLEARING_CART = _COUNTING + _COUNTING_TWICE + "\n" + _COUNTED_CART + _CLEARING
# Interaction: the function nobody calls deleted; the cart recounts the lines it clears, and the till clears the cart
# once it has rung a line up, when it is not empty.
CLEARING_CART_IN_USE = _COUNTING + "\n" + _COUNTED_CART + _CLEARING.replace("        dropped = len(self.lines)", "        dropped = self._recount()")
TILL_THAT_CLEARS = TILL.replace(
    "        return self.cart.total()",
    "        rung = self.cart.total()\n        if not self.cart.empty:\n            self.cart.clear()\n        return rung",
)
# Interaction: a till that takes off an offer whose class no hint says, and two classes that each declare value, so
# the read cannot tell which the offer is.
TILL_WITH_AN_UNTYPED_OFFER = TILL.replace(
    "    def ring(self, line: str) -> int:\n        self.cart.add(line)\n        return self.cart.total()",
    "    def ring(self, line: str, offer) -> int:\n        self.cart.add(line)\n        return self.cart.total() - offer.value()",
)
VOUCHER = '''

class Voucher:
    def value(self) -> int:
        return 10
'''
# Interaction: the till moved out of the shop module into the orders module, so the cart's add and total are called
# from another module, and the shop started from an app folder of its own, so the till's ring is too.
MAIN_WITH_ORDERS_TILL = MAIN.replace("from shop.till import Till", "from orders.till import Till")
# Interaction: a receipt printer joined to no class but by inheritance; then registered with the printers registry,
# which holds it.
RECEIPT = '''
class Printable:
    def print_out(self) -> str:
        return ""


class Receipt(Printable):
    def print_out(self) -> str:
        return "receipt"
'''
REGISTERED_RECEIPT = RECEIPT + "\n\nPRINTERS.register(Receipt)\n"
# Interaction: the till holds the receipt it prints.
TILL_WITH_RECEIPT = TILL.replace("from shop.cart import Cart", "from shop.cart import Cart\nfrom shop.receipt import Receipt").replace(
    "        self.cart = cart\n", "        self.cart = cart\n        self.receipt = Receipt()\n"
).replace("        return self.cart.total()", "        self.receipt.print_out()\n        return self.cart.total()")
# Interaction: a coupons package (no module card) holding the coupon alone, then the coupon beside a voucher.
TILL_WITH_PACKAGED_COUPON = TILL_WITH_COUPON.replace("from shop.cart import Cart, Coupon", "from shop.cart import Cart\nfrom shop.coupons.coupon import Coupon")
MAIN_WITH_PACKAGED_COUPON = MAIN_WITH_COUPON.replace("from shop.cart import Coupon", "from shop.coupons.coupon import Coupon")


def shop_with(files: dict[str, str]) -> dict[str, str]:
    """The shop project, with files in place of or beside its seed files."""
    return {**_SHOP, **files}


# Each rule's failing and repaired shop, by the rule's slug.
EXAMPLES: dict[str, tuple[dict[str, str], dict[str, str]]] = {
    "delete-unused-classes": (
        shop_with({"shop/cart.py": CART + COUPON}),
        shop_with({"shop/cart.py": CART + COUPON, "shop/till.py": TILL_WITH_COUPON, "orders/start.py": MAIN_WITH_COUPON}),
    ),
    "delete-unused-operations": (
        shop_with({"shop/cart.py": CLEARING_CART}),
        shop_with({"shop/cart.py": CLEARING_CART_IN_USE, "shop/till.py": TILL_THAT_CLEARS}),
    ),
    "check-use-the-graph-cannot-see": (
        shop_with({"shop/cart.py": CART + COUPON + VOUCHER, "shop/till.py": TILL_WITH_AN_UNTYPED_OFFER.replace("from shop.cart import Cart", "from shop.cart import Cart, Coupon, Voucher")}),
        shop_with({"shop/cart.py": CART + COUPON + VOUCHER, "shop/till.py": TILL_WITH_COUPON.replace("coupon.value()", "coupon.value() - Voucher().value()").replace("import Cart, Coupon", "import Cart, Coupon, Voucher"), "orders/start.py": MAIN_WITH_COUPON}),
    ),
    "make-module-only-operations-private": (
        shop_with({}),
        {**{name: text for name, text in _SHOP.items() if name not in ("shop/till.py", "orders/start.py")}, "orders/till.py": TILL, "app/start.py": MAIN_WITH_ORDERS_TILL},
    ),
    "connect-disconnected-classes": (
        shop_with({"shop/receipt.py": RECEIPT}),
        shop_with({"shop/receipt.py": RECEIPT, "shop/till.py": TILL_WITH_RECEIPT}),
    ),
    "merge-one-class-packages": (
        shop_with({"shop/coupons/coupon.py": COUPON, "shop/till.py": TILL_WITH_PACKAGED_COUPON, "orders/start.py": MAIN_WITH_PACKAGED_COUPON}),
        shop_with({"shop/coupons/coupon.py": COUPON, "shop/coupons/voucher.py": VOUCHER, "shop/till.py": TILL_WITH_PACKAGED_COUPON.replace("coupon.value()", "coupon.value() - Voucher().value()").replace("from shop.coupons.coupon import Coupon", "from shop.coupons.coupon import Coupon\nfrom shop.coupons.voucher import Voucher"), "orders/start.py": MAIN_WITH_PACKAGED_COUPON}),
    ),
}


def example_pair(slug: str) -> RulePair:
    """The rule's failing and repaired shop, each read once, as the rule examples read a tree of files."""
    faulty, repaired = EXAMPLES[slug]
    return files_rule_pair(slug, faulty, repaired)


# Interaction: a printer only example code uses, the receipt examples, which nothing in production imports; then the
# till rings up the receipt example, so production imports the example code and its use of the printer is real.
PRINTER = '''
class Printer:
    def print_out(self, text: str) -> str:
        return text.upper()
'''
RECEIPT_EXAMPLES = '''
from shop.printer import Printer


class ReceiptExample:
    def printed(self) -> str:
        return Printer().print_out("receipt")
'''
TILL_PRINTING_THE_EXAMPLE = TILL.replace("from shop.cart import Cart", "from shop.cart import Cart\nfrom shop.receipt_examples import ReceiptExample").replace(
    "        return self.cart.total()", "        ReceiptExample().printed()\n        return self.cart.total()"
)
# Interaction: a till formatter that extends a formatter from a library outside the code read, whose example_passed
# the library calls, and which the shop's start builds.
SHOP_FORMATTER = '''
from mamba.formatters import DocumentationFormatter


class ShopFormatter(DocumentationFormatter):
    def __init__(self) -> None:
        self.passed = None

    def example_passed(self, example) -> None:
        self.passed = example
'''
MAIN_WITH_FORMATTER = MAIN.replace("from shop.till import Till", "from shop.formatter import ShopFormatter\nfrom shop.till import Till").replace(
    '    return Till(Cart()).ring("book")', '    ShopFormatter()\n    return Till(Cart()).ring("book")'
)
# Interaction: checks that print a receipt to compare, spec support kept under a production name; then the shop's
# config names it as test code.
PRINT_CHECKS = '''
from shop.printer import Printer


class PrintChecks:
    def printed(self) -> str:
        return Printer().print_out("receipt")
'''
CONFIG_NAMING_THE_CHECKS = json.dumps({"code_reach": json.loads(SHOP_CONFIG)["code_reach"], "test_code": {"files": ["shop/print_checks.py"]}})
# Interaction: a book the till prices through a protocol it satisfies by shape, not by extending it; first with no
# protocol, the till pricing nothing, then with the till pricing whatever satisfies Priced.
PRICING = '''
from typing import Protocol


class Priced(Protocol):
    def price(self) -> int:
        ...

    def label(self) -> str:
        ...


class Book:
    def __init__(self, title: str) -> None:
        self.title = title

    def price(self) -> int:
        return 5

    def label(self) -> str:
        return self.title
'''
TILL_PRICING = TILL.replace("from shop.cart import Cart", "from shop.cart import Cart\nfrom shop.pricing import Priced").replace(
    "    def ring(self, line: str) -> int:\n        self.cart.add(line)\n        return self.cart.total()",
    "    def ring(self, line: str, item: Priced) -> int:\n        self.cart.add(item.label())\n        return self.cart.total() + item.price()",
)
MAIN_PRICING = MAIN.replace("from shop.till import Till", "from shop.pricing import Book\nfrom shop.till import Till").replace(
    'ring("book")', 'ring("book", Book("Dune"))'
)
# Interaction: the shop's start builds a book and rings up a line, while the till prices nothing.
MAIN_WITH_A_BOOK = MAIN.replace("from shop.till import Till", "from shop.pricing import Book\nfrom shop.till import Till").replace(
    '    return Till(Cart()).ring("book")', '    Book("Dune")\n    return Till(Cart()).ring("book")'
)
# Each situation the use rules meet beside their failing and repaired shops: the shop's files without it and with it.
SITUATIONS: dict[str, tuple[dict[str, str], dict[str, str]]] = {
    "example code nothing in production imports": (
        shop_with({"shop/printer.py": PRINTER, "shop/receipt_examples.py": RECEIPT_EXAMPLES}),
        shop_with({"shop/printer.py": PRINTER, "shop/receipt_examples.py": RECEIPT_EXAMPLES, "shop/till.py": TILL_PRINTING_THE_EXAMPLE}),
    ),
    "spec support the config names as test code": (
        shop_with({"shop/printer.py": PRINTER, "shop/print_checks.py": PRINT_CHECKS}),
        shop_with({"shop/printer.py": PRINTER, "shop/print_checks.py": PRINT_CHECKS, ".context/config.json": CONFIG_NAMING_THE_CHECKS}),
    ),
    "an operation called through a protocol its class satisfies": (
        shop_with({"shop/pricing.py": PRICING, "orders/start.py": MAIN_WITH_A_BOOK}),
        shop_with({"shop/pricing.py": PRICING, "shop/till.py": TILL_PRICING, "orders/start.py": MAIN_PRICING}),
    ),
    "a class a registry holds": (
        shop_with({"shop/receipt.py": RECEIPT}),
        shop_with({"shop/receipt.py": REGISTERED_RECEIPT}),
    ),
    "a class extending a class from outside the code read": (
        shop_with({}),
        shop_with({"shop/formatter.py": SHOP_FORMATTER, "orders/start.py": MAIN_WITH_FORMATTER}),
    ),
}


def situation(name: str) -> tuple[RuleFixture, RuleFixture]:
    """The shop read without the situation and with it."""
    without, within = SITUATIONS[name]
    return practice_from_files(without), practice_from_files(within)
