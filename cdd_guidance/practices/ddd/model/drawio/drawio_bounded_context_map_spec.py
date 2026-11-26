"""DrawIOBoundedContextMap — the bounded-context map and the aggregate view drawn by Clean Engineering's draw.io
diagram: contexts and aggregates as nested modules, building blocks as classes with their stereotypes."""

import html
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from expects import be_above, be_below, be_empty, be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner
from harness.drawio import CellStyle, DrawioCell
from cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map import DrawIOAggregateCell, DrawIOBoundedContextMap
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

_EXAMPLES = Path(__file__).resolve().parent.parent / "_examples" / "expected"
_MAP = (_EXAMPLES / "bounded-context-map.md").read_text(encoding="utf-8")
_MODEL = (_EXAMPLES / "domain-model.md").read_text(encoding="utf-8")
# A bookshop of three bounded contexts written after the template: each repository under its own `####` heading.
_SHOP_MODEL = (_EXAMPLES.parent / "trip" / "three-contexts" / "domain-model.md").read_text(encoding="utf-8")


def _cells(xml):
    return {cell.get("id"): cell for cell in ET.fromstring(xml).iter("mxCell")}


def _arrows(xml):
    return [cell for cell in ET.fromstring(xml).iter("mxCell") if cell.get("edge") == "1"]


def _containers(xml, kind):
    """The box of each container cell of kind, by the words it is titled with."""
    return {
        html.unescape(cell.get("value")): DrawioCell(cell).box
        for cell in ET.fromstring(xml).iter("mxCell")
        if CellStyle(cell.get("style", "")).value("kind") == kind
    }


def _class_cards(xml):
    """The box of each class card, by the module its style keeps it in and its id."""
    return {
        (CellStyle(cell.get("style", "")).value("module"), cell.get("id")): DrawioCell(cell).box
        for cell in ET.fromstring(xml).iter("mxCell")
        if CellStyle(cell.get("style", "")).value("module")
    }


def _holds(outer, inner):
    return (
        outer.x <= inner.x and outer.y < inner.y
        and inner.x + inner.w <= outer.x + outer.w and inner.y + inner.h <= outer.y + outer.h
    )


def _overlap(first, second):
    return (
        first.x < second.x + second.w and second.x < first.x + first.w
        and first.y < second.y + second.h and second.y < first.y + first.h
    )


def _overlapping(boxes):
    boxes = list(boxes)
    return [(one, other) for index, one in enumerate(boxes) for other in boxes[index + 1:] if _overlap(one, other)]


def _layout_violations(xml):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "model.drawio"
        path.write_text(xml, encoding="utf-8")
        return [
            violation.message
            for slug, scanner_type in DrawioScanner.every().items()
            for violation in scanner_type(rule=slug).scan_file(Path(folder), path)
        ]


