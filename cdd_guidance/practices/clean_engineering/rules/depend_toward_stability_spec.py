"""depend-toward-stability: a module that many modules import should not import one that fewer import. The rule
compares two modules by the modules that import each, counted from the import edges every read records, and lists each
such dependency as a candidate, since some are deliberate."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_true, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules import BY_SLUG
from cdd_guidance.practices.clean_engineering.rules.rule_examples import files_rule_pair, practice_from_files

_SLUG = "depend-toward-stability"
_ORDER = "class Order:\n    def total(self) -> int:\n        return 0\n"
# A module is a folder that owns a module card; a folder without one is a package inside the module above it.
_CARDS = {
    f"{module}/.context/module-context.md": f"# {module}\n*{module.title()}* is what {module} keeps.\n\n- **Seam (terms):** {module.title()}\n\n## Constraint\n\nUse it only.\n"
    for module in ("checkout", "billing", "shipping", "orders", "promo")
}
# orders is imported by checkout, billing and shipping.
_USERS_OF_ORDERS = _CARDS | {
    f"{module}/{module}.py": f"from orders.order import Order\n\n\nclass {module.title()}:\n    def of(self, order: Order) -> int:\n        return order.total()\n"
    for module in ("checkout", "billing", "shipping")
}
_PROMO = "class Promo:\n    def discount(self) -> int:\n        return 0\n"
# orders imports promo, which nothing else imports.
_ORDERS_IMPORTING_PROMO = {
    **_USERS_OF_ORDERS,
    "orders/order.py": "from promo.promo import Promo\n\n\nclass Order:\n    def total(self) -> int:\n        return Promo().discount()\n",
    "promo/promo.py": _PROMO,
}
# promo imports orders: the module nothing relies on depends on the one three rely on.
_PROMO_IMPORTING_ORDERS = {
    **_USERS_OF_ORDERS,
    "orders/order.py": _ORDER,
    "promo/promo.py": "from orders.order import Order\n\n\nclass Promo:\n    def discount(self, order: Order) -> int:\n        return order.total()\n",
}
# orders imports promo only through its package orders/lines, a part of orders.
_ORDERS_PACKAGE_IMPORTING_PROMO = {
    **_USERS_OF_ORDERS,
    "orders/order.py": "from orders.lines.line import Line\n\n\nclass Order:\n    def total(self) -> int:\n        return Line().price()\n",
    "orders/lines/line.py": "from promo.promo import Promo\n\n\nclass Line:\n    def price(self) -> int:\n        return Promo().discount()\n",
    "promo/promo.py": _PROMO,
}
# orders imports its own package, orders/lines, which only orders imports.
_ORDERS_IMPORTING_ITS_OWN_PART = {
    **_USERS_OF_ORDERS,
    "orders/order.py": "from orders.lines.line import Line\n\n\nclass Order:\n    def total(self) -> int:\n        return Line().price()\n",
    "orders/lines/line.py": "class Line:\n    def price(self) -> int:\n        return 0\n",
}


with description("a module that imports another module") as self:
    with context("that fewer modules import than import it"):
        with before.all:
            self.pair = files_rule_pair(_SLUG, _ORDERS_IMPORTING_PROMO, _PROMO_IMPORTING_ORDERS)
            self.listed = practice_from_files(_ORDERS_IMPORTING_PROMO).hits(BY_SLUG[_SLUG])

        with it("should be listed, and pass once the dependency runs toward the module more modules import"):
            self.pair.check()

        with it("should be listed with both modules and how many modules import each"):
            expect(self.listed).to(equal([
                "Module 'orders', which 3 modules import, imports 'promo', which 1 module imports: 'orders' now changes whenever 'promo' does, "
                "and the 3 modules that import it change with it. Read whether this is deliberate, such as a small helper that seldom changes; "
                "if it is not, turn the dependency round or move what both need into 'orders'."
            ]))

        with it("should be a candidate for a judge, not a violation the graph decides"):
            expect(BY_SLUG[_SLUG].requires_judge).to(be_true)

    with context("through a package inside it"):
        with it("should be listed on the module, since a package is a part of the module that holds it"):
            listed = practice_from_files(_ORDERS_PACKAGE_IMPORTING_PROMO).hits(BY_SLUG[_SLUG])
            expect([said.split(",")[0] for said in listed]).to(equal(["Module 'orders'"]))

    with context("that is its child module, a folder beneath it with a module card of its own"):
        with it("should be listed, since a child module is another module the parent relies on"):
            child = {**_ORDERS_IMPORTING_ITS_OWN_PART, "orders/lines/.context/module-context.md": _CARDS["orders/.context/module-context.md"].replace("orders", "lines")}
            listed = practice_from_files(child).hits(BY_SLUG[_SLUG])
            expect([said.split(":")[0] for said in listed]).to(equal(["Module 'orders', which 3 modules import, imports 'lines', which 1 module imports"]))

    with context("that is a package inside itself, a folder beneath it with no module card"):
        with it("should not be listed, since a module's own part is not another module it relies on"):
            expect(practice_from_files(_ORDERS_IMPORTING_ITS_OWN_PART).hits(BY_SLUG[_SLUG])).to(equal([]))
