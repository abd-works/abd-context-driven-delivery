"""A model document whose headings carry an HTML comment after their words, as Clean Engineering's own template marks
each heading with the fidelities that write it (`## {ClassName}   <!-- Md -->`). A comment is no part of what a heading
names: the class, the module and the module's sections are read by the words before it."""

from expects import equal, expect
from mamba import before, description, it

from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel

_DOCUMENT = (
    "# shop/ledger                                  <!-- Mu -->\n"
    "\n"
    "- **Purpose:** keep the shop's ledger.\n"
    "\n"
    "## Constraint                                  <!-- Mu -->\n"
    "\n"
    "Every entry is recorded once.\n"
    "\n"
    "## Ledger                                      <!-- Md -->\n"
    "\n"
    "+ Ledger(owner: str)\n"
    "------\n"
    "+ balance: int\n"
    "----\n"
    "+ record(entry: str): str\n"
    "\n"
    "## Entry : Record                              <!-- Md, optional -->\n"
    "\n"
    "------\n"
    "+ amount: int\n"
)


with description("a model document whose headings carry a comment after their words") as self:
    with before.all:
        self.model = MarkdownCleanEngineeringModel().parse(_DOCUMENT)
        self.module = self.model.modules[0]

    with it("should name the module by the words before the comment"):
        expect(self.module.name).to(equal("shop/ledger"))

    with it("should name each class by the words before the comment"):
        expect([cls.name for cls in self.module.classes]).to(equal(["Ledger", "Entry"]))

    with it("should read the class a heading's comment follows as extending the class it names"):
        expect(self.module.classes[1].bases if len(self.module.classes) > 1 else None).to(equal(["Record"]))

    with it("should read a Constraint heading as the module's constraint, not as a class"):
        expect(self.module.constraint).to(equal("Every entry is recorded once."))
