"""A class's stereotypes are data on the class model: each code channel writes them and reads them back."""

import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass  # noqa: E402
from cdd_guidance.practices.clean_engineering.model.javascript.javascript_class_model import (  # noqa: E402
    JavaScriptCleanEngineeringModel,
)
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel  # noqa: E402
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel  # noqa: E402
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import (  # noqa: E402
    TypeScriptCleanEngineeringModel,
)


def _cart_model() -> CleanEngineeringModel:
    """A model with one class, Cart, an Aggregate Root and Entity that holds a shopper's lines."""
    cart = OoadClass("Cart", 1, intent="A shopper's cart.")
    cart.stereotypes = ["Aggregate Root", "Entity"]
    module = Module("cart", 1)
    module.classes.append(cart)
    model = CleanEngineeringModel("model", 1)
    model.modules.append(module)
    return model


def _round_trip(channel):
    """The Cart class after the channel writes the model and reads its own code back."""
    parsed = channel.parse(channel.render(_cart_model()))
    return next(oclass for oclass in parsed.every_class() if oclass.name == "Cart")


def _read(channel, code: str) -> OoadClass:
    return channel.parse(code).every_class()[0]


with description("a class that carries stereotypes"):
    with context("written as python"):
        with it("should write each stereotype as a decorator with no arguments"):
            expect(PythonCleanEngineeringModel().render(_cart_model())).to(contain("@aggregate_root\n@entity\nclass Cart:"))

        with it("should read the same stereotypes back"):
            expect(_round_trip(PythonCleanEngineeringModel()).stereotypes).to(equal(["Aggregate Root", "Entity"]))

        with it("should keep the intent without the stereotypes"):
            expect(_round_trip(PythonCleanEngineeringModel()).intent).to(equal("A shopper's cart."))

    with context("written as typescript"):
        with it("should write each stereotype as a decorator call"):
            expect(TypeScriptCleanEngineeringModel().render(_cart_model())).to(contain("@AggregateRoot()\n@Entity()\nclass Cart {"))

        with it("should read the same stereotypes back"):
            expect(_round_trip(TypeScriptCleanEngineeringModel()).stereotypes).to(equal(["Aggregate Root", "Entity"]))

        with it("should keep the intent from the doc comment"):
            expect(_round_trip(TypeScriptCleanEngineeringModel()).intent).to(equal("A shopper's cart."))

    with context("written as javascript, which has no decorators"):
        with it("should mark the stereotypes in the doc comment"):
            expect(JavaScriptCleanEngineeringModel().render(_cart_model())).to(contain("/** <<Aggregate Root>> <<Entity>> A shopper's cart. */"))

        with it("should read the same stereotypes back"):
            expect(_round_trip(JavaScriptCleanEngineeringModel()).stereotypes).to(equal(["Aggregate Root", "Entity"]))


with description("hand-written code that marks a class's stereotype"):
    with context("in a typescript doc comment"):
        with it("should read the mark as the stereotype and the rest as the intent"):
            oclass = _read(TypeScriptCleanEngineeringModel(), "/** <<Value Object>> Card authorization fields. */\nexport class CardAuthorization {\n  amount: number;\n}\n")
            expect((oclass.stereotypes, oclass.intent)).to(equal((["Value Object"], "Card authorization fields.")))

    with context("in a python comment line above the class"):
        with it("should read the mark as the stereotype"):
            oclass = _read(PythonCleanEngineeringModel(), "import os\n\n# <<Entity>>\nclass Account:\n    id: str\n")
            expect(oclass.stereotypes).to(equal(["Entity"]))

    with context("with a decorator that takes arguments"):
        with it("should not read it as a stereotype"):
            oclass = _read(PythonCleanEngineeringModel(), "@dataclass(frozen=True)\n@value_object\nclass Money:\n    amount: int\n")
            expect(oclass.stereotypes).to(equal(["Value Object"]))


