"""How Clean Engineering reads the Bookshop into its graph: three modules of Python whose classes share operation and
property names (`total`, `lines`, `__init__`), a subclass, and properties assigned in constructors; then the class
models of the same modules, beside that code."""

from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_files

BOOKSHOP = Path(__file__).resolve().parent / "fixtures" / "bookshop"
MODULES = ("catalogue", "ordering", "fulfilment")


def _code() -> dict:
    """The Bookshop's Python, under `src/` as its imports name it."""
    files = sorted((BOOKSHOP / "code").rglob("*.py"))
    return {f"src/{file.relative_to(BOOKSHOP / 'code').as_posix()}": file.read_text(encoding="utf-8") for file in files}


def _models() -> dict:
    """Each module's class model, where the model fidelity writes it."""
    return {f"src/{module}/.context/{module}-model.md": (BOOKSHOP / f"{module}-model.md").read_text(encoding="utf-8") for module in MODULES}


def _owned(fixture, node) -> str:
    """A member as `Class.member`, by the class that declares it."""
    return f"{node.get_fact('owner')}.{node.name}"


def _edges(fixture, kind: str) -> list:
    return list(fixture.practice.reading.in_graph.edge_index.of(kind))


def _calls(fixture) -> list:
    """Each call from an operation to an operation, as `Class.caller -> Class.called`."""
    edges = [edge for edge in _edges(fixture, "invokes") if edge.parent.type == "Operation" and edge.child.type == "Operation"]
    return sorted(f"{_owned(fixture, edge.parent)} -> {_owned(fixture, edge.child)}" for edge in edges)


def _reads(fixture, caller: str) -> list:
    """Each property the member called caller reads or calls, as `Class.property`."""
    edges = [edge for edge in _edges(fixture, "invokes") if _owned(fixture, edge.parent) == caller and edge.child.type == "Property"]
    return sorted(_owned(fixture, edge.child) for edge in edges)


def _between_classes(fixture, kind: str) -> list:
    return sorted(f"{edge.parent.name} -> {edge.child.name}" for edge in _edges(fixture, kind) if edge.parent.type == edge.child.type == "OoadClass")


def _code_file(node) -> bool:
    return node.source.file.endswith(".py")


with description("Clean Engineering reading the Bookshop into its graph") as self:
    with context("with code whose classes share operation and property names"):
        with before.all:
            self.fixture = practice_from_files(_code())

        with it("should join each call to the one operation its receiver names, by the receiver's type and the file's imports"):
            expect(_calls(self.fixture)).to(equal([
                "Book.reserve -> Book.is_in_stock",
                "Cart.add -> Book.is_in_stock",
                "Cart.check_out -> Order.place",
                "Cart.check_out -> Payment.authorise",
                "Cart.total -> CartLine.subtotal",
                "Catalogue.search -> Book.matches",
                "ExpressShipment.__init__ -> Shipment.__init__",
                "Order.place -> Book.reserve",
                "Order.total -> CartLine.subtotal",
                "Shipment.dispatch -> Order.total",
            ]))

        with it("should join a read to the property of the class its receiver is, not to every property of that name"):
            expect(_reads(self.fixture, "Shipment.dispatch")).to(equal(["Order.payment", "Payment.authorised", "Shipment.dispatched", "Shipment.order"]))

        with it("should hold a property for each field a constructor assigns"):
            properties = sorted(_owned(self.fixture, node) for node in self.fixture.practice.reading.in_graph.nodes("Property"))
            expect(properties).to(equal([
                "Book.copies", "Book.isbn", "Book.price", "Book.title",
                "Cart.customer_id", "Cart.lines",
                "CartLine.book", "CartLine.quantity",
                "Catalogue.books",
                "ExpressShipment.courier",
                "Order.lines", "Order.payment", "Order.status",
                "Payment.amount", "Payment.authorised",
                "Shipment.address", "Shipment.dispatched", "Shipment.order",
            ]))

        with it("should join a subclass to the class it extends"):
            expect(_between_classes(self.fixture, "baseClass")).to(equal(["ExpressShipment -> Shipment"]))

        with it("should join a class to each class a property of it is typed as, a list's element included"):
            expect(_between_classes(self.fixture, "dependsOn")).to(equal([
                "Cart -> CartLine", "CartLine -> Book", "Catalogue -> Book", "Order -> CartLine", "Order -> Payment", "Shipment -> Order",
            ]))

        with it("should join an operation to the class a list it returns holds"):
            returned = sorted(f"{_owned(self.fixture, edge.parent)} -> {edge.child.name}" for edge in _edges(self.fixture, "returns"))
            expect(returned).to(contain("Catalogue.search -> Book"))

    with context("with a class model beside the code that implements it"):
        with before.all:
            self.fixture = practice_from_files({**_code(), **_models()})
            self.classes = list(self.fixture.practice.reading.in_graph.nodes("OoadClass"))

        with it("should hold each class the model describes as a node of its own, beside the code's class"):
            described = sorted(node.name for node in self.classes if not _code_file(node))
            expect(described).to(equal(["Book", "Cart", "CartLine", "Catalogue", "ExpressShipment", "Order", "Payment", "Shipment"]))

        with it("should keep the code's class of each name"):
            coded = sorted(node.name for node in self.classes if _code_file(node) and node.name in {"Cart", "Order", "Shipment"})
            expect(coded).to(equal(["Cart", "Order", "Shipment"]))

        with it("should join each code class to the model class it implements, the one its own module's model describes"):
            joined = sorted(f"{edge.parent.source.file} -> {edge.child.source.file}" for edge in _edges(self.fixture, "implements") if edge.parent.name == "Order")
            expect(joined).to(equal(["src/ordering/order.py -> src/ordering/.context/ordering-model.md"]))

        with it("should keep the stereotypes the model gives a class"):
            cart = next(node for node in self.classes if node.name == "Cart" and not _code_file(node))
            expect(cart.get_fact("stereotypes")).to(equal(["Aggregate Root"]))

        with it("should join a model class to the class a property of it relates to, by the kind the model writes"):
            kinds = {kind: _between_classes(self.fixture, kind) for kind in ("composition", "aggregation", "association")}
            expect({kind: [pair for pair in pairs if pair.startswith(("Cart ->", "Order ->"))] for kind, pairs in kinds.items()}).to(equal({
                "composition": ["Cart -> CartLine"],
                "aggregation": ["Order -> CartLine"],
                "association": ["Order -> Payment"],
            }))

        with it("should join the model's subclass to the class it extends, in the model"):
            based = [f"{edge.parent.source.file} -> {edge.child.source.file}" for edge in _edges(self.fixture, "baseClass") if not _code_file(edge.parent)]
            expect(based).to(equal(["src/fulfilment/.context/fulfilment-model.md -> src/fulfilment/.context/fulfilment-model.md"]))
