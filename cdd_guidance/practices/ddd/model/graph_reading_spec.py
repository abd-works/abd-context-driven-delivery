"""DDD's reading of a working copy into the graph: the context mappings a bounded context lists are DDD's own nodes,
whether or not a pattern is applied, and a graph opened from its save holds them as the build that saved it did."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect  # noqa: E402
from mamba import before, context, description, it  # noqa: E402

from cdd_guidance.practices.ddd.ddd import Ddd  # noqa: E402
from harness.graph.graph import Graph  # noqa: E402
from harness.graph.rule_fixture import RuleFixture, SchemaRuleRun  # noqa: E402
from harness.graph.schema_conformance import FRAMEWORK_RULES  # noqa: E402

_SALES = {
    "src/.context/bounded-context.md": "# Sales\n\nMappings:\n- Sales · cart → Billing · invoice\n",
    "src/cart/cart.ts": "export class Cart {\n  total() { return 1; }\n}\n",
    "src/cart/cart_repository.ts": "export class CartRepository {\n  find(id) { return id; }\n}\n",
    "src/invoice/invoice.ts": "export class Invoice {\n  amount() { return 1; }\n}\n",
    "src/invoice/invoice_repository.ts": "export class InvoiceRepository {\n  find(id) { return id; }\n}\n",
}


# A domain model, the only file of its folder: one aggregate whose root and repository no code declares.
_SHOP_DOMAIN_MODEL = (
    "# Domain Model — Shop\n"
    "\n"
    "## Sales | custom\n"
    "\n"
    "### Cart\n"
    "\n"
    "#### Cart <<Aggregate Root>> <<Entity>>\n"
    "\n"
    "------\n"
    "+ total: int\n"
    "----\n"
    "+ add(item: str): Cart\n"
    "\n"
    "#### CartRepository <<Repository>>\n"
    "\n"
    "------\n"
    "----\n"
    "+ load(id: str): Cart\n"
)


def blocks_of(fixture: RuleFixture, kind: str) -> list:
    """The building blocks of kind DDD's graph holds."""
    return fixture.practice.reading.in_graph.nodes(kind)


def mappings_of(graph: Graph) -> list[tuple]:
    """Each context mapping on graph's DDD practice: its name, its line, the context it sits under, and the aggregates
    its sides name."""
    ddd = graph.practice("ddd").reading
    found = []
    for mapping in ddd.in_graph.nodes("ContextMapping"):
        sides = tuple((side, [edge.child.name for edge in graph.edges.from_parent(side, mapping)]) for side in ("local", "remote"))
        found.append((mapping.name, mapping.source.start_line, graph.edges.direct_parent(mapping).name, sides))
    return found


with description("DDD's reading of a working copy into the graph"):
    with context("whose bounded context lists a context mapping"):
        with before.all:
            self.fixture = RuleFixture(Ddd, _SALES)
            self.graph = self.fixture.practice.reading.graph

        with it("should hold the mapping under the bounded context, linked to the aggregates its sides name"):
            expect(mappings_of(self.graph)).to(equal([
                ("Sales · cart → Billing · invoice", 4, "Sales", (("local", ["cart"]), ("remote", ["invoice"]))),
            ]))

        with it("should save the two sides the mapping names"):
            mapping = self.graph.practice("ddd").reading.in_graph.nodes("ContextMapping")[0]
            expect((mapping.get_fact("local"), mapping.get_fact("remote"))).to(equal(("Sales · cart", "Billing · invoice")))

        with context("that is opened again from its saved graph"):
            with before.all:
                self.graph.save_json()
                self.reopened = Graph()
                self.reopened.reads.open_saved(self.fixture.root)

            with it("should hold the mappings the build that saved it held"):
                expect(mappings_of(self.reopened)).to(equal(mappings_of(self.graph)))


