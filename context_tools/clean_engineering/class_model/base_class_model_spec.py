"""BDD spec for CleanEngineering model nodes — OoadClass, CleanEngineeringModel, translate_from reconciliation."""

import sys
from pathlib import Path

from expects import be_true, equal, expect, have_len
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
    base_type_name_for,
    companion_interface_name,
    ensure_example_factory_family,
    example_extension_kind,
    example_factory_name_for,
    is_example_factory_name,
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


with description("example factory naming"):
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

        with it("should name CartExampleFactory from ICart"):
            expect(example_factory_name_for("ICart")).to(equal("CartExampleFactory"))

        with it("should recognize CartExampleFactory"):
            expect(is_example_factory_name("CartExampleFactory")).to(be_true)

    with context("companion_interface_name for example extensions"):
        with before.each:
            self.known = ["ICart", "FakeCart", "IsolatedCart", "ProductionCart", "CartExampleFactory"]

        with it("should resolve FakeCart to ICart"):
            expect(companion_interface_name("FakeCart", self.known)).to(equal("ICart"))

        with it("should resolve IsolatedCart to ICart"):
            expect(companion_interface_name("IsolatedCart", self.known)).to(equal("ICart"))

        with it("should resolve ProductionCart to ICart"):
            expect(companion_interface_name("ProductionCart", self.known)).to(equal("ICart"))

        with it("should not resolve ExampleFactory to an interface"):
            expect(companion_interface_name("CartExampleFactory", self.known)).to(equal(None))

    with context("ensure_example_factory_family"):
        with before.each:
            self.module = Module(name="checkout", sequential_order=1)
            self.added = ensure_example_factory_family(self.module, "ICart")

        with it("should add ICart Cart and CartExampleFactory only"):
            names = {c.name for c in self.module.classes}
            expect(names).to(
                equal(
                    {
                        "ICart",
                        "Cart",
                        "CartExampleFactory",
                    }
                )
            )

        with it("should not add Fake Isolated or Production subclasses"):
            names = {c.name for c in self.module.classes}
            expect("FakeCart" in names).to(equal(False))
            expect("IsolatedCart" in names).to(equal(False))
            expect("ProductionCart" in names).to(equal(False))

        with it("should be idempotent"):
            again = ensure_example_factory_family(self.module, "Cart")
            expect(again).to(equal([]))
            expect(self.module.classes).to(have_len(3))
