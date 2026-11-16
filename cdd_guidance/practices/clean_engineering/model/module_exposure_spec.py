"""What of each module's subtree leaves it: the class definitions named, registered, or published from outside it,
each import resolved to the definition it names, and the operations of its classes."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.class_graph import ClassGraph
from cdd_guidance.practices.clean_engineering.model.module_exposure import ModuleExposure
from cdd_guidance.practices.clean_engineering.model.public_routes import PublicRoutes, RegisteredClasses
from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files

_CARD = "# module\n"
_SHOP_CARD = {"shop/.context/module-context.md": _CARD}


def _classes(*names: str) -> str:
    return "".join(f"class {name}:\n    def run(self) -> int:\n        return 1\n\n\n" for name in names)


def _module_of(folder: str, file: str, names: tuple[str, ...]) -> dict[str, str]:
    """A module folder with its card and one Python file of the named classes."""
    return {f"{folder}/.context/module-context.md": _CARD, f"{folder}/{file}": _classes(*names)}


def _ts_module_of(folder: str, names: tuple[str, ...]) -> dict[str, str]:
    """A module folder with its card and one TypeScript file, named after the folder, of the named classes."""
    text = "".join(f"export class {name} {{\n  run(): number {{\n    return 1;\n  }}\n}}\n\n" for name in names)
    return {f"{folder}/.context/module-context.md": _CARD, f"{folder}/{folder}.ts": text}


def _module(fixture, name: str):
    return next(node for node in fixture.practice.reading.in_graph.nodes("Module") if node.name == name)


def _public(fixture, name: str) -> dict:
    return _module(fixture, name).get_fact("public_classes")


def _counts(module) -> tuple[int, int, int]:
    return (module.get_fact("subtree_class_count"), module.get_fact("public_class_count"), module.get_fact("private_class_count"))


def _operations(module) -> tuple[int, int, int, int]:
    keys = ("operations_total", "operations_public", "operations_private", "seam_operations")
    return tuple(module.get_fact(key) for key in keys)


with description("module exposure"):
    with context("with two modules that each define a Node, only one of them imported from outside"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_module_of("left", "graph.py", ("Node", "Edge", "Path")),
                    **_module_of("right", "graph.py", ("Node", "Edge", "Path")),
                    **_SHOP_CARD,
                    "shop/checkout.py": "from left.graph import Node\n",
                }
            )

        with it("should make public only the Node the import names"):
            expect(_public(self.fixture, "left")).to(equal({"left/graph.py:Node": {"named": ["shop"]}}))

        with it("should keep its namesake private"):
            expect(_public(self.fixture, "right")).to(equal({}))

    with context("with a package without a card, a nested module, a test fixture, and a spec inside a module"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_module_of("cart", "cart.py", ("Cart", "Line")),
                    "cart/lines/line_item.py": _classes("LineItem"),
                    "cart/fixtures.py": _classes("FakeCart"),
                    **_module_of("cart/pricing", "pricing.py", ("Levy", "Rate", "Fee")),
                    "cart/cart_extra.py": "from cart.pricing.pricing import Levy\n",
                    **_SHOP_CARD,
                    "shop/checkout.py": "from cart.pricing.pricing import Rate\nfrom cart.lines.line_item import LineItem\n",
                    "shop/checkout_spec.py": "from cart.cart import Cart, Line\n",
                }
            )

        with it("should count the package's classes and the nested module's in the parent, not the fixture's"):
            expect(_counts(_module(self.fixture, "cart"))).to(equal((6, 2, 4)))

        with it("should make public in the parent only what code outside the parent names, not what a spec names"):
            expect(sorted(_public(self.fixture, "cart"))).to(equal(["cart/lines/line_item.py:LineItem", "cart/pricing/pricing.py:Rate"]))

        with it("should measure the nested module on its own, a class its parent names public there"):
            expect(sorted(_public(self.fixture, "pricing"))).to(equal(["cart/pricing/pricing.py:Levy", "cart/pricing/pricing.py:Rate"]))

    with context("with a load of the imported module's files alone, its importer left outside the scope"):
        with before.all:
            self.fixture = practice_from_files(
                {**_module_of("left", "graph.py", ("Node", "Edge", "Path")), **_SHOP_CARD, "shop/checkout.py": "from left.graph import Node\n"}
            )
            self.fixture.read_only(["left/graph.py"])

        with it("should still make public the class the file outside the scope imports"):
            expect(_public(self.fixture, "left")).to(equal({"left/graph.py:Node": {"named": ["shop"]}}))

    with context("with one name defined in two files of a module, both imported from outside"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_module_of("cart", "a.py", ("Item", "Price")),
                    "cart/b.py": _classes("Item"),
                    **_SHOP_CARD,
                    "shop/checkout.py": "from cart.a import Item\nfrom cart.b import Item as Other\n",
                }
            )

        with it("should count each definition once in the total, the public, and the private"):
            expect(_counts(_module(self.fixture, "cart"))).to(equal((3, 2, 1)))

    with context("with a class reached through the module it is imported with"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_module_of("cart", "cart.py", ("Cart", "Line", "Price")),
                    **_SHOP_CARD,
                    "shop/checkout.py": "import cart.cart as basket\n\n\ndef total() -> int:\n    return basket.Cart().run()\n",
                }
            )

        with it("should make public the class the qualified name reaches"):
            expect(_public(self.fixture, "cart")).to(equal({"cart/cart.py:Cart": {"named": ["shop"]}}))

    with context("with a class imported through the package that re-exports it"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_module_of("cart", "cart.py", ("Cart", "Line", "Price")),
                    "cart/__init__.py": "from cart.cart import Cart\n",
                    **_SHOP_CARD,
                    "shop/checkout.py": "from cart import Cart\n",
                }
            )

        with it("should make public the definition the re-export names"):
            expect(_public(self.fixture, "cart")).to(equal({"cart/cart.py:Cart": {"named": ["shop"]}}))

    with context("with a TypeScript import of one of two classes of the same name"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_ts_module_of("cart", ("Cart", "Line", "Price")),
                    **_ts_module_of("till", ("Cart", "Drawer", "Coin")),
                    **_SHOP_CARD,
                    "shop/checkout.ts": "import { Cart } from '../cart/cart';\n\nexport const made = new Cart();\n",
                }
            )

        with it("should make public the class in the file the import's path names"):
            expect(_public(self.fixture, "cart")).to(equal({"cart/cart.ts:Cart": {"named": ["shop"]}}))

        with it("should keep the namesake in the other file private"):
            expect(_public(self.fixture, "till")).to(equal({}))

    with context("with a script that imports a Python class's data through its generated language adapter"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_module_of("board", "ticket_card.py", ("Ticket", "Lane", "Column")),
                    **_SHOP_CARD,
                    "shop/view.ts": "import type { TicketData } from '@cdd/board/ticket-card';\n\nexport const shown: TicketData[] = [];\n",
                }
            )

        with it("should make public the Python class the adapter sends"):
            expect(_public(self.fixture, "board")).to(equal({"board/ticket_card.py:Ticket": {"named": ["shop"]}}))

    with context("with a script module's exported and unexported functions"):
        with before.all:
            script = "export function shown(): number {\n  return 1;\n}\n\nfunction hidden(): number {\n  return 2;\n}\n"
            self.fixture = practice_from_files({"cart/.context/module-context.md": _CARD, "cart/cart.ts": script})

        with it("should count an unexported function as private"):
            expect(_operations(_module(self.fixture, "cart"))[:3]).to(equal((2, 1, 1)))

    with context("with a toolset the installer publishes and one only its host publishes"):
        with before.all:
            toolsets = "@agent_toolset\nclass Cart:\n    def run(self) -> int:\n        return 1\n\n\n"
            hosted = "@hosted_only\n@agent_toolset\nclass Line:\n    def run(self) -> int:\n        return 1\n\n\n"
            self.fixture = practice_from_files(
                {"cart/.context/module-context.md": _CARD, "cart/cart.py": toolsets + hosted + _classes("Price")}
            )

        with it("should make the toolset public as published, and not the hosted one"):
            expect(_public(self.fixture, "cart")).to(equal({"cart/cart.py:Cart": {"published": "toolset"}}))

    with context("with a class a package registers with a framework registry"):
        with before.all:
            self.fixture = practice_from_files(_module_of("cart", "cart.py", ("Cart", "Line", "Price")))
            reading = self.fixture.practice.reading
            registered = RegisteredClasses({"ACTION_CATALOGUE": [type("Line", (), {"__module__": "cart.cart"})]})
            ModuleExposure(reading.in_graph, ClassGraph(reading), PublicRoutes(registered)).record()

        with it("should make it public as registered, with the registry"):
            expect(_public(self.fixture, "cart")).to(equal({"cart/cart.py:Line": {"registered": "ACTION_CATALOGUE"}}))

    with context("with a test double beside the module's classes and an example that imports one of them"):
        with before.all:
            self.fixture = practice_from_files(
                {
                    **_module_of("cart", "cart.py", ("Cart", "Line", "Price")),
                    "cart/mock_cart.py": _classes("MockCart"),
                    "catalog/.context/module-context.md": _CARD,
                    "catalog/examples/shop.py": "from cart.cart import Cart\n",
                }
            )

        with it("should neither count the double nor make public the class only the example names"):
            expect(_counts(_module(self.fixture, "cart"))).to(equal((3, 0, 3)))

    with context("with classes and module functions of every visibility"):
        with before.all:
            cart = (
                "class Cart:\n"
                "    def __init__(self) -> None:\n        self._lines = []\n\n"
                "    @property\n    def total(self) -> int:\n        return self._sum()\n\n"
                "    def add(self, line: int) -> None:\n        self._lines.append(line)\n\n"
                "    def _sum(self) -> int:\n        return sum(self._lines)\n\n\n"
                "def make_cart() -> Cart:\n    return Cart()\n\n\n"
                "def _empty() -> list:\n    return []\n"
            )
            self.fixture = practice_from_files(
                {
                    "cart/.context/module-context.md": _CARD,
                    "cart/cart.py": cart + "\n\n" + _classes("Line", "Price"),
                    **_SHOP_CARD,
                    "shop/checkout.py": "from cart.cart import Cart\n",
                }
            )

        with it("should count every operation, the public ones, the private rest, and the public ones on its public classes"):
            # Cart: __init__, total, add, _sum; Line and Price: run; functions: make_cart, _empty.
            expect(_operations(_module(self.fixture, "cart"))).to(equal((8, 5, 3, 2)))
