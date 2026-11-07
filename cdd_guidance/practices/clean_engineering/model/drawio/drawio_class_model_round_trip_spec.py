"""A class model drawn as a Draw.io class diagram and read back from it."""
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
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


def _class(model, name):
    return next(oclass for module in model.modules for oclass in module.classes if oclass.name == name)


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
            self.loaded = DrawIOCleanEngineeringModel().load(str(self.path))

        with it("should read the classes the file shows"):
            expect([oclass.name for oclass in self.loaded.modules[0].classes]).to(equal(["Order", "OrderLine"]))
