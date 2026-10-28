"""Mamba spec for `a domain model Markdown document` rendered back to Markdown.

The fixture is a trimmed copy of a pml-web domain model: a document title over bounded-context
modules, aggregate headings inside each module, and bold class cards under each aggregate.
"""

from pathlib import Path

from mamba import description, context, it, before
from expects import equal, contain, be_true, expect

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import (
    MarkdownCleanEngineeringModel,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "domain-model.md"


def _content(model):
    """Module and class names with each class's intent, properties, and operations."""
    return [
        (
            module.name,
            [
                (
                    loaded.name,
                    loaded.intent,
                    [prop.save() for prop in loaded.properties],
                    [operation.render() for operation in loaded.operations],
                )
                for loaded in module.classes
            ],
        )
        for module in model.modules
    ]


with description("a domain model Markdown document") as self:
    with before.each:
        self.text = FIXTURE.read_text(encoding="utf-8")
        self.parsed = MarkdownCleanEngineeringModel().parse(self.text)
        self.rendered = MarkdownCleanEngineeringModel().render(self.parsed)

    with context("parsed"):
        with it("should hold one module per bounded context that has class cards"):
            expect([module.name for module in self.parsed.modules]).to(
                equal(["Customer | custom", "Inventory | custom"])
            )

        with it("should hold one class per class card"):
            expect([[c.name for c in module.classes] for module in self.parsed.modules]).to(equal([
                ["AccountCredentials", "CredentialsValidation", "PasswordReset", "CredentialsRepository"],
                ["Plan", "PlanFeature", "PlanRepository", "PaymentGateway"],
            ]))

        with it("should read each card's properties and operations"):
            card = self.parsed.modules[0].classes[0]
            expect([prop.name for prop in card.properties]).to(contain("email", "validation", "passwordReset"))
            expect([operation.name for operation in card.operations]).to(contain("register", "signOut"))

    with context("rendered back to Markdown"):
        with it("should write the document it was parsed from"):
            expect(self.rendered).to(equal(self.text))

        with it("should parse to the same modules, classes, properties, and operations"):
            again = MarkdownCleanEngineeringModel().parse(self.rendered)
            expect(_content(again)).to(equal(_content(self.parsed)))

    with context("with a new operation on one class"):
        with before.each:
            card = self.parsed.modules[1].classes[2]
            from cdd_guidance.practices.clean_engineering.model.base_class_model import Operation
            card.operations.append(Operation(name="retire", parameters=["plan: Plan"], return_type="void"))
            self.rendered = MarkdownCleanEngineeringModel().render(self.parsed)

        with it("should write that card from the model under its own heading"):
            expect(self.rendered).to(contain("#### **PlanRepository** <<Repository>>\n"))
            expect(self.rendered).to(contain("+ retire(plan: Plan): void"))

        with it("should leave every other card as written"):
            others = self.text.split("#### **PlanRepository**")[0]
            expect(self.rendered.startswith(others)).to(be_true)

    with context("rendered through the clean engineering render tool"):
        with it("should write the document it was given"):
            result = CleanEngineering(fidelity="model").render("markdown", self.text, source="markdown")
            expect(result["content"]).to(equal(self.text))
