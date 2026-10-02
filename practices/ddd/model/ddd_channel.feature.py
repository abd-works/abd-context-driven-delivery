"""Channel round trip. Not collected with the other specs.

Loads the expected markdown, writes the markdown channel under actual, and
reads each node's own children.

    .\\.venv\\Scripts\\python.exe -m mamba.cli practices/ddd/model/ddd_channel.feature.py
"""

import shutil
from pathlib import Path

from expects import equal, expect
from mamba import before, describe, included_context, it, shared_context

from practices.clean_engineering.model.property import Property
from practices.ddd.model.knowledge_graph.nodes import KnowledgeGraphDomainDrivenDesignModel
from practices.ddd.model.nodes import DDDModelFactory, DomainEvent, ValueObject

EXPECTED = Path(__file__).resolve().parent / ".examples" / "expected" / "bounded-context-map.md"
ACTUAL = Path(__file__).resolve().parent / ".examples" / "actual"


def _events(aggregate):
    if aggregate.root is None:
        return []
    return [item for item in aggregate.root.properties if isinstance(item, DomainEvent)]


def check_map(loaded) -> None:
    expect(len(loaded.contexts)).to(equal(2))
    sales, catalog = loaded.contexts
    expect(sales.name).to(equal("Sales"))
    expect(sales.owner).to(equal("custom"))
    expect(catalog.name).to(equal("Catalog"))
    expect(catalog.owner).to(equal("bespoke"))

    expect(len(sales.aggregates)).to(equal(1))
    cart = sales.aggregates[0]
    expect(cart.name).to(equal("ShoppingCart"))
    expect(cart.root.name).to(equal("ShoppingCart"))
    expect(cart.root.is_root).to(equal(True))
    expect(cart.root.aggregate).to(equal(cart))
    expect([item.name for item in cart.root.invariant_objects]).to(equal(["CartItem", "Discount"]))
    expect(cart.root.invariant_objects[0].stereotype).to(equal("invariant"))

    expect(len(cart.integrations)).to(equal(1))
    integration = cart.integrations[0]
    expect(integration.target).to(equal("Product"))
    expect(integration.pattern).to(equal("Customer/Supplier"))
    expect(integration.direction).to(equal("downstream"))
    expect(integration.crosses).to(equal("unit price"))
    expect(integration.integration).to(equal("synchronous call to Catalog.Product.unit_price at add_item"))

    expect(len(_events(cart))).to(equal(1))
    event = _events(cart)[0]
    expect(event.producer).to(equal(cart))
    expect(isinstance(event.subject, Property)).to(equal(True))
    expect([item.name for item in event.consumers]).to(equal(["Product"]))

    expect(catalog.aggregates[0].name).to(equal("Product"))
    expect(catalog.aggregates[0].root.is_root).to(equal(True))


with shared_context("a domain driven design model saved through a channel"):
    with it("should match each bounded context, aggregate, integration, and event"):
        check_map(self.loaded)


with describe("a domain driven design model"):
    with describe("from markdown"):
        with describe("to markdown"):
            with before.all:
                source = DDDModelFactory.load(str(EXPECTED))
                folder = ACTUAL / "from-markdown" / "to-markdown"
                if folder.exists():
                    shutil.rmtree(folder)
                folder.mkdir(parents=True)
                written = folder / "bounded-context-map.md"
                written.write_text(source.save(), encoding="utf-8")
                self.loaded = DDDModelFactory.load(str(written))
            with included_context("a domain driven design model saved through a channel"):
                pass
        with describe("to knowledge graph"):
            with before.all:
                source = DDDModelFactory.load(str(EXPECTED))
                folder = ACTUAL / "from-markdown" / "to-knowledge-graph"
                if folder.exists():
                    shutil.rmtree(folder)
                folder.mkdir(parents=True)
                self.loaded = KnowledgeGraphDomainDrivenDesignModel(source)
                (folder / "bounded-context-map.kg").write_text(self.loaded.save(), encoding="utf-8")
            with included_context("a domain driven design model saved through a channel"):
                pass

    with it("should load the expected map"):
        check_map(DDDModelFactory.load(str(EXPECTED)))

    with it("should return a new value object from create, clone, and mix"):
        original = ValueObject("Money", 1)
        created = original.create()
        cloned = original.clone()
        mixed = original.mix(ValueObject("Money", 2, intent="combined"))
        expect(created is original).to(equal(False))
        expect(cloned is original).to(equal(False))
        expect(mixed is original).to(equal(False))
        expect(created.name).to(equal("Money"))
        expect(mixed.intent).to(equal("combined"))