with description("DrawIOBoundedContextMap"):
    with context("that draws a bounded context map"):
        with before.all:
            self.xml = DrawIOBoundedContextMap().render(MarkdownBoundedContextMap().parse(_MAP))
            self.cells = _cells(self.xml)

        with it("should draw each context as a module"):
            expect(self.cells["sales-custom"].get("parent")).to(equal("1"))

        with it("should nest each aggregate inside its context's module"):
            expect(self.cells["sales-custom-shoppingcart"].get("parent")).to(equal("sales-custom"))

        with it("should list the aggregate's members as the module's bullets"):
            label = self.cells["sales-custom-shoppingcart"].get("value")
            expect("• CartItem" in label and "• Discount" in label).to(be_true)

        with it("should leave the aggregate's prose out of its module"):
            expect("the cart" in self.cells["sales-custom-shoppingcart"].get("value")).to(equal(False))

        with it("should draw each integration as a dependency arrow named by its pattern"):
            ends = [(arrow.get("source"), arrow.get("target"), arrow.get("value")) for arrow in _arrows(self.xml)]
            expect(ends).to(equal([("sales-custom-shoppingcart", "catalog-bespoke-product", "Customer/Supplier")]))

        with it("should place the context an integration reaches before the context it leaves"):
            x = {name: float(self.cells[name].find("mxGeometry").get("x")) for name in ("sales-custom", "catalog-bespoke")}
            expect(x["catalog-bespoke"] < x["sales-custom"]).to(be_true)

        with it("should name each aggregate's kind in its cell's style"):
            expect("kind=aggregate;" in self.cells["sales-custom-shoppingcart"].get("style")).to(be_true)

        with it("should keep the cells it drew as its own modules"):
            drawn = DrawIOBoundedContextMap()
            drawn.render(MarkdownBoundedContextMap().parse(_MAP))
            expect([module.name for module in drawn.modules if isinstance(module, DrawIOAggregateCell)]).to(
                contain("Sales | custom/ShoppingCart")
            )

    with context("that reads back a map whose purpose lines were reworded"):
        with before.all:
            xml = DrawIOBoundedContextMap().render(MarkdownBoundedContextMap().parse(_MAP))
            reworded = xml.replace("&lt;i&gt;aggregate&lt;/i&gt;", "&lt;i&gt;what the business keeps&lt;/i&gt;")
            self.read = DrawIOBoundedContextMap().parse(reworded)

        with it("should read each aggregate by the kind its cell's style names"):
            expect([item.name for item in self.read.every_aggregate]).to(contain("ShoppingCart"))

    with context("that draws a domain model with class cards"):
        with before.all:
            self.xml = DrawIOBoundedContextMap().render(MarkdownBoundedContextMap().parse(_MODEL))
            self.cells = _cells(self.xml)
            self.ends = {(arrow.get("source"), arrow.get("target")): arrow for arrow in _arrows(self.xml)}

        with it("should draw each building block as a class with its stereotypes"):
            label = self.cells["customer-custom-customer-profile--customerprofile"].get("value")
            expect("&lt;&lt;Aggregate Root&gt;&gt; &lt;&lt;Entity&gt;&gt;" in label).to(be_true)

        with it("should draw the repository written under its own heading inside its root's card"):
            expect("customer-custom-customer-profile--customerprofilerepository" in self.cells).to(equal(False))

        with it("should keep each class in the module of its context and aggregate"):
            style = self.cells["customer-custom-kyc--kycinquiry"].get("style")
            expect("module=Customer | custom · KYC;" in style).to(be_true)

        with it("should compose the members under the root"):
            arrow = self.ends[("customer-custom-customer-profile--customerprofile", "customer-custom-customer-profile--identity")]
            expect("startArrow=diamondThin;startFill=1" in arrow.get("style")).to(be_true)

        with it("should land a dependency on another aggregate's root card where an operation calls its repository"):
            arrow = self.ends[("customer-custom-customer-profile--customerprofile", "customer-custom-kyc--kycinquiry")]
            expect(arrow.get("value")).to(equal("«sendSupportRequest»"))

        with it("should draw a dependency from the root along each integration, named by its pattern"):
            arrow = self.ends[("service-custom-subscription--subscription", "customer-custom-customer-profile--customerprofile")]
            expect(arrow.get("value")).to(equal("«Customer/Supplier»"))

        with it("should draw no arrow out of an aggregate that needs no other"):
            leaving = [ends for ends in self.ends if ends[0] == "customer-custom-kyc--kycinquiry"]
            expect(leaving).to(be_empty)

        with it("should pass every Clean Engineering layout scanner"):
            expect(_layout_violations(self.xml)).to(be_empty)

    with context("that draws a domain model whose repository is written inside its root's card"):
        with before.all:
            self.markdown = _MODEL.replace("#### KycInquiryRepository <<Repository>>", "**KycInquiryRepository** «Repository»")
            self.xml = DrawIOBoundedContextMap().render(MarkdownBoundedContextMap().parse(self.markdown))
            self.cells = _cells(self.xml)
            self.root = html.unescape(self.cells["customer-custom-kyc--kycinquiry"].get("value"))
            self.ends = {(arrow.get("source"), arrow.get("target")): arrow for arrow in _arrows(self.xml)}

        with it("should draw the repository inside its root's card, not as a card of its own"):
            expect("customer-custom-kyc--kycinquiryrepository" in self.cells).to(equal(False))

        with it("should head the repository's part of the card with its «Repository» stereotype and its name"):
            expect("<<Repository>>" in self.root and "<b>KycInquiryRepository</b>" in self.root).to(be_true)

        with it("should list the repository's operations under its own heading, below the root's"):
            expect(self.root.index("create(identity: Identity, address: Address)")).to(be_above(self.root.index("<b>KycInquiryRepository</b>")))

        with it("should keep the root's own operations above the repository's heading"):
            expect(self.root.index("verify()")).to(be_below(self.root.index("<b>KycInquiryRepository</b>")))

        with it("should land an arrow to the repository on its root's card"):
            arrow = self.ends[("customer-custom-customer-profile--customerprofile", "customer-custom-kyc--kycinquiry")]
            expect(arrow.get("value")).to(equal("«sendSupportRequest»"))

        with it("should pass every Clean Engineering layout scanner"):
            expect(_layout_violations(self.xml)).to(be_empty)

        with context("that is read back"):
            with before.all:
                read = DrawIOBoundedContextMap().parse(self.xml)
                self.kyc = next(item for item in read.every_aggregate if item.name == "KYC")

            with it("should read the repository as the aggregate's repository"):
                expect(self.kyc.repository.name).to(equal("KycInquiryRepository"))

            with it("should read the repository's operations as its own, not the root's"):
                expect([item.name for item in self.kyc.root_card.operations]).to(equal(["fill", "verify"]))

    with context("that draws a domain model of three bounded contexts written after the template"):
        with before.all:
            self.source = MarkdownBoundedContextMap().parse(_SHOP_MODEL)
            self.xml = DrawIOBoundedContextMap().render(self.source)
            self.cells = _cells(self.xml)
            self.contexts = _containers(self.xml, "boundedContext")
            self.aggregates = _containers(self.xml, "aggregate")
            self.cards = _class_cards(self.xml)

        with it("should draw each bounded context as a container titled with its name and owner"):
            expect(sorted(self.contexts)).to(equal(["Catalogue | custom", "Fulfilment | ShipFast", "Ordering | custom"]))

        with it("should draw each aggregate as a container titled with its name"):
            expect(sorted(self.aggregates)).to(equal(["Book", "Cart", "Order", "Shipment"]))

        with it("should draw each aggregate's container inside its bounded context's container"):
            held = sorted(
                (aggregate, context_name)
                for aggregate, box in self.aggregates.items()
                for context_name, outer in self.contexts.items() if _holds(outer, box)
            )
            expect(held).to(equal([
                ("Book", "Catalogue | custom"), ("Cart", "Ordering | custom"),
                ("Order", "Ordering | custom"), ("Shipment", "Fulfilment | ShipFast"),
            ]))

        with it("should draw each class card inside its aggregate's container"):
            outside = [
                cell_id for (module, cell_id), box in self.cards.items()
                if not _holds(self.aggregates[module.split(" · ")[-1]], box)
            ]
            expect(outside).to(be_empty)

        with it("should draw the root and its members as the cards of the aggregate's container"):
            in_cart = sorted(cell_id for (module, cell_id), _box in self.cards.items() if module.endswith(" · Cart"))
            expect(in_cart).to(equal(["ordering-custom-cart--cart", "ordering-custom-cart--cartline"]))

        with it("should draw each repository written under its own heading inside its root's card, below its operations"):
            root = html.unescape(self.cells["ordering-custom-cart--cart"].get("value"))
            expect(root.index("<b>CartRepository</b>")).to(be_above(root.index("checkOut(")))

        with it("should draw no repository as a card of its own"):
            expect([cell_id for _module, cell_id in self.cards if cell_id.endswith("repository")]).to(be_empty)

        with it("should draw no two bounded contexts over each other"):
            expect(_overlapping(self.contexts.values())).to(be_empty)

        with it("should draw no two aggregates over each other"):
            expect(_overlapping(self.aggregates.values())).to(be_empty)

        with it("should draw no two class cards over each other"):
            expect(_overlapping(self.cards.values())).to(be_empty)

        with it("should pass every Clean Engineering layout scanner"):
            expect(_layout_violations(self.xml)).to(be_empty)

        with context("that is read back"):
            with before.all:
                self.read = DrawIOBoundedContextMap().parse(self.xml)
                self.cart = next(item for item in self.read.every_aggregate if item.name == "Cart")
                self.written = next(item for item in self.source.every_aggregate if item.name == "Cart")

            with it("should read every context, aggregate and card it drew, and nothing from the containers"):
                def shape(model):
                    return [
                        (item.label, [(a.name, sorted(card.name for card in a.classes)) for a in item.aggregates])
                        for item in model.contexts
                    ]
                expect(shape(self.read)).to(equal(shape(self.source)))

            with it("should read each repository drawn in its root's card with the operations it keeps"):
                expect((self.cart.repository.name, [item.name for item in self.cart.repository.operations])).to(
                    equal(("CartRepository", ["create", "load", "update"]))
                )

            with it("should read the root's own operations as its own, not its repository's"):
                expect([item.name for item in self.cart.root_card.operations]).to(
                    equal([item.name for item in self.written.root_card.operations])
                )


with description("an aggregate view drawn in a folder that holds its domain model"):
    with before.all:
        from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import class_name_in
        from harness.guidance.practice_formats import Written

        folder = Path(tempfile.mkdtemp())
        (folder / "domain-model.md").write_text(_MODEL, encoding="utf-8")
        xml = DrawIOBoundedContextMap().render(MarkdownBoundedContextMap().parse(_MODEL), Written(folder=folder))
        self.links = {class_name_in(holder.get("label", "")): holder.get("link", "") for holder in ET.fromstring(xml).iter("UserObject") if holder.get("link")}

    with it("should link each class card to its class's heading in the domain model"):
        expect(self.links["CustomerProfile"]).to(equal("domain-model.md#customerprofile-aggregate-root-entity"))
