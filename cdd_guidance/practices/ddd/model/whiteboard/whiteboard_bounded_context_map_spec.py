"""WhiteboardBoundedContextMap — the bounded-context map and the aggregate view drawn by Clean Engineering's whiteboard,
as the drawio channel draws them: contexts as sections holding their aggregates, building blocks as class cards."""

from pathlib import Path

from expects import be_above, be_true, equal, expect
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

        with it("should draw no «from:» copy of a class another aggregate owns"):
            copies = [element.text for element in self.board.elements if isinstance(element, Shape) and "«from:" in element.text]
            expect(copies).to(equal([]))

        with it("should draw a call into another aggregate's repository as one arrow to the root's card the repository is drawn in"):
            ids = {element.text.split("**")[1]: element.id for element in self.board.elements if isinstance(element, Shape) and element.role == "class"}
            calls = [(arrow.from_id, arrow.to_id) for arrow in self.board.elements if isinstance(arrow, Arrow) and arrow.label == "«sendSupportRequest»"]
            expect(calls).to(equal([(ids["CustomerProfile"], ids["KycInquiry"])]))

        with it("should draw each integration from the root as one arrow to the root it reaches, named by its pattern"):
            ids = {element.text.split("**")[1]: element.id for element in self.board.elements if isinstance(element, Shape) and element.role == "class"}
            reached = [(arrow.from_id, arrow.to_id) for arrow in self.board.elements if isinstance(arrow, Arrow) and arrow.label == "«Customer/Supplier»"]
            expect(reached).to(equal([(ids["Subscription"], ids["CustomerProfile"])]))

        with it("should read back each aggregate's classes"):
            def classes(drawn):
                return sorted((aggregate.name, sorted(oclass.name for oclass in aggregate.classes)) for aggregate in drawn.every_aggregate)
            expect(classes(WhiteboardBoundedContextMap().parse(self.text))).to(equal(classes(self.source)))

    with context("that draws a domain model whose repository is written inside its root's card"):
        with before.all:
            folded = _MODEL.replace("#### KycInquiryRepository <<Repository>>", "**KycInquiryRepository** «Repository»")
            self.text = WhiteboardBoundedContextMap().render(MarkdownBoundedContextMap().parse(folded))
            cards = [element.text for element in Whiteboard.from_text(self.text).elements if isinstance(element, Shape) and element.role == "class"]
            self.root = next(card for card in cards if "**KycInquiry**" in card and "«from:" not in card)
            self.cards = cards

        with it("should draw the repository inside its root's card, not as a card of its own"):
            expect([card for card in self.cards if "**KycInquiryRepository**" in card]).to(equal([self.root]))

        with it("should head the repository's part of the card with its «Repository» stereotype, below the root's operations"):
            expect(self.root.index("*«Repository»*\n**KycInquiryRepository**")).to(be_above(self.root.index("+ verify()")))

        with it("should read the repository back as the aggregate's repository, with its operations"):
            kyc = next(item for item in WhiteboardBoundedContextMap().parse(self.text).every_aggregate if item.name == "KYC")
            expect((kyc.repository.name, [item.name for item in kyc.repository.operations])).to(
                equal(("KycInquiryRepository", ["create", "load", "update"])))

    with context("that draws a domain model of two contexts, one holding two aggregates"):
        with before.all:
            self.board = Whiteboard.from_text(WhiteboardBoundedContextMap().render(MarkdownBoundedContextMap().parse(_TWO_CONTEXTS)))
            self.sections = [element for element in self.board.whole_elements if isinstance(element, Section)]
            self.by_text = {element.text: element for element in self.sections}
            self.cards = [element for element in self.board.whole_elements if isinstance(element, Shape) and element.role in ("class", "imported")]

        with it("should label each aggregate's container with the aggregate's name and each context's with the context's name"):
            expect(sorted(self.by_text)).to(equal(["Cart", "Inventory", "Plans", "Revenue", "Subscription"]))

        with it("should draw each aggregate's container inside its context's container, with room for its title"):
            for context_name, aggregate_names in (("Revenue", ("Cart", "Subscription")), ("Inventory", ("Plans",))):
                for aggregate_name in aggregate_names:
                    expect(_encloses(self.by_text[context_name], self.by_text[aggregate_name], _TITLE_ROOM)).to(be_true)

        with it("should draw no class card across the edge of its aggregate's container"):
            aggregates = [self.by_text[name] for name in ("Cart", "Subscription", "Plans")]
            for card in self.cards:
                holder = next(section for section in aggregates if section.holds(card))
                expect(_encloses(holder, card, 0)).to(be_true)

        with it("should put the context containers first in the order, then the aggregate containers"):
            sections = [element_id for element_id in self.board.order if element_id in {section.id for section in self.sections}]
            texts = [self.board.element(element_id).text for element_id in sections]
            expect(texts[:2]).to(equal(["Revenue", "Inventory"]))
            expect(sorted(texts[2:])).to(equal(["Cart", "Plans", "Subscription"]))

        with it("should lay the contexts out left to right"):
            expect(self.by_text["Revenue"].box.x + self.by_text["Revenue"].box.w < self.by_text["Inventory"].box.x).to(be_true)


_INSET = 24
_TITLE_ROOM = 28


def _encloses(outer, inner, title_room):
    """Whether inner sits inside outer, _INSET in from each edge, with title_room above it for its title."""
    return (outer.box.x + _INSET <= inner.box.x and inner.box.x + inner.box.w <= outer.box.x + outer.box.w - _INSET
            and outer.box.y + _INSET + title_room <= inner.box.y and inner.box.y + inner.box.h <= outer.box.y + outer.box.h - _INSET)


_TWO_CONTEXTS = """# Domain Model

## Revenue | custom

### Cart

#### Cart <<Aggregate Root>> <<Entity>>

------
+ id: string
+ << composition >> items: CartItem
----
+ addItem(sku: string): void

#### CartItem <<Value Object>>

------
+ sku: string
+ quantity: number
----

### Subscription

#### Subscription <<Aggregate Root>> <<Entity>>

------
+ id: string
+ << association >> cart: Cart
----
+ renew(): void

## Inventory | custom

### Plans

#### Plan <<Aggregate Root>> <<Entity>>

------
+ planId: string
+ price: number
----
"""
