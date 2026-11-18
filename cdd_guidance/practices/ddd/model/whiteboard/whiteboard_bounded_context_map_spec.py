"""WhiteboardBoundedContextMap — the bounded-context map and the aggregate view drawn by Clean Engineering's whiteboard,
as the drawio channel draws them: contexts as sections holding their aggregates, building blocks as class cards."""

from pathlib import Path

from expects import be_true, equal, expect
from mamba import before, context, description, it

from harness.whiteboard.whiteboard import Arrow, Section, Shape, Whiteboard
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap
from cdd_guidance.practices.ddd.model.whiteboard.whiteboard_bounded_context_map import WhiteboardBoundedContextMap

_EXAMPLES = Path(__file__).resolve().parent.parent / "_examples" / "expected"
_MAP = (_EXAMPLES / "bounded-context-map.md").read_text(encoding="utf-8")
_MODEL = (_EXAMPLES / "domain-model.md").read_text(encoding="utf-8")


def _map_summary(drawn):
    return [
        (context_.module_path, [(aggregate.name, aggregate.drawn_members,
                                 [(drawn.aggregate_reached_by(item).module_path, item.pattern) for item in aggregate.integrations])
                                for aggregate in context_.aggregates])
        for context_ in drawn.every_context
    ]


with description("WhiteboardBoundedContextMap"):
    with context("that draws a bounded context map"):
        with before.all:
            self.source = MarkdownBoundedContextMap().parse(_MAP)
            self.text = WhiteboardBoundedContextMap().render(self.source)
            self.board = Whiteboard.from_text(self.text)
            self.contexts = {element.text: element for element in self.board.elements if isinstance(element, Section) and element.role == "context"}
            self.aggregates = {element.text.split("**")[1]: element for element in self.board.elements
                               if isinstance(element, Shape) and element.role == "aggregate"}

        with it("should draw each context as a section"):
            expect(sorted(self.contexts)).to(equal(["Catalog | bespoke", "Sales | custom"]))

        with it("should draw each aggregate inside its context's section"):
            expect(self.contexts["Sales | custom"].holds(self.aggregates["Sales | custom/ShoppingCart"])).to(be_true)

        with it("should list the aggregate's members as its bullets"):
            lines = self.aggregates["Sales | custom/ShoppingCart"].text.splitlines()
            expect("- CartItem" in lines and "- Discount" in lines).to(be_true)

        with it("should draw each integration as a dependency arrow named by its pattern"):
            ends = [(arrow.from_id, arrow.to_id, arrow.label) for arrow in self.board.elements if isinstance(arrow, Arrow)]
            expect(ends).to(equal([(self.aggregates["Sales | custom/ShoppingCart"].id,
                                    self.aggregates["Catalog | bespoke/Product"].id, "Customer/Supplier")]))

        with it("should read back every context, aggregate, member and integration"):
            expect(_map_summary(WhiteboardBoundedContextMap().parse(self.text))).to(equal(_map_summary(self.source)))

    with context("that draws an aggregate reaching two members of one other aggregate"):
        with before.all:
            twice = _MAP.replace("    integration: synchronous call to Catalog.Product.unit_price at add_item\n",
                                 "    integration: synchronous call to Catalog.Product.unit_price at add_item\n"
                                 "  - Product (by Sku)\n    pattern: Conformist\n    direction: downstream\n")
            self.board = Whiteboard.from_text(WhiteboardBoundedContextMap().render(MarkdownBoundedContextMap().parse(twice)))

        with it("should draw one arrow to that aggregate, named by the first integration's pattern"):
            labels = [arrow.label for arrow in self.board.elements if isinstance(arrow, Arrow)]
            expect(labels).to(equal(["Customer/Supplier"]))

    with context("that draws a domain model"):
        with before.all:
            self.source = MarkdownBoundedContextMap().parse(_MODEL)
            self.text = WhiteboardBoundedContextMap().render(self.source)
            self.board = Whiteboard.from_text(self.text)

        with it("should draw each building block as a class card with its stereotypes"):
            cards = [element.text for element in self.board.elements if isinstance(element, Shape) and element.role == "class"]
            expect(any("*«Aggregate Root» «Entity»*" in card and "**CustomerProfile**" in card for card in cards)).to(be_true)

        with it("should read back each aggregate's classes"):
            def classes(drawn):
                return sorted((aggregate.name, sorted(oclass.name for oclass in aggregate.classes)) for aggregate in drawn.every_aggregate)
            expect(classes(WhiteboardBoundedContextMap().parse(self.text))).to(equal(classes(self.source)))
