"""The failing and repaired examples of Clean Engineering's rules across files: small trees of files, each read by the
practice as a working copy is, that the rule specs and the story tests check one rule against."""

from __future__ import annotations

# put-logic-on-the-owning-resource: a cart that builds the price list it asks on each call, from a string.
_PRICE_LIST = (
    "class PriceList:\n"
    "    def __init__(self, currency: str) -> None:\n        self.currency = currency\n\n"
    "    def price(self, sku: str) -> int:\n        return len(sku)\n"
)
_DEPOT = (
    "class Depot:\n"
    "    def __init__(self, name: str) -> None:\n        self.name = name\n\n"
    "    @classmethod\n    def named(cls, name: str) -> 'Depot':\n        return cls(name)\n\n"
    "    def open(self) -> bool:\n        return True\n"
)
_CART_HEAD = "from shop.depot import Depot\nfrom shop.price_list import PriceList\n\n\nclass Cart:\n"
CART_BUILDS_PER_CALL = {
    "shop/price_list.py": _PRICE_LIST,
    "shop/cart.py": _CART_HEAD + "    def total(self, sku: str) -> int:\n        return PriceList(\"usd\").price(sku)\n",
}
CART_LOOKS_UP_BY_NAME = {
    "shop/depot.py": _DEPOT,
    "shop/cart.py": _CART_HEAD + "    def park(self) -> bool:\n        return Depot.named(\"north\").open()\n",
}
# The cart holds the price list it is handed.
CART_HOLDS_WHAT_IT_IS_HANDED = {
    "shop/price_list.py": _PRICE_LIST,
    "shop/cart.py": _CART_HEAD + (
        "    def __init__(self, prices: PriceList) -> None:\n        self.prices = prices\n\n"
        "    def total(self, sku: str) -> int:\n        return self.prices.price(sku)\n"
    ),
}
CART_IS_HANDED_A_PARAMETER = {
    "shop/price_list.py": _PRICE_LIST,
    "shop/cart.py": _CART_HEAD + "    def total(self, prices: PriceList, sku: str) -> int:\n        return prices.price(sku)\n",
}
# A note made for one message: a formatted string is no reference to an object anything owns.
CART_BUILDS_A_MESSAGE_PER_CALL = {
    "shop/note.py": "class Note:\n    def __init__(self, text: str) -> None:\n        self.text = text\n\n    def shown(self) -> str:\n        return self.text\n",
    "shop/cart.py": (
        "from shop.note import Note\n\n\n"
        "class Cart:\n    def warn(self, sku: str) -> str:\n        return Note(f\"no price for {sku}\").shown()\n"
    ),
}
CART_BUILDS_IN_ITS_CONSTRUCTOR = {
    "shop/price_list.py": _PRICE_LIST,
    "shop/cart.py": _CART_HEAD + (
        "    def __init__(self) -> None:\n        self.prices = PriceList(\"usd\")\n\n"
        "    def total(self, sku: str) -> int:\n        return self.prices.price(sku)\n"
    ),
}

# eliminate-duplication: an invoice and a parcel that total their lines with the same statements, each under
# names of its own; and two one-line getters that read alike.
_INVOICE = (
    "class Invoice:\n"
    "    def total(self, lines: list) -> int:\n"
    "        amount = 0\n"
    "        for line in lines:\n"
    "            amount += line.price * line.quantity\n"
    "        amount -= amount // 10\n"
    "        return amount\n\n"
    "    def number(self) -> str:\n        return self.code\n"
)
TOTALLED_IN_TWO_FILES = {
    "billing/invoice.py": _INVOICE,
    "shipping/parcel.py": (
        "class Parcel:\n"
        "    def cost(self, items: list) -> int:\n"
        "        summed = 0\n"
        "        for item in items:\n"
        "            summed += item.price * item.quantity\n"
        "        summed -= summed // 10\n"
        "        return summed\n\n"
        "    def label(self) -> str:\n        return self.code\n"
    ),
}
# The same total written word for word in two files.
COPIED_IN_TWO_FILES = {
    "billing/invoice.py": _INVOICE,
    "shipping/parcel.py": _INVOICE.replace("class Invoice", "class Parcel").replace("def number", "def label"),
}
TOTALLED_IN_ONE_PLACE = {
    "billing/invoice.py": _INVOICE,
    "shipping/parcel.py": (
        "from billing.invoice import Invoice\n\n\n"
        "class Parcel:\n"
        "    def __init__(self, invoice: Invoice) -> None:\n        self.invoice = invoice\n\n"
        "    def cost(self, items: list) -> int:\n        return self.invoice.total(items)\n\n"
        "    def label(self) -> str:\n        return self.code\n"
    ),
}