with description("DDD's reading of a domain model no code realizes yet"):
    with context("with a folder whose only file is a domain model"):
        with before.all:
            self.fixture = RuleFixture(Ddd, {"src/.context/domain-model.md": _SHOP_DOMAIN_MODEL})
            self.roots = blocks_of(self.fixture, "EntityRoot")

        with it("should hold the aggregate root the document describes as a building block"):
            expect([root.name for root in self.roots]).to(equal(["Cart"]))

        with it("should keep the stereotypes the document gives the root"):
            expect(self.roots[0].get_fact("stereotypes") if self.roots else None).to(equal(["Aggregate Root", "Entity"]))

        with it("should hold the root and its repository in the aggregate the document names"):
            aggregates = self.fixture.practice.reading.in_graph.nodes("Aggregate")
            edges = self.fixture.practice.reading.graph.edges
            held = [(kind, [edge.child.name for edge in edges.from_parent(kind, aggregates[0])]) for kind in ("root", "owns")] if aggregates else []
            expect(([node.name for node in aggregates], held)).to(equal((["Cart"], [("root", ["Cart"]), ("owns", ["CartRepository"])])))

        with it("should place the root at the document's line that names it"):
            source = self.roots[0].source if self.roots else None
            expect((source.file, source.start_line) if source else None).to(equal(("src/.context/domain-model.md", 7)))


# A domain model whose cards relate their classes: the Cart composes its Lines and associates with a Customer in another
# aggregate; the Coupon is related to nothing.
_RELATED_DOMAIN_MODEL = (
    "# Domain Model — Shop\n"
    "\n"
    "## Sales | custom\n"
    "\n"
    "### Cart\n"
    "\n"
    "#### Cart <<Aggregate Root>> <<Entity>>\n"
    "\n"
    "------\n"
    "+ << composition >> lines: Line[]\n"
    "+ << association >> customer: Customer\n"
    "\n"
    "#### CartRepository <<Repository>>\n"
    "\n"
    "------\n"
    "+ << aggregation >> carts: Collection<Cart>\n"
    "\n"
    "#### Line <<Entity>>\n"
    "\n"
    "------\n"
    "+ nickname: string\n"
    "\n"
    "#### Coupon <<Value Object>>\n"
    "\n"
    "------\n"
    "+ code: string\n"
    "\n"
    "### Customer\n"
    "\n"
    "#### Customer <<Aggregate Root>> <<Entity>>\n"
    "\n"
    "------\n"
    "+ name: string\n"
    "\n"
    "#### CustomerRepository <<Repository>>\n"
    "\n"
    "------\n"
    "+ << aggregation >> customers: Collection<Customer>\n"
)


def orphaned_in(fixture: RuleFixture) -> list[str]:
    """The building blocks no-orphaned-objects reports, by name."""
    rule = next(rule for rule in fixture.practice.reading.graph_checks.values() if getattr(rule, "slug", "") == "no-orphaned-objects")
    run = SchemaRuleRun(rule, fixture.context)
    return sorted(node.name for node in fixture.context.nodes() if run.node_hits(node))


with description("DDD's reading of the relationships a domain model's cards declare"):
    with before.all:
        self.fixture = RuleFixture(Ddd, {"src/.context/domain-model.md": _RELATED_DOMAIN_MODEL})
        self.edges = self.fixture.practice.reading.graph.edges
        self.cart = next(iter(blocks_of(self.fixture, "EntityRoot")), None)

    with it("should relate the root to the class it composes and the class it associates with"):
        related = sorted(edge.child.name for edge in self.edges.from_parent("dependsOn", self.cart)) if self.cart else []
        expect(related).to(equal(["Customer", "Line"]))

    with it("should report no class the document relates to another as orphaned, only the one it relates to none"):
        expect(orphaned_in(self.fixture)).to(equal(["Coupon"]))


# A bookshop of three bounded contexts as its two documents write it, after the templates: the bounded-context map
# with integrations and events, and the domain model whose roots hold one another by identity.
_THREE_CONTEXTS = Path(__file__).resolve().parent / "_examples" / "trip" / "three-contexts"
_BOOKSHOP_DOCUMENTS = {
    ".context/bounded-context-map.md": (_THREE_CONTEXTS / "bounded-context-map.md").read_text(encoding="utf-8"),
    ".context/domain-model.md": (_THREE_CONTEXTS / "domain-model.md").read_text(encoding="utf-8"),
}


def ddd_nodes(fixture: RuleFixture, kind: str) -> list:
    return fixture.practice.reading.in_graph.nodes(kind)


def reached(fixture: RuleFixture, kind: str, node) -> list[str]:
    """The names of the nodes an edge of kind leads to from node, in order of name."""
    return sorted(edge.child.name for edge in fixture.practice.reading.graph.edges.from_parent(kind, node))


