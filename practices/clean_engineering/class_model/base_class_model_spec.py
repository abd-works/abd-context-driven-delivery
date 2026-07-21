"""BDD spec for CleanEngineering model nodes — OoadClass, CleanEngineeringModel, translate_from reconciliation."""

import sys
from pathlib import Path

from expects import be_true, equal, expect, have_len
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)


with description("Property"):
    with context("constructed with name and type"):
        with before.each:
            self.prop = Property(name="remaining_budget", type_hint="float")

        with it("should store name"):
            expect(self.prop.name).to(equal("remaining_budget"))

        with it("should store type_hint"):
            expect(self.prop.type_hint).to(equal("float"))

        with it("should default description to empty string"):
            expect(self.prop.description).to(equal(""))


with description("Operation"):
    with context("constructed with name only"):
        with before.each:
            self.op = Operation(name="calculate_total")

        with it("should store name"):
            expect(self.op.name).to(equal("calculate_total"))

        with it("should default parameters to empty list"):
            expect(self.op.parameters).to(equal([]))

        with it("should default return_type to empty string"):
            expect(self.op.return_type).to(equal(""))

    with context("constructed with parameters and return type"):
        with before.each:
            self.op = Operation(
                name="apply_discount",
                parameters=["rate: float"],
                return_type="float",
            )

        with it("should store parameters"):
            expect(self.op.parameters).to(equal(["rate: float"]))

        with it("should store return_type"):
            expect(self.op.return_type).to(equal("float"))


with description("Relationship"):
    with context("constructed with target and kind"):
        with before.each:
            self.rel = Relationship(target="Order", kind="owns")

        with it("should store target"):
            expect(self.rel.target).to(equal("Order"))

        with it("should store kind"):
            expect(self.rel.kind).to(equal("owns"))

        with it("should default cardinality to empty string"):
            expect(self.rel.cardinality).to(equal(""))


with description("OoadClass"):
    with context("constructed with name only"):
        with before.each:
            self.cls = OoadClass(name="Cart", sequential_order=1)

        with it("should store name"):
            expect(self.cls.name).to(equal("Cart"))

        with it("should default intent to empty string"):
            expect(self.cls.intent).to(equal(""))

        with it("should default properties to empty list"):
            expect(self.cls.properties).to(equal([]))

        with it("should default operations to empty list"):
            expect(self.cls.operations).to(equal([]))

        with it("should default relationships to empty list"):
            expect(self.cls.relationships).to(equal([]))

        with it("should default collaborators to empty list"):
            expect(self.cls.collaborators).to(equal([]))

    with context("constructed with full attributes"):
        with before.each:
            self.cls = OoadClass(
                name="Cart",
                sequential_order=1,
                intent="Holds line items and places orders on behalf of the owner.",
                properties=[Property(name="owner", type_hint="str")],
                operations=[Operation(name="place_order", return_type="Order")],
                relationships=[Relationship(target="Order", kind="owns")],
                collaborators=["Order", "LineItem"],
            )

        with it("should store intent"):
            expect(self.cls.intent).to(equal("Holds line items and places orders on behalf of the owner."))

        with it("should store properties"):
            expect(self.cls.properties).to(have_len(1))
            expect(self.cls.properties[0].name).to(equal("owner"))

        with it("should store operations"):
            expect(self.cls.operations).to(have_len(1))
            expect(self.cls.operations[0].name).to(equal("place_order"))

        with it("should store relationships"):
            expect(self.cls.relationships).to(have_len(1))
            expect(self.cls.relationships[0].target).to(equal("Order"))

        with it("should store collaborators"):
            expect(self.cls.collaborators).to(equal(["Order", "LineItem"]))

    with context("update_self called from a source OoadClass"):
        with before.each:
            self.cls = OoadClass(name="Cart", sequential_order=1)
            source = OoadClass(
                name="Cart",
                sequential_order=1,
                intent="Updated intent.",
                properties=[Property(name="items", type_hint="list")],
            )
            self.cls.update_self(source)

        with it("should copy intent from source"):
            expect(self.cls.intent).to(equal("Updated intent."))

        with it("should copy properties from source"):
            expect(self.cls.properties).to(have_len(1))


with description("CleanEngineeringModel"):
    with context("constructed with name only"):
        with before.each:
            self.model = CleanEngineeringModel(name="checkout", sequential_order=1)

        with it("should store name"):
            expect(self.model.name).to(equal("checkout"))

        with it("should default classes to empty list"):
            expect(self.model.classes).to(equal([]))

    with context("translate_from with a source that has one new class"):
        with before.each:
            self.model = CleanEngineeringModel(name="checkout", sequential_order=1)
            source = CleanEngineeringModel(name="checkout", sequential_order=1)
            module = Module(name="checkout", sequential_order=1)
            module.classes.append(OoadClass(name="Cart", sequential_order=1))
            source.modules.append(module)
            self.report = self.model.translate_from(source)

        with it("should add the new class to model.classes"):
            expect(self.model.classes).to(have_len(1))
            expect(self.model.classes[0].name).to(equal("Cart"))

        with it("should record an ADD in the report"):
            expect(len(self.report.adds())).to(equal(1))

    with context("translate_from with a class removed from source"):
        with before.each:
            self.model = CleanEngineeringModel(name="checkout", sequential_order=1)
            module = Module(name="checkout", sequential_order=1)
            module.classes.append(OoadClass(name="Cart", sequential_order=1))
            self.model.modules.append(module)
            source = CleanEngineeringModel(name="checkout", sequential_order=1)
            self.report = self.model.translate_from(source)

        with it("should remove the class from model.classes"):
            expect(self.model.classes).to(equal([]))

        with it("should record a REMOVE in the report"):
            expect(len(self.report.removes())).to(equal(1))

    with context("translate_from matching an existing class by name"):
        with before.each:
            self.model = CleanEngineeringModel(name="checkout", sequential_order=1)
            module = Module(name="checkout", sequential_order=1)
            module.classes.append(OoadClass(name="Cart", sequential_order=1, intent="old intent"))
            self.model.modules.append(module)
            source = CleanEngineeringModel(name="checkout", sequential_order=1)
            source_module = Module(name="checkout", sequential_order=1)
            source_module.classes.append(
                OoadClass(name="Cart", sequential_order=1, intent="new intent")
            )
            source.modules.append(source_module)
            self.model.translate_from(source)

        with it("should update the existing class in place"):
            expect(self.model.classes[0].intent).to(equal("new intent"))
