"""The facts a class's source gives the rules: a class read from code declares the measures of its code as its own
fields, and a class read from a markdown model document has no such measures at all."""

from expects import be_false, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonClass, PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.reading.card_lines import CardLines

_CART = (
    "class Cart:\n"
    "    def __init__(self) -> None:\n"
    "        self.lines = Lines()\n"
    "\n"
    "    def total(self) -> int:\n"
    "        return 1\n"
)

_ORDER_MODEL = (
    "# shop\n"
    "\n"
    "## Order\n"
    "\n"
    "- **Interaction:** Order asks Payment to charge\n"
    "\n"
    "------\n"
    "+ total: int\n"
    "----\n"
    "+ checkout(): int\n"
)


# The measures a class read from code keeps, which a class read from a markdown model document has none of.
_CODE_MEASURES = {"method_count", "operation_shapes", "property_names", "constructs", "prose_comment", "prototype_swap"}


def _loaded_code_class():
    oclass = PythonCleanEngineeringModel().parse(_CART).file_module().classes[0]
    oclass.source_facts.load()
    return oclass


def _loaded_model_class():
    oclass = MarkdownCleanEngineeringModel().parse(_ORDER_MODEL).every_class()[0]
    CardLines(_ORDER_MODEL).place(oclass)
    oclass.source_facts.load()
    return oclass


with description("a class's source facts"):
    with context("with a class read from code"):
        with it("should declare how many operations it has before its source is measured"):
            expect(PythonClass("Cart", 1).method_count).to(equal(0))

        with context("that has its source measured"):
            with before.all:
                self.cart = _loaded_code_class()

            with it("should count its operations"):
                expect(self.cart.method_count).to(equal(2))

            with it("should name the collaborators its constructor builds"):
                expect(self.cart.constructs).to(equal(["Lines"]))

            with it("should save its measures with the graph"):
                expect(_CODE_MEASURES - set(type(self.cart).graph_facts)).to(equal(set()))

    with context("with a class read from a markdown model document"):
        with before.all:
            self.order = _loaded_model_class()

        with it("should have no count of its operations"):
            expect(hasattr(self.order, "method_count")).to(be_false)

        with it("should have none of the measures of a class read from code"):
            expect(sorted(name for name in _CODE_MEASURES if hasattr(self.order, name))).to(equal([]))

        with it("should keep the line, counted in its card, of each bold Interaction bullet the card writes"):
            expect(self.order.bold_interaction_lines).to(equal([3]))
