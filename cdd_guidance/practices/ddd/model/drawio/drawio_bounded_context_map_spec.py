"""DrawIOBoundedContextMap — the bounded-context map and the aggregate view drawn by Clean Engineering's draw.io
diagram: contexts and aggregates as nested modules, building blocks as classes with their stereotypes."""

import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from expects import be_empty, be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner
from cdd_guidance.practices.ddd.model.drawio.drawio_bounded_context_map import DrawIOAggregateCell, DrawIOBoundedContextMap
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

_EXAMPLES = Path(__file__).resolve().parent.parent / "_examples" / "expected"
_MAP = (_EXAMPLES / "bounded-context-map.md").read_text(encoding="utf-8")
_MODEL = (_EXAMPLES / "domain-model.md").read_text(encoding="utf-8")


def _cells(xml):
    return {cell.get("id"): cell for cell in ET.fromstring(xml).iter("mxCell")}


def _arrows(xml):
    return [cell for cell in ET.fromstring(xml).iter("mxCell") if cell.get("edge") == "1"]


def _layout_violations(xml):
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "model.drawio"
        path.write_text(xml, encoding="utf-8")
        return [
            violation.message
            for slug, scanner_type in DrawioScanner.discover().items()
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

        with it("should draw the repository as a class of its own"):
            expect("customer-custom-customer-profile--customerprofilerepository" in self.cells).to(be_true)

        with it("should keep each class in the module of its context and aggregate"):
            style = self.cells["customer-custom-kyc--kycinquiry"].get("style")
            expect("module=Customer | custom · KYC;" in style).to(be_true)

        with it("should compose the members under the root"):
            arrow = self.ends[("customer-custom-customer-profile--customerprofile", "customer-custom-customer-profile--identity")]
            expect("startArrow=diamondThin;startFill=1" in arrow.get("style")).to(be_true)

        with it("should draw a dependency where an operation calls into another aggregate"):
            arrow = self.ends[("customer-custom-customer-profile--customerprofile", "customer-custom-kyc--kycinquiryrepository")]
            expect(arrow.get("value")).to(equal("«sendSupportRequest»"))

        with it("should draw a dependency from the root along each integration, named by its pattern"):
            arrow = self.ends[("service-custom-subscription--subscription", "customer-custom-customer-profile--customerprofile")]
            expect(arrow.get("value")).to(equal("«Customer/Supplier»"))

        with it("should draw no arrow out of an aggregate that needs no other"):
            leaving = [ends for ends in self.ends if ends[0] == "customer-custom-kyc--kycinquiry"]
            expect(leaving).to(be_empty)

        with it("should pass every Clean Engineering layout scanner"):
            expect(_layout_violations(self.xml)).to(be_empty)
