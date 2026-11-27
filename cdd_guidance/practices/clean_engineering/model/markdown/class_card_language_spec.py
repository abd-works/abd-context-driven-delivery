"""Mamba spec for a class card that opens with its language.

At model fidelity each class's language sits on its own card, above the typed block: its definition paragraph, then a
``### term`` per domain term it owns with ``-`` bullets. The reader keeps all of it as the class's intent and still reads
the constructor and members below it.
"""

from mamba import description, context, it, before
from expects import equal, contain, expect

from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import (
    MarkdownCleanEngineeringModel,
)

CARD = """# ability

- **Purpose:** hold a hero's ability ranks.

## **Ability**

*Ability* is one of a hero's eight traits; it holds a rank that modifies related rolls.

### ability rank

- Numeric value of an ability; starts at 0.
- Strength (STR) measures muscle power.
- **Invariant:** never below -5 by a player's choice.

+ Ability(name: AbilityName, rank: Integer)
	// a rank change reaches every derived trait in the same operation
------
+ rank: Integer
----
+ setRank(rank: Integer): Ability
- _cascade(): None
"""


with description("a class card that opens with its language") as self:
    with before.each:
        modules = MarkdownCleanEngineeringModel().parse(CARD).modules
        self.ability = modules[0].classes[0]

    with context("its intent"):
        with it("should keep the definition paragraph, the term heading and every bullet"):
            expect(self.ability.intent).to(contain(
                "*Ability* is one of a hero's eight traits; it holds a rank that modifies related rolls.",
                "### ability rank",
                "- Numeric value of an ability; starts at 0.",
                "- Strength (STR) measures muscle power.",
                "- **Invariant:** never below -5 by a player's choice.",
            ))

    with context("its typed block"):
        with it("should read the constructor below the language, not a language bullet"):
            constructors = [op.name for op in self.ability.operations if op.name == "Ability"]
            expect(constructors).to(equal(["Ability"]))

        with it("should read the properties and operations as before"):
            expect([prop.name for prop in self.ability.properties]).to(equal(["rank"]))
            expect([op.name for op in self.ability.operations if op.name != "Ability"]).to(equal(["setRank", "_cascade"]))