def _kept_cart(channel) -> OoadClass:
    """Cart, kept in the Sales context's ShoppingCart module, depending on Product with the facts of that dependency
    and on Clock with none, written by channel and read back."""
    model = _cart_model()
    cart = model.modules[0].classes[0]
    cart.module_path = ["Sales | custom", "ShoppingCart"]
    cart.depend_on("Product", "Customer/Supplier")
    cart.dependencies[0].details = {"direction": "downstream", "crosses": "product identity"}
    cart.depend_on("Clock", "reads time from")
    return _read(channel, channel.render(model))


with description("a class whose doc comment names its module path and a dependency with details"):
    with context("written as python and read back"):
        with it("should keep the module path"):
            expect(_kept_cart(PythonCleanEngineeringModel()).module_path).to(equal(["Sales | custom", "ShoppingCart"]))

        with it("should keep the dependency's label and details"):
            dependency = _kept_cart(PythonCleanEngineeringModel()).dependencies[0]
            expect((dependency.target, dependency.label, dependency.details)).to(
                equal(("Product", "Customer/Supplier", {"direction": "downstream", "crosses": "product identity"}))
            )

        with it("should leave a dependency with no details to the code that makes it"):
            expect([item.target for item in _kept_cart(PythonCleanEngineeringModel()).dependencies]).to(equal(["Product"]))

        with it("should keep the intent apart from the module path and the dependency"):
            expect(_kept_cart(PythonCleanEngineeringModel()).intent).to(equal("A shopper's cart."))

    with context("written as typescript and read back"):
        with it("should keep the module path"):
            expect(_kept_cart(TypeScriptCleanEngineeringModel()).module_path).to(equal(["Sales | custom", "ShoppingCart"]))

        with it("should keep the dependency's details"):
            expect(_kept_cart(TypeScriptCleanEngineeringModel()).dependencies[0].details["crosses"]).to(equal("product identity"))

        with it("should keep the stereotypes and intent"):
            oclass = _kept_cart(TypeScriptCleanEngineeringModel())
            expect((oclass.stereotypes, oclass.intent)).to(equal((["Aggregate Root", "Entity"], "A shopper's cart.")))

    with context("written as markdown and read back"):
        with it("should keep the dependency's label and details"):
            dependency = _kept_cart(MarkdownCleanEngineeringModel()).dependencies[0]
            expect((dependency.target, dependency.label, dependency.details)).to(
                equal(("Product", "Customer/Supplier", {"direction": "downstream", "crosses": "product identity"}))
            )

        with it("should keep a dependency with no details as it was"):
            expect([item.details for item in _kept_cart(MarkdownCleanEngineeringModel()).dependencies]).to(
                equal([{"direction": "downstream", "crosses": "product identity"}, {}])
            )


with description("a class's doc comment"):
    with context("written from a class with a module path, stereotypes, and a detailed dependency, and read into another"):
        with before.all:
            from cdd_guidance.practices.clean_engineering.model.field_types import Relationship

            written = OoadClass("Cart", 1)
            written.intent = "Holds a shopper's lines."
            written.stereotypes = ["Aggregate Root"]
            written.module_path = ["Sales | custom", "Cart"]
            written.dependencies = [Relationship(target="Product", kind="dependency", label="Customer/Supplier", details={"direction": "downstream"})]
            self.comment = written.doc_comment(marked=True)
            self.read = OoadClass("Cart", 1)
            self.comment.describe(self.read)

        with it("should mark the class's stereotypes"):
            expect(self.comment.stereotypes).to(equal(["Aggregate Root"]))

        with it("should give the class read its intent, module path, and dependency"):
            dependency = self.read.dependencies[0]
            expect((self.read.intent, self.read.module_path, dependency.target, dependency.details)).to(
                equal(("Holds a shopper's lines.", ["Sales | custom", "Cart"], "Product", {"direction": "downstream"}))
            )
