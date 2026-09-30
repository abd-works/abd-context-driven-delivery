"""BDD spec for CleanEngineering model nodes - OoadClass, CleanEngineeringModel, translate_from reconciliation."""

import sys
from pathlib import Path

from expects import be_true, equal, expect, have_len
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from practices.clean_engineering.model.property import bind_property_relationship
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
    base_type_name_for,
    companion_interface_name,
    example_extension_kind,
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

        with it("should default invariants to an empty list"):
            expect(self.prop.invariants).to(equal([]))

    with context("given ordered invariant lines"):
        with before.each:
            from practices.clean_engineering.model.property import append_invariant

            self.prop = Property(name="verified", type_hint="boolean")
            append_invariant(self.prop, "persisted KYC on the party")
            append_invariant(self.prop, "flips true on confirmIdentity when PersonaInquiry.verified")

        with it("should keep each line in order"):
            expect([item.sequential_order for item in self.prop.invariants]).to(equal([1, 2]))
            expect([item.text for item in self.prop.invariants]).to(equal([
                "persisted KYC on the party",
                "flips true on confirmIdentity when PersonaInquiry.verified",
            ]))


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
            expect([parameter.save() for parameter in self.op.parameters]).to(equal(["rate: float"]))

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


def _order_property() -> Property:
    prop = Property(name="order", type_hint="Order")
    prop.stereotype = "association"
    prop.cardinality = "0..1"
    bind_property_relationship(prop)
    return prop


with description("a property type"):
    with it("should relate a domain class and keep the cardinality on that relationship"):
        customers = Property(name="customers", type_hint="Collection<Customer>")
        customers.stereotype = "aggregation"
        customers.cardinality = "0..*"
        bind_property_relationship(customers)
        expect(customers.relationship.target).to(equal("Customer"))
        expect(customers.relationship.kind).to(equal("aggregation"))
        expect(customers.relationship.cardinality).to(equal("0..*"))

    with it("should leave a primitive and a third-party type without a relationship"):
        identifier = Property(name="id", type_hint="string")
        cause = Property(name="cause", type_hint="Error")
        bind_property_relationship(identifier)
        bind_property_relationship(cause)
        expect(identifier.relationship).to(equal(None))
        expect(cause.relationship).to(equal(None))


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
                properties=[_order_property()],
                operations=[Operation(name="place_order", return_type="Order")],
                collaborators=["Order", "LineItem"],
            )

        with it("should store intent"):
            expect(self.cls.intent).to(equal("Holds line items and places orders on behalf of the owner."))

        with it("should store properties"):
            expect(self.cls.properties).to(have_len(1))
            expect(self.cls.properties[0].name).to(equal("order"))

        with it("should store operations"):
            expect(self.cls.operations).to(have_len(1))
            expect(self.cls.operations[0].name).to(equal("place_order"))

        with it("should store the relationship on the property"):
            expect(self.cls.relationships).to(have_len(1))
            expect(self.cls.relationships[0].target).to(equal("Order"))
            expect(self.cls.relationships[0].cardinality).to(equal("0..1"))
            expect(self.cls.properties[0].relationship.cardinality).to(equal("0..1"))

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


with description("Module"):
    with context("constructed with modules-fidelity fields"):
        with before.each:
            self.module = Module(
                name="character",
                sequential_order=1,
                description="Sheet ownership.",
                seam_terms=["Character", "ISource"],
                dependencies=["checks"],
            )

        with it("should store name"):
            expect(self.module.name).to(equal("character"))

        with it("should store description"):
            expect(self.module.description).to(equal("Sheet ownership."))

        with it("should store seam_terms"):
            expect(self.module.seam_terms).to(equal(["Character", "ISource"]))

        with it("should store dependencies"):
            expect(self.module.dependencies).to(equal(["checks"]))

        with it("should default classes to empty list"):
            expect(self.module.classes).to(equal([]))

    with context("public_terms"):
        with it("should prefer explicit seam_terms"):
            module = Module(
                name="checks",
                sequential_order=1,
                seam_terms=["Trait", "Check"],
            )
            module.classes.append(OoadClass(name="Ignored", sequential_order=1))
            expect(module.public_terms()).to(equal(["Trait", "Check"]))

        with it("should fall back to thin class names"):
            module = Module(name="checks", sequential_order=1)
            module.classes.append(OoadClass(name="Trait", sequential_order=1))
            module.classes.append(OoadClass(name="Check", sequential_order=2))
            expect(module.public_terms()).to(equal(["Trait", "Check"]))

        with it("should fall back to comma-separated seam string"):
            module = Module(
                name="checks",
                sequential_order=1,
                seam="Trait, Check, CheckResult",
            )
            expect(module.public_terms()).to(equal(["Trait", "Check", "CheckResult"]))

    with context("update_self copies modules-fidelity fields"):
        with before.each:
            self.module = Module(name="character", sequential_order=1)
            source = Module(
                name="character",
                sequential_order=1,
                description="Updated purpose.",
                seam="Character",
                seam_terms=["Character", "ISource"],
                dependencies=["checks"],
                constraint="Callers use ISource only.",
            )
            self.module.update_self(source)

        with it("should copy description"):
            expect(self.module.description).to(equal("Updated purpose."))

        with it("should copy seam_terms"):
            expect(self.module.seam_terms).to(equal(["Character", "ISource"]))

        with it("should copy dependencies"):
            expect(self.module.dependencies).to(equal(["checks"]))

        with it("should copy constraint"):
            expect(self.module.constraint).to(equal("Callers use ISource only."))


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


with description("interface naming"):
    with context("Fake / Isolated / Production prefixes"):
        with it("should detect FakeCart as Fake"):
            expect(example_extension_kind("FakeCart")).to(equal("Fake"))

        with it("should detect IsolatedCart as Isolated"):
            expect(example_extension_kind("IsolatedCart")).to(equal("Isolated"))

        with it("should detect ProductionCart as Production"):
            expect(example_extension_kind("ProductionCart")).to(equal("Production"))

        with it("should not treat Cart as an extension"):
            expect(example_extension_kind("Cart")).to(equal(None))

        with it("should strip FakeCart to Cart"):
            expect(base_type_name_for("FakeCart")).to(equal("Cart"))

    with context("companion_interface_name for example extensions"):
        with before.each:
            self.known = ["ICart", "FakeCart", "IsolatedCart", "ProductionCart"]

        with it("should resolve FakeCart to ICart"):
            expect(companion_interface_name("FakeCart", self.known)).to(equal("ICart"))

        with it("should resolve IsolatedCart to ICart"):
            expect(companion_interface_name("IsolatedCart", self.known)).to(equal("ICart"))

        with it("should resolve ProductionCart to ICart"):
            expect(companion_interface_name("ProductionCart", self.known)).to(equal("ICart"))
