"""Mamba spec for a class card that opens with its language.

At model fidelity each class's language sits on its own card, under its heading and above its members: a short story
told from the class (what it is for, how it works, which classes it works with, the states it moves through), then one
``-`` bullet per responsibility. The reader keeps all of it as the class's intent, paragraph breaks included, and still
reads the constructor and members below it; a card written again from the class writes the language back as it was.
"""

from mamba import description, context, it, before
from expects import equal, contain, expect

from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import (
    MarkdownCleanEngineeringModel,
)

STORY = (
    "The *Cart* is the customer's order while they are still building it. The Cart turns each plan the customer picks "
    "into a *Line*, and becomes the customer's once they verify an account."
)
SECOND_PARAGRAPH = "When the order is placed, the Cart closes, and nothing in it changes."
LINES_BULLET = (
    "- **Lines.** The Cart adds a Line for each plan the customer picks. When the customer removes a line, the Cart tells "
    "the *Line* it has left the order, and the Line gives up what it was holding."
)
PRICE_BULLET = (
    "- **Price.** The Cart calculates the monthly charge from its Lines' plan prices less its *FamilyDiscount*; the "
    "*ProductOrder* takes the first bill as its up-front payment."
)
LANGUAGE = "\n\n".join([STORY, SECOND_PARAGRAPH, f"{LINES_BULLET}\n{PRICE_BULLET}"])

CARD = f"""# cart

- **Purpose:** hold the customer's order while they build it.

## **Cart**

{LANGUAGE}

+ Cart(id: string)
\t// handed out by CartRepository.create
------
+ << composition >> lines: Line[]
\t// at most 5
----
+ addLine(plan: Plan): Line
- _renumber(): None
"""


with description("a class card that opens with its language") as self:
    with before.each:
        self.model = MarkdownCleanEngineeringModel().parse(CARD)
        self.cart = self.model.modules[0].classes[0]

    with context("its intent"):
        with it("should keep the story and one bullet per responsibility, with their paragraph breaks"):
            expect(self.cart.intent).to(equal(LANGUAGE))

    with context("its typed block"):
        with it("should read the constructor below the language, not a responsibility bullet"):
            constructors = [op.name for op in self.cart.operations if op.name == "Cart"]
            expect(constructors).to(equal(["Cart"]))

        with it("should read the properties and operations below the language"):
            expect(([prop.name for prop in self.cart.properties], [op.name for op in self.cart.operations if op.name != "Cart"])).to(
                equal((["lines"], ["addLine", "_renumber"])))

    with context("that is written again after a member changes"):
        with before.each:
            self.cart.operations[-1].name = "_number"
            self.written = self.model.render(self.model)

        with it("should write the language under the heading, above the members, as it was read"):
            expect(self.written).to(contain(f"Cart\n\n{LANGUAGE}\n\n+ Cart("))
