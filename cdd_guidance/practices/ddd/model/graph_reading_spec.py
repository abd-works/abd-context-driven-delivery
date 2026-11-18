"""DDD's reading of a working copy into the graph: the context mappings a bounded context lists are DDD's own nodes,
whether or not a pattern is applied, and a graph opened from its save holds them as the build that saved it did."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect  # noqa: E402
from mamba import before, context, description, it  # noqa: E402

from cdd_guidance.practices.ddd.ddd import Ddd  # noqa: E402
from harness.graph.graph import Graph  # noqa: E402
from harness.graph.rule_fixture import RuleFixture, SchemaRuleRun  # noqa: E402

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

    with context("with code that declares the root the domain model describes"):
        with before.all:
            self.fixture = RuleFixture(
                Ddd,
                {
                    "src/.context/domain-model.md": _SHOP_DOMAIN_MODEL,
                    "src/cart/cart.py": "@aggregate_root\nclass Cart:\n    def total(self) -> int:\n        return 1\n",
                },
            )

        with it("should hold one building block for the root, the one the code declares"):
            expect([(root.name, root.source.file) for root in blocks_of(self.fixture, "EntityRoot")]).to(equal([("Cart", "src/cart/cart.py")]))


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
