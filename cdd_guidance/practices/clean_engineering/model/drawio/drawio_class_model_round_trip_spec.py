"""A class model drawn as a Draw.io class diagram and read back from it."""
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from expects import equal, expect, have_len
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property


def _shop() -> CleanEngineeringModel:
    lines = Property(name="lines", type_hint="List[OrderLine]")
    lines.stereotype = "composition"
    lines.derive_relationship()
    order = OoadClass(
        name="Order",
        sequential_order=1,
        properties=[Property(name="number", type_hint="str"), lines],
        operations=[Operation(name="add_line", parameters=["product: str", "quantity: int"], return_type="OrderLine")],
    )
    line = OoadClass(name="OrderLine", sequential_order=2, properties=[Property(name="quantity", type_hint="int")])
    model = CleanEngineeringModel(name="Shop", sequential_order=1)
    module = Module(name="sales", sequential_order=1)
    module.classes = [order, line]
    model.modules = [module]
    return model


def _payments() -> CleanEngineeringModel:
    """One payment base with three kinds of payment that derive from it."""
    payment = OoadClass(name="Payment", sequential_order=1, properties=[Property(name="amount", type_hint="int")])
    kinds = [OoadClass(name=name, sequential_order=order) for order, name in enumerate(("CardPayment", "CashPayment", "VoucherPayment"), 2)]
    for kind in kinds:
        kind.bases = ["Payment"]
    module = Module(name="billing", sequential_order=1)
    module.classes = [payment] + kinds
    model = CleanEngineeringModel(name="Billing", sequential_order=1)
    model.modules = [module]
    return model


def _class(model, name):
    return next(oclass for module in model.modules for oclass in module.classes if oclass.name == name)


def _inheritance_edges(rendered: str):
    return [cell for cell in ET.fromstring(rendered).iter("mxCell") if cell.get("edge") == "1" and "endArrow=block" in cell.get("style", "")]


def _entry_anchor(edge) -> str:
    return re.search(r"entryX=[^;]+;entryY=[^;]+", edge.get("style")).group(0)


with description("a class model drawn as a Draw.io class diagram"):
    with context("that is read back"):
        with before.each:
            channel = DrawIOCleanEngineeringModel()
            self.parsed = channel.parse(channel.render(_shop()))

        with it("should keep the module name"):
            expect([module.name for module in self.parsed.modules]).to(equal(["sales"]))

        with it("should keep both classes in their order"):
            expect([oclass.name for oclass in self.parsed.modules[0].classes]).to(equal(["Order", "OrderLine"]))

        with it("should keep each typed property"):
            order = _class(self.parsed, "Order")
            expect([(prop.name, prop.type_hint) for prop in order.properties]).to(
                equal([("number", "str"), ("lines", "List[OrderLine]")])
            )

        with it("should keep the operation with its parameters and return type"):
            add_line = _class(self.parsed, "Order").operations[0]
            expect((add_line.name, [parameter.save() for parameter in add_line.parameters], add_line.return_type)).to(
                equal(("add_line", ["product: str", "quantity: int"], "OrderLine"))
            )

        with it("should keep the composition on the property that holds the lines"):
            relationship = _class(self.parsed, "Order").properties[1].relationship
            expect((relationship.target, relationship.kind)).to(equal(("OrderLine", "composition")))

        with it("should keep the part's own property"):
            expect([prop.name for prop in _class(self.parsed, "OrderLine").properties]).to(equal(["quantity"]))

    with context("that is loaded from a file"):
        with before.each:
            self.path = Path(tempfile.mkdtemp()) / "shop.drawio"
            self.path.write_text(DrawIOCleanEngineeringModel().render(_shop()), encoding="utf-8")
            self.loaded = DrawIOCleanEngineeringModel().parse(self.path.read_text(encoding="utf-8"))

        with it("should read the classes the file shows"):
            expect([oclass.name for oclass in self.loaded.modules[0].classes]).to(equal(["Order", "OrderLine"]))


with description("a class model where several classes derive from one base"):
    with context("that is drawn"):
        with before.each:
            self.rendered = DrawIOCleanEngineeringModel().render(_payments())
            self.path = Path(tempfile.mkdtemp()) / "billing.drawio"
            self.path.write_text(self.rendered, encoding="utf-8")

        with it("should draw one inheritance arrow for each derived class"):
            expect(sorted(edge.get("source") for edge in _inheritance_edges(self.rendered))).to(
                equal(["billing--cardpayment", "billing--cashpayment", "billing--voucherpayment"])
            )

        with it("should end every inheritance arrow at one point on the base"):
            expect({_entry_anchor(edge) for edge in _inheritance_edges(self.rendered)}).to(have_len(1))

        with it("should pass the overlap and anchor layout rules with the shared line"):
            report = DrawioScanner(scan_root=self.path.parent).run_report([str(self.path)])
            rules = [item["rule"] for item in report["violations"]]
            expect([rule for rule in rules if rule in ("edges-do-not-overlap-edges", "distinct-anchor-points")]).to(equal([]))

    with context("that is read back"):
        with before.each:
            channel = DrawIOCleanEngineeringModel()
            self.parsed = channel.parse(channel.render(_payments()))

        with it("should give each derived class its base exactly"):
            expect({name: _class(self.parsed, name).bases for name in ("CardPayment", "CashPayment", "VoucherPayment")}).to(
                equal({"CardPayment": ["Payment"], "CashPayment": ["Payment"], "VoucherPayment": ["Payment"]})
            )

        with it("should give the base no base of its own"):
            expect(_class(self.parsed, "Payment").bases).to(equal([]))