# hold-state-on-the-object-not-in-parameters: a session handed down from a desk through its clerk to the archive.
SESSION_HANDED_DOWN = {
    "desk/archive.py": "class Archive:\n    def store(self, session: str) -> str:\n        return session.upper()\n",
    "desk/clerk.py": (
        "from desk.archive import Archive\n\n\n"
        "class Clerk:\n"
        "    def __init__(self, archive: Archive) -> None:\n        self.archive = archive\n\n"
        "    def file(self, session: str) -> str:\n        return self.archive.store(session)\n"
    ),
    "desk/desk.py": (
        "from desk.clerk import Clerk\n\n\n"
        "class Desk:\n"
        "    def __init__(self, clerk: Clerk) -> None:\n        self.clerk = clerk\n\n"
        "    def open(self, session: str) -> str:\n        return self.clerk.file(session)\n"
    ),
}
# A desk that hands its session between its own operations only.
SESSION_HANDED_WITHIN_ONE_CLASS = {
    "desk/desk.py": (
        "class Desk:\n"
        "    def open(self, session: str) -> str:\n        return self._checked(session)\n\n"
        "    def _checked(self, session: str) -> str:\n        return self._stored(session)\n\n"
        "    def _stored(self, session: str) -> str:\n        return session.upper()\n"
    ),
}
# A desk that hands its session to the constructor of the clerk made for it: the clerk then holds it.
SESSION_HANDED_TO_A_CONSTRUCTOR = {
    "desk/archive.py": "class Archive:\n    def __init__(self, session: str) -> None:\n        self.session = session\n",
    "desk/clerk.py": (
        "from desk.archive import Archive\n\n\n"
        "class Clerk:\n    def __init__(self, session: str) -> None:\n        self.archive = Archive(session)\n"
    ),
    "desk/desk.py": (
        "from desk.clerk import Clerk\n\n\n"
        "class Desk:\n    def open(self, session: str) -> Clerk:\n        return Clerk(session)\n"
    ),
}
# The archive is made for its session and holds it.
SESSION_HELD = {
    "desk/archive.py": (
        "class Archive:\n"
        "    def __init__(self, session: str) -> None:\n        self.session = session\n\n"
        "    def store(self) -> str:\n        return self.session.upper()\n"
    ),
    "desk/clerk.py": (
        "from desk.archive import Archive\n\n\n"
        "class Clerk:\n"
        "    def __init__(self, archive: Archive) -> None:\n        self.archive = archive\n\n"
        "    def file(self) -> str:\n        return self.archive.store()\n"
    ),
    "desk/desk.py": (
        "from desk.clerk import Clerk\n\n\n"
        "class Desk:\n"
        "    def __init__(self, clerk: Clerk) -> None:\n        self.clerk = clerk\n\n"
        "    def open(self) -> str:\n        return self.clerk.file()\n"
    ),
}
# A board every operation of which is handed the ticket it is made for.
TICKET_TO_EVERY_OPERATION = {
    "desk/board.py": (
        "class Board:\n"
        "    def show(self, ticket: str) -> str:\n        return ticket\n\n"
        "    def move(self, ticket: str, column: str) -> str:\n        return ticket + column\n\n"
        "    def close(self, ticket: str) -> str:\n        return ticket + '.'\n"
    ),
}
TICKET_HELD = {
    "desk/board.py": (
        "class Board:\n"
        "    def __init__(self, ticket: str) -> None:\n        self.ticket = ticket\n\n"
        "    def show(self) -> str:\n        return self.ticket\n\n"
        "    def move(self, column: str) -> str:\n        return self.ticket + column\n\n"
        "    def close(self) -> str:\n        return self.ticket + '.'\n"
    ),
}

