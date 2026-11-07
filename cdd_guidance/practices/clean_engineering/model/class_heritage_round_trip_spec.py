"""A class's base classes and stereotypes survive every format the class model is written in and read back from."""

from expects import be_empty, equal, expect, raise_error
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    UnreadableSource,
)
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.java.java_class_model import JavaCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.javascript.javascript_class_model import JavaScriptCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.json.json_class_model import JsonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.sketch.sketch_class_model import SketchCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel


def _shop() -> CleanEngineeringModel:
    """A cart that extends a basket and is auditable, marked as an aggregate root."""
    cart = OoadClass("Cart", 3, intent="A shopper's cart.", operations=[Operation(name="total", return_type="int")])
    cart.stereotypes = ["Aggregate Root", "Entity"]
    cart.bases = ["Basket", "Auditable"]
    shop = Module("shop", 1)
    shop.classes = [OoadClass("Basket", 1, intent="Holds items."), OoadClass("Auditable", 2, intent="Keeps a trail."), cart]
    model = CleanEngineeringModel("shop")
    model.modules.append(shop)
    return model


def _cart(model: CleanEngineeringModel) -> OoadClass:
    return next(oclass for oclass in model.every_class() if oclass.name == "Cart")


def _read_back(channel) -> OoadClass:
    return _cart(channel.parse(channel.render(_shop())))


with description("a class that extends two bases and carries stereotypes"):
    with context("written as markdown and read back"):
        with before.each:
            self.cart = _read_back(MarkdownCleanEngineeringModel())

        with it("should keep both bases in order"):
            expect(self.cart.bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("written as JSON and read back"):
        with before.each:
            self.cart = _read_back(JsonCleanEngineeringModel())

        with it("should keep both bases in order"):
            expect(self.cart.bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("written as a sketch and read back"):
        with before.each:
            self.cart = _read_back(SketchCleanEngineeringModel())

        with it("should keep both bases in order"):
            expect(self.cart.bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("drawn in draw.io and read back"):
        with before.each:
            self.cart = _read_back(DrawIOCleanEngineeringModel())

        with it("should keep both bases as inheritance arrows"):
            expect(sorted(self.cart.bases)).to(equal(["Auditable", "Basket"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("written as Python and read back"):
        with before.each:
            self.cart = _read_back(PythonCleanEngineeringModel())

        with it("should keep both bases in order"):
            expect(self.cart.bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("written as TypeScript and read back"):
        with before.each:
            self.cart = _read_back(TypeScriptCleanEngineeringModel())

        with it("should keep the base it extends and the one it implements"):
            expect(self.cart.bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("written as Java and read back"):
        with before.each:
            self.cart = _read_back(JavaCleanEngineeringModel())

        with it("should keep the base it extends and the one it implements"):
            expect(self.cart.bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("written as JavaScript and read back"):
        with before.each:
            self.cart = _read_back(JavaScriptCleanEngineeringModel())

        with it("should keep the base it extends and the one its implements line names"):
            expect(self.cart.bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its stereotypes"):
            expect(self.cart.stereotypes).to(equal(["Aggregate Root", "Entity"]))

    with context("copied into another model"):
        with it("should keep its bases in the clone"):
            expect(_cart(_shop()).clone().bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its bases when another model is brought up to date from it"):
            target = CleanEngineeringModel("shop")
            target.translate_from(_shop())
            expect(_cart(target).bases).to(equal(["Basket", "Auditable"]))

        with it("should keep its bases in its record"):
            expect(_cart(_shop()).as_record()["bases"]).to(equal(["Basket", "Auditable"]))


with description("a markdown class heading"):
    with context("that names two bases"):
        with it("should read each base on its own"):
            parsed = MarkdownCleanEngineeringModel().parse("# Shop\n\n## Cart : Basket, Auditable\n\nA cart.\n")
            expect(_cart(parsed).bases).to(equal(["Basket", "Auditable"]))

    with context("that names a base and is written again"):
        with it("should write the base back on the heading"):
            channel = MarkdownCleanEngineeringModel()
            written = channel.render(channel.parse("# Shop\n\n## Basket\n\n## Cart : Basket\n\nA cart.\n"))
            expect([line for line in written.splitlines() if line.startswith("## Cart")]).to(equal(["## Cart : Basket"]))

    with context("that marks stereotypes before its bases"):
        with it("should read the stereotypes apart from the name"):
            parsed = MarkdownCleanEngineeringModel().parse("# Shop\n\n## Cart <<Aggregate Root>> : Basket\n\nA cart.\n")
            expect((_cart(parsed).name, _cart(parsed).stereotypes)).to(equal(("Cart", ["Aggregate Root"])))


with description("a source the class model cannot read"):
    with context("Python that does not parse"):
        with it("should raise UnreadableSource rather than read a partial model"):
            expect(lambda: PythonCleanEngineeringModel().parse("class Cart(:\n    pass\n")).to(raise_error(UnreadableSource))

    with context("a draw.io file that is not XML"):
        with it("should raise UnreadableSource rather than read an empty model a sync would delete every class for"):
            expect(lambda: DrawIOCleanEngineeringModel().parse("<mxfile><diagram>")).to(raise_error(UnreadableSource))

    with context("a draw.io file that is XML"):
        with it("should read without error"):
            expect(DrawIOCleanEngineeringModel().parse("<mxfile></mxfile>").modules).to(be_empty)
