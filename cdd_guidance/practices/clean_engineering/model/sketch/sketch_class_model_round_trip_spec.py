"""A class model written as the clean engineering section of a sketch and read back from it."""
from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property, append_invariant
from cdd_guidance.practices.clean_engineering.model.sketch.sketch_class_model import SketchCleanEngineeringModel


def _shop() -> CleanEngineeringModel:
    lines = Property(name="lines")
    lines.cardinality = "1..*"
    append_invariant(lines, "never empty after checkout")
    add_line = Operation(name="addLine", parameters=["product", "quantity"], callees=["lines.append"])
    append_invariant(add_line, "before checkout")
    order = OoadClass(
        name="Order",
        sequential_order=1,
        properties=[lines],
        operations=[add_line, Operation(name="total", return_type="Money"), Operation(name="checkout")],
    )
    order.bases = ["Entity"]
    order.stereotypes = ["Aggregate Root"]
    line = OoadClass(name="OrderLine", sequential_order=2, properties=[Property(name="quantity")])
    invoice = OoadClass(name="Invoice", sequential_order=1, operations=[Operation(name="issue", parameters=["order"])])
    sales = Module(name="sales", sequential_order=1)
    sales.classes = [order, line]
    billing = Module(name="billing", sequential_order=2)
    billing.classes = [invoice]
    model = CleanEngineeringModel(name="shop", sequential_order=1)
    model.modules = [sales, billing]
    return model


def _class(model, name):
    return next(oclass for oclass in model.every_class() if oclass.name == name)


def _operation(model, class_name, name):
    return next(operation for operation in _class(model, class_name).operations if operation.name == name)


with description("a class model written as a sketch"):
    with context("that is read back"):
        with before.each:
            self.parsed = SketchCleanEngineeringModel().parse(SketchCleanEngineeringModel().render(_shop()))

        with it("should keep the model name"):
            expect(self.parsed.name).to(equal("shop"))

        with it("should keep each module in order"):
            expect([module.name for module in self.parsed.modules]).to(equal(["sales", "billing"]))

        with it("should keep each module's classes"):
            expect([[oclass.name for oclass in module.classes] for module in self.parsed.modules]).to(
                equal([["Order", "OrderLine"], ["Invoice"]])
            )

        with it("should keep the base a class extends"):
            expect(_class(self.parsed, "Order").bases).to(equal(["Entity"]))

        with it("should keep the stereotypes a class carries"):
            expect(_class(self.parsed, "Order").stereotypes).to(equal(["Aggregate Root"]))

        with it("should keep properties as properties"):
            expect([prop.name for prop in _class(self.parsed, "Order").properties]).to(equal(["lines"]))

        with it("should keep the property's cardinality and invariant"):
            lines = _class(self.parsed, "Order").properties[0]
            expect((lines.cardinality, [item.text for item in lines.invariants])).to(
                equal(("1..*", ["never empty after checkout"]))
            )

        with it("should keep operations as operations, even one with nothing after its name"):
            expect([operation.name for operation in _class(self.parsed, "Order").operations]).to(
                equal(["addLine", "total", "checkout"])
            )

        with it("should keep the operation's parameters"):
            add_line = _operation(self.parsed, "Order", "addLine")
            expect([parameter.name for parameter in add_line.parameters]).to(equal(["product", "quantity"]))

        with it("should keep the operation's return type"):
            expect(_operation(self.parsed, "Order", "total").return_type).to(equal("Money"))

        with it("should keep the operation's interactions"):
            expect(_operation(self.parsed, "Order", "addLine").callees).to(equal(["lines.append"]))

        with it("should keep the operation's invariants"):
            add_line = _operation(self.parsed, "Order", "addLine")
            expect([item.text for item in add_line.invariants]).to(equal(["before checkout"]))

        with it("should keep a class in a later module with its operation"):
            expect([parameter.name for parameter in _operation(self.parsed, "Invoice", "issue").parameters]).to(
                equal(["order"])
            )

    with context("that replaces the section of an existing sketch"):
        with before.each:
            previous = (
                "# shop sketch\n\n## stories:\n\nbuy things\n\n"
                "## clean engineering:\n\n### old/\n\n##### Stale\n\n```\ngone\n```\n\n"
                "## behavior driven development:\n\nan order\n"
            )
            self.written = SketchCleanEngineeringModel().render(_shop(), previous)

        with it("should keep the other practices' sections"):
            expect(self.written).to(contain("## stories:\n\nbuy things"))
            expect(self.written).to(contain("## behavior driven development:\n\nan order"))

        with it("should replace the old clean engineering section"):
            expect("Stale" in self.written).to(equal(False))
            expect([oclass.name for oclass in SketchCleanEngineeringModel().parse(self.written).every_class()]).to(
                equal(["Order", "OrderLine", "Invoice"])
            )
