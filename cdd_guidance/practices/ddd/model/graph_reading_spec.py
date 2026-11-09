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
from harness.graph.rule_fixture import RuleFixture  # noqa: E402

_SALES = {
    "src/.context/bounded-context.md": "# Sales\n\nMappings:\n- Sales · cart → Billing · invoice\n",
    "src/cart/cart.ts": "export class Cart {\n  total() { return 1; }\n}\n",
    "src/cart/cart_repository.ts": "export class CartRepository {\n  find(id) { return id; }\n}\n",
    "src/invoice/invoice.ts": "export class Invoice {\n  amount() { return 1; }\n}\n",
    "src/invoice/invoice_repository.ts": "export class InvoiceRepository {\n  find(id) { return id; }\n}\n",
}


def mappings_of(graph: Graph) -> list[tuple]:
    """Each context mapping on graph's DDD practice: its name, its line, the context it sits under, and the aggregates
    its sides name."""
    ddd = graph.practice("ddd").reading
    found = []
    for mapping in ddd.in_graph.nodes("ContextMapping"):
        sides = tuple((side, [edge.child.name for edge in graph.edges_from(side, mapping)]) for side in ("local", "remote"))
        found.append((mapping.name, mapping.source.start_line, graph.direct_parent(mapping).name, sides))
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
                self.reopened.open_saved(self.fixture.root)

            with it("should hold the mappings the build that saved it held"):
                expect(mappings_of(self.reopened)).to(equal(mappings_of(self.graph)))