def held_in(fixture: RuleFixture, kind: str) -> dict:
    """The nodes of kind, by the name of the node each sits under."""
    edges = fixture.practice.reading.graph.edges
    held: dict = {}
    for node in ddd_nodes(fixture, kind):
        held.setdefault(edges.direct_parent(node).name, []).append(node.name)
    return {parent: sorted(names) for parent, names in held.items()}


with description("DDD's reading of a bounded context map and a domain model no code realizes yet"):
    with before.all:
        self.fixture = RuleFixture(Ddd, _BOOKSHOP_DOCUMENTS)

    with it("should hold each bounded context the documents head, and no context for the folder"):
        expect(sorted(node.name for node in ddd_nodes(self.fixture, "BoundedContext"))).to(equal(["Catalogue", "Fulfilment", "Ordering"]))

    with it("should hold each aggregate once, under the bounded context that heads it"):
        expect(held_in(self.fixture, "Aggregate")).to(equal({"Ordering": ["Cart", "Order"], "Catalogue": ["Book"], "Fulfilment": ["Shipment"]}))

    with it("should hold each integration as a context mapping from its aggregate to the aggregate it reaches, with its pattern"):
        mappings = [
            (reached(self.fixture, "local", node), reached(self.fixture, "remote", node), node.get_fact("pattern"))
            for node in ddd_nodes(self.fixture, "ContextMapping")
        ]
        expect(sorted(mappings)).to(equal([
            (["Cart"], ["Book"], "Customer/Supplier"),
            (["Order"], ["Shipment"], "Open Host / Published Language"),
            (["Shipment"], ["Order"], "Conformist"),
        ]))

    with it("should hold each mapping under the bounded context of the aggregate that has the dependency"):
        expect({parent: len(names) for parent, names in held_in(self.fixture, "ContextMapping").items()}).to(equal({"Ordering": 2, "Fulfilment": 1}))

    with it("should hold each event of the event map, with the aggregate that emits it and the aggregates that consume it"):
        events = [
            (node.name, reached(self.fixture, "producer", node), reached(self.fixture, "consumers", node))
            for node in ddd_nodes(self.fixture, "DomainEvent")
        ]
        expect(sorted(events)).to(equal([("CartCheckedOut", ["Cart"], ["Order"]), ("OrderPaid", ["Order"], ["Shipment"])]))

    with it("should associate each root with the root its aggregate's integration reaches"):
        associated = {root.name: reached(self.fixture, "associates", root) for root in ddd_nodes(self.fixture, "EntityRoot")}
        expect(associated).to(equal({"Cart": ["Book"], "Order": ["Shipment"], "Book": [], "Shipment": ["Order"]}))

    with it("should relate a root to the classes its members are typed by and the classes its operations call"):
        cart = next(root for root in ddd_nodes(self.fixture, "EntityRoot") if root.name == "Cart")
        expect(reached(self.fixture, "dependsOn", cart)).to(equal(["BookRepository", "CartLine", "Order", "OrderRepository"]))

    with it("should find the model conforms to the schema: a root is not required to associate with another"):
        expect(SchemaRuleRun(FRAMEWORK_RULES["conforms-to-schema"], self.fixture.context).hits()).to(equal([]))


_ORDERING_CODE = {
    "ordering/.context/bounded-context.md": "# Ordering\n\nWhere a Customer fills a Cart.\n\nCart → Catalogue · Book\n",
    "catalogue/.context/bounded-context.md": "# Catalogue\n\nThe books the shop sells.\n",
    "ordering/cart/cart.py": (
        "@aggregate_root\n@entity\nclass Cart:\n"
        '    """Module: Ordering | custom · Cart\n---<<Customer/Supplier>>--> Book\ncontext: Catalogue\naggregate: Book\nentity: Book\nheld_by: BookId"""\n\n'
        "    cartId: CartId\n    # << association >>\n    # held by identity — Book lives in Catalogue · Book\n    bookId: BookId\n\n"
        "    def total(self) -> Money:\n        return 1\n\n\n"
        "@repository\nclass CartRepository:\n    def load(self, cartId: CartId) -> Cart:\n        return cartId\n"
    ),
    "ordering/cart/cart.ts": (
        "/**\n * Module: Ordering | custom · Cart\n * ---<<Customer/Supplier>>--> Book\n * context: Catalogue\n * aggregate: Book\n * entity: Book\n */\n"
        "@AggregateRoot()\n@Entity()\nclass Cart {\n  cartId: CartId;\n  total(): Money { return 1; }\n}\n\n"
        "@Repository()\nclass CartRepository {\n  load(cartId: CartId): Cart { return cartId; }\n}\n"
    ),
    "catalogue/book/book.py": (
        "@aggregate_root\n@entity\nclass Book:\n    bookId: BookId\n\n    def reprice(self, amount: Money) -> None:\n        return None\n\n\n"
        "@repository\nclass BookRepository:\n    def load(self, bookId: BookId) -> Book:\n        return bookId\n"
    ),
    "catalogue/book/book.ts": (
        "@AggregateRoot()\n@Entity()\nclass Book {\n  bookId: BookId;\n  reprice(amount: Money): void { return; }\n}\n\n"
        "@Repository()\nclass BookRepository {\n  load(bookId: BookId): Book { return bookId; }\n}\n"
    ),
}