# do-not-invent-parallel-object-models: a listing that names again the checks a registry already holds.
_CHECKS = "".join(f"class {name}:\n    def run(self) -> int:\n        return {number}\n\n\n" for number, name in enumerate(("Alpha", "Beta", "Gamma")))
_REGISTRY = "from checks.kinds import Alpha, Beta, Gamma\n\nCHECKS = (Alpha(), Beta(), Gamma())\n"
SECOND_REGISTRY = {
    "checks/kinds.py": _CHECKS,
    "checks/registry.py": _REGISTRY,
    "report/listing.py": "from checks.kinds import Alpha, Beta, Gamma\n\nLISTED = [Alpha, Beta, Gamma]\n",
}
ONE_REGISTRY = {
    "checks/kinds.py": _CHECKS,
    "checks/registry.py": _REGISTRY,
    "report/listing.py": "from checks.registry import CHECKS\n\nLISTED = [type(check) for check in CHECKS]\n",
}

# A file that exports the classes, and a list that spells their names as labels: neither is a registry.
NAMES_EXPORTED_AND_SPELLED = {
    "checks/kinds.py": _CHECKS,
    "checks/__init__.py": "from checks.kinds import Alpha, Beta, Gamma\n\n__all__ = [Alpha, Beta, Gamma]\n",
    "report/listing.py": "LABELS = ['Alpha', 'Beta', 'Gamma']\n",
}

# use-consistent-naming: a cart that gets the order and a till that fetches it.
TWO_VERBS_FOR_ORDER = {
    "store/cart.py": "class Cart:\n    def get_order(self, number: int) -> str:\n        return str(number)\n",
    "store/till.py": "class Till:\n    def fetch_order(self, number: int) -> str:\n        return str(number)\n",
}
ONE_VERB_FOR_ORDER = {
    "store/cart.py": "class Cart:\n    def get_order(self, number: int) -> str:\n        return str(number)\n",
    "store/till.py": "class Till:\n    def get_order(self, number: int) -> str:\n        return str(number)\n",
}

# seam-names-current-code: a shop card whose seam and dependencies the code has moved on from.
def _card(module: str, seam: str, dependencies: str) -> str:
    return (
        f"# {module}\n*{module.title()}* is what {module} keeps.\n\n"
        f"- **Seam (terms):** {seam}\n- **Dependencies (one-way):** {dependencies}\n\n## Constraint\n\nUse the seam only.\n"
    )


_MODULES = {
    "pricing/.context/module-context.md": _card("pricing", "Price", "*(none)*"),
    "pricing/price.py": "class Price:\n    def amount(self) -> int:\n        return 1\n",
    "stock/.context/module-context.md": _card("stock", "Shelf", "*(none)*"),
    "stock/shelf.py": "class Shelf:\n    def count(self) -> int:\n        return 1\n",
    "tax/.context/module-context.md": _card("tax", "Rate", "*(none)*"),
    "tax/rate.py": "class Rate:\n    def share(self) -> int:\n        return 1\n",
    "shop/cart.py": (
        "from pricing.price import Price\nfrom tax.rate import Rate\n\n\n"
        "class Cart:\n    def total(self, price: Price, rate: Rate) -> int:\n        return price.amount() * rate.share()\n"
    ),
}
CARD_BEHIND_THE_CODE = {
    **_MODULES,
    "shop/.context/module-context.md": _card("shop", "Cart, Basket", "`pricing`, `stock`, `ledger/books`"),
}
# The card names a package inside the module by its path from the module's folder.
CARD_NAMING_ITS_OWN_PACKAGE = {
    **_MODULES,
    "shop/lines/detail/line.py": "class Line:\n    def price(self) -> int:\n        return 1\n",
    "shop/.context/module-context.md": _card("shop", "Cart", "`pricing`, `tax`, `lines/detail`"),
}
# A module still at the modules fidelity: its card names its seam before any code declares it.
CARD_BEFORE_ANY_CODE = {
    "shop/.context/module-context.md": _card("shop", "Cart, Basket", "`pricing`"),
}
CARD_MATCHING_THE_CODE = {
    **_MODULES,
    "shop/.context/module-context.md": _card("shop", "Cart", "`pricing`, `tax`"),
}
