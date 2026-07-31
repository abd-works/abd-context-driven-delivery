"""BDD spec - a module with an example factory renders IType + Type + ExampleFactory (no Fake subclasses)."""

import sys
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    ensure_example_factory_family,
)
from context_tools.clean_engineering.class_model.javascript_class_model import (
    JavaScriptCleanEngineeringModel,
)
from context_tools.clean_engineering.class_model.markdown_class_model import (
    MarkdownCleanEngineeringModel,
)
from context_tools.clean_engineering.class_model.python_class_model import (
    PythonCleanEngineeringModel,
)


def _family_model() -> CleanEngineeringModel:
    model = CleanEngineeringModel(name="", sequential_order=1)
    module = Module(name="checkout", sequential_order=1)
    ensure_example_factory_family(module, "Cart")
    model.modules.append(module)
    return model


with description("a module that holds a Cart example-factory family") as self:
    with context("that has been rendered as Python"):
        with before.each:
            self.text = PythonCleanEngineeringModel.render(_family_model())

        with it("should declare ICart"):
            expect(self.text).to(contain("class ICart"))

        with it("should declare production Cart"):
            expect(self.text).to(contain("class Cart"))

        with it("should declare CartExampleFactory"):
            expect(self.text).to(contain("class CartExampleFactory"))

        with it("should not declare FakeCart IsolatedCart or ProductionCart classes"):
            expect("class FakeCart" in self.text).to(equal(False))
            expect("class IsolatedCart" in self.text).to(equal(False))
            expect("class ProductionCart" in self.text).to(equal(False))

    with context("that has been rendered as JavaScript"):
        with before.each:
            self.text = JavaScriptCleanEngineeringModel.render(_family_model())

        with it("should declare ICart"):
            expect(self.text).to(contain("class ICart"))

        with it("should declare production Cart"):
            expect(self.text).to(contain("class Cart"))

        with it("should declare CartExampleFactory as an example factory"):
            expect(self.text).to(contain("class CartExampleFactory"))
            expect(self.text).to(contain("example factory"))

        with it("should not declare FakeCart IsolatedCart or ProductionCart classes"):
            expect("class FakeCart" in self.text).to(equal(False))
            expect("class IsolatedCart" in self.text).to(equal(False))
            expect("class ProductionCart" in self.text).to(equal(False))

    with context("that has been rendered as Markdown"):
        with before.each:
            self.text = MarkdownCleanEngineeringModel.render(_family_model())

        with it("should heading ICart"):
            expect(self.text).to(contain("ICart"))

        with it("should heading CartExampleFactory"):
            expect(self.text).to(contain("## CartExampleFactory") or contain("CartExampleFactory"))

        with it("should not heading FakeCart as a type"):
            expect("## FakeCart" in self.text).to(equal(False))

    with context("that has been round-tripped through Markdown into Python"):
        with before.each:
            md = MarkdownCleanEngineeringModel.render(_family_model())
            parsed = MarkdownCleanEngineeringModel.parse(md)
            self.py = PythonCleanEngineeringModel.render(parsed)

        with it("should still declare CartExampleFactory"):
            expect(self.py).to(contain("CartExampleFactory"))