def files_reached(fixture: RuleFixture, kind: str, node) -> list[str]:
    return sorted(edge.child.source.file for edge in fixture.practice.reading.graph.edges.from_parent(kind, node))


with description("DDD's reading of aggregates written in two languages, in folders named in lower case"):
    with before.all:
        self.fixture = RuleFixture(Ddd, _ORDERING_CODE)

    with it("should link a mapping's sides to the aggregates whose folders spell its names in lower case"):
        mapping = ddd_nodes(self.fixture, "ContextMapping")[0]
        expect((reached(self.fixture, "local", mapping), reached(self.fixture, "remote", mapping))).to(equal((["cart"], ["book"])))

    with it("should have each repository access the root declared in its own file"):
        repositories = [block for block in ddd_nodes(self.fixture, "Repository") if block.name == "CartRepository"]
        accessed = sorted((block.source.file, files_reached(self.fixture, "accesses", block)) for block in repositories)
        expect(accessed).to(equal([("ordering/cart/cart.py", ["ordering/cart/cart.py"]), ("ordering/cart/cart.ts", ["ordering/cart/cart.ts"])]))

    with it("should associate a root with the root its integration reaches, the one written in its own language"):
        roots = [block for block in ddd_nodes(self.fixture, "EntityRoot") if block.name == "Cart"]
        associated = sorted((root.source.file, files_reached(self.fixture, "associates", root)) for root in roots)
        expect(associated).to(equal([("ordering/cart/cart.py", ["catalogue/book/book.py"]), ("ordering/cart/cart.ts", ["catalogue/book/book.ts"])]))

    with it("should join each building block to the Clean Engineering class read from the same file, which it is"):
        root = next(block for block in ddd_nodes(self.fixture, "EntityRoot") if block.source.file == "ordering/cart/cart.py")
        classes = [edge.child.node_id for edge in self.fixture.practice.reading.graph.edges.from_parent("isA", root)]
        expect(classes).to(equal([root.ooad_class.node_id]))


    with it("should join each aggregate to the Clean Engineering package or module of its folder, which it is"):
        cart = next(node for node in ddd_nodes(self.fixture, "Aggregate") if node.source.file == "ordering/cart")
        expect([edge.child.node_id.split(":", 2)[2] for edge in self.fixture.practice.reading.graph.edges.from_parent("isA", cart)]).to(equal(["ordering/cart"]))

    with context("with a bounded context whose folder has a module card"):
        with before.all:
            self.carded = RuleFixture(Ddd, {**_ORDERING_CODE, "ordering/.context/module-context.md": "# ordering\nWhere a Customer fills a Cart.\n"})

        with it("should join the bounded context to the Clean Engineering module of its folder"):
            ordering = next(node for node in ddd_nodes(self.carded, "BoundedContext") if node.name == "Ordering")
            joined = [edge.child.node_id for edge in self.carded.practice.reading.graph.edges.from_parent("isA", ordering)]
            expect(joined).to(equal(["clean_engineering:Module:ordering"]))

        with it("should join no module to a bounded context whose folder Clean Engineering reads nothing from"):
            catalogue = next(node for node in ddd_nodes(self.carded, "BoundedContext") if node.name == "Catalogue")
            expect(self.carded.practice.reading.graph.edges.from_parent("isA", catalogue)).to(equal([]))


