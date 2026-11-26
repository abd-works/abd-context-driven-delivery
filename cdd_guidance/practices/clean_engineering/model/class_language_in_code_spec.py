"""Mamba spec for a class's language in code: the story and the responsibility bullets a model card writes under the
class's heading are the class's doc comment, paragraph breaks and all, and read back as the class's language."""

from expects import contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.javascript.javascript_class_model import JavaScriptCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel

STORY = "The *Cart* is the customer's order while they are still building it."
CLOSING = "When the order is placed, the Cart closes."
LINES = "- **Lines.** The Cart adds a Line for each plan the customer picks."
PRICE = "- **Price.** The Cart calculates the monthly charge from its Lines' plan prices."
LANGUAGE = f"{STORY}\n\n{CLOSING}\n\n{LINES}\n{PRICE}"

CARD = f"""# cart

## Cart

{LANGUAGE}

+ Cart(id: string)
------
+ id: string
----
+ addLine(plan: Plan): Line
"""


def _model() -> MarkdownCleanEngineeringModel:
    model = MarkdownCleanEngineeringModel()
    model.parse(CARD)
    return model


with description("a class's language written into code") as self:
    with context("written as a Python class"):
        with before.all:
            self.code = PythonCleanEngineeringModel().render(_model())

        with it("should be the class's docstring, each line after the first set in under the class"):
            expect(self.code).to(contain(f'    """{STORY}\n\n    {CLOSING}\n\n    {LINES}\n    {PRICE}"""'))

        with it("should read back as the class's language"):
            expect(PythonCleanEngineeringModel().parse(self.code).modules[0].classes[0].intent).to(equal(LANGUAGE))

    with context("written as a TypeScript class"):
        with before.all:
            self.code = TypeScriptCleanEngineeringModel().render(_model())

        with it("should be the class's doc comment, a bare star between its paragraphs"):
            expect(self.code).to(contain(f"/**\n * {STORY}\n *\n * {CLOSING}\n *\n * {LINES}\n * {PRICE}\n */\nclass Cart"))

        with it("should read back as the class's language"):
            expect(TypeScriptCleanEngineeringModel().parse(self.code).modules[0].classes[0].intent).to(equal(LANGUAGE))

    with context("written as a JavaScript class"):
        with before.all:
            self.code = JavaScriptCleanEngineeringModel().render(_model())

        with it("should be the class's doc comment, a bare star between its paragraphs"):
            expect(self.code).to(contain(f"/**\n * {STORY}\n *\n * {CLOSING}\n *\n * {LINES}\n * {PRICE}\n */\nclass Cart"))

        with it("should read back as the class's language"):
            expect(JavaScriptCleanEngineeringModel().parse(self.code).modules[0].classes[0].intent).to(equal(LANGUAGE))