with description("DDD's reading of a domain model beside the code that implements it"):
    with before.all:
        self.fixture = RuleFixture(
            Ddd,
            {
                "src/.context/domain-model.md": _SHOP_DOMAIN_MODEL,
                "src/cart/cart.py": "@aggregate_root\nclass Cart:\n    def total(self) -> int:\n        return 1\n",
            },
        )
        self.roots = {root.source.file: root for root in blocks_of(self.fixture, "EntityRoot")}

    with it("should hold the root the document describes and the root the code declares, neither in place of the other"):
        expect(sorted(self.roots)).to(equal(["src/.context/domain-model.md", "src/cart/cart.py"]))

    with it("should join the code's root to the document's root it implements, in the aggregate its folder names"):
        code = self.roots.get("src/cart/cart.py")
        expect(files_reached(self.fixture, "implements", code) if code else None).to(equal(["src/.context/domain-model.md"]))


# A bounded context's own file names each aggregate as a link to that aggregate's heading in the domain model. Here
# the links say what the names alone would not: Ordering's link is titled Cart and opens the heading Shopping Cart, the
# domain model heads Book under Library while Catalogue's file links it, and Ordering's file links no Order.
_LINK = "../../.context/domain-model.md"
_LINKED_SHOP = {
    "ordering/.context/bounded-context.md": f"# Ordering\n\nAggregates:\n- [Cart]({_LINK}#shopping-cart)\n\nCart → Catalogue · Book\n",
    "catalogue/.context/bounded-context.md": f"# Catalogue\n\nAggregates:\n- [Book]({_LINK}#book)\n",
    ".context/domain-model.md": (
        "# Domain Model — Bookshop\n\n"
        "## Ordering | custom\n\n"
        "### Shopping Cart\n\n#### Cart <<Aggregate Root>> <<Entity>>\n\n------\n+ cartId: CartId\n----\n+ total(): Money\n\n"
        "### Order\n\n#### Order <<Aggregate Root>> <<Entity>>\n\n------\n+ orderId: OrderId\n----\n+ submit(): void\n\n"
        "## Library | custom\n\n"
        "### Book\n\n#### Book <<Aggregate Root>> <<Entity>>\n\n------\n+ isbn: Isbn\n----\n+ price(): Money\n"
    ),
}


def aggregates_owned_by(fixture: RuleFixture, context_name: str) -> list[str]:
    """The aggregates the graph puts under the bounded context called context_name, in order of name."""
    owner = next(node for node in ddd_nodes(fixture, "BoundedContext") if node.name == context_name)
    owned = fixture.practice.reading.graph.edges.from_parent("owns", owner)
    return sorted(edge.child.name for edge in owned if edge.child.type == "Aggregate")


with description("DDD's reading of bounded contexts whose files link their aggregates to the domain model"):
    with before.all:
        self.fixture = RuleFixture(Ddd, _LINKED_SHOP)

    with it("should give a context the aggregate at the heading its link opens, whatever words the link shows"):
        expect(aggregates_owned_by(self.fixture, "Ordering")).to(equal(["Shopping Cart"]))

    with it("should give a context the aggregate its link opens, though the domain model heads it under another context"):
        expect(aggregates_owned_by(self.fixture, "Catalogue")).to(equal(["Book"]))

    with it("should not give a context that writes links an aggregate its file does not link, though the domain model heads it under the context's name"):
        expect(aggregates_owned_by(self.fixture, "Ordering")).not_to(contain("Order"))

    with it("should link a mapping's sides to the aggregates the two contexts' links open by those names"):
        mapping = ddd_nodes(self.fixture, "ContextMapping")[0]
        expect((reached(self.fixture, "local", mapping), reached(self.fixture, "remote", mapping))).to(equal((["Shopping Cart"], ["Book"])))

    with context("beside a context whose file names its aggregates in plain words"):
        with before.all:
            plain = {**_LINKED_SHOP, "ordering/.context/bounded-context.md": "# Ordering\n\nAggregates:\n- Shopping Cart\n- Order\n"}
            self.fixture = RuleFixture(Ddd, plain)

        with it("should give that context the aggregates the domain model heads under its name, as it always has"):
            expect(aggregates_owned_by(self.fixture, "Ordering")).to(equal(["Order", "Shopping Cart"]))
