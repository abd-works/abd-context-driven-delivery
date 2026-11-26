"""Mamba spec for `a domain model written after the DDD model template`, read and written by Clean Engineering.

The DDD model template (`practices/ddd/templates/model.md`, artifact `ce-domain-model`) extends Clean Engineering's
class-model template: `##` a bounded context, `###` an aggregate, `####` a class named plainly with its
`<<Stereotypes>>`, and the root's repository as a `**{Root}Repository** «Repository»` block inside the root's card.
The fixture is a trimmed copy of pml-web's domain model in that layout.
"""

from pathlib import Path

from expects import be_false, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "ddd-layout-domain-model.md"
TEXT = FIXTURE.read_text(encoding="utf-8")
PARSED = MarkdownCleanEngineeringModel().parse(TEXT)


def _class(name):
    return next(loaded for loaded in PARSED.every_class() if loaded.name == name)


with description("a domain model written after the DDD model template") as self:
    with context("parsed"):
        with it("should hold one module per bounded context that has classes"):
            expect([module.name for module in PARSED.modules]).to(equal(["Customer"]))

        with it("should hold one class per plain stereotyped heading and per repository block"):
            expect([loaded.name for loaded in PARSED.modules[0].classes]).to(
                equal(["Credentials", "CredentialsRepository", "PasswordReset", "IccidInventoryRepository"])
            )

        with it("should read the repository block as a class of its own, marked Repository"):
            expect(_class("CredentialsRepository").stereotypes).to(equal(["Repository"]))
            expect([prop.name for prop in _class("CredentialsRepository").properties]).to(equal(["accounts"]))
            expect([operation.name for operation in _class("CredentialsRepository").operations]).to(
                equal(["create", "load", "update"])
            )

        with it("should leave the repository's members off the root"):
            expect([operation.name for operation in _class("Credentials").operations]).to(
                equal(["register", "requestTemporaryPassword", "signOut"])
            )

        with it("should keep the root's language, invariants, notes and calls"):
            root = _class("Credentials")
            expect(root.intent).to(contain("The *Credentials* are the email and password"))
            expect(root.invariants).to(equal(["A token is issued only to a verified account with no new password pending."]))
            expect(root.operations[1].callees).to(equal(["CredentialsRepository.load(this)", "PasswordReset.send()"]))

    with context("rendered back to markdown"):
        with it("should write the document it was read from"):
            expect(PARSED.render(PARSED)).to(equal(TEXT))

    with context("with one class changed"):
        with before.each:
            self.changed = MarkdownCleanEngineeringModel().parse(TEXT)
            from cdd_guidance.practices.clean_engineering.model.operation import Operation

            for loaded in self.changed.every_class():
                if loaded.name in ("PasswordReset", "CredentialsRepository"):
                    loaded.operations.append(Operation.from_signature("retire(): void"))
            self.written = self.changed.render(self.changed)

        with it("should write a changed class under its plain heading, with no constructor the card did not write"):
            expect(self.written).to(contain("#### PasswordReset <<Entity>>\n\nAccess Selfcare.\n\n------\n"))

        with it("should write a changed repository as its block inside the root's card"):
            expect(self.written).to(contain("**CredentialsRepository** «Repository»\n\n------\n+ accounts"))
            expect(self.written).to(contain("+ update(credentials: Credentials): Credentials\n+ retire(): void\n"))

    with context("through the clean engineering render tool"):
        with before.all:
            self.practice = CleanEngineering(fidelity="model")
            self.drawing = self.practice.render("drawio", TEXT, source="markdown").content

        with it("should draw every class as its own card, the repository block too"):
            for name in ("Credentials", "CredentialsRepository", "PasswordReset", "IccidInventoryRepository"):
                expect(self.drawing).to(contain(f"&lt;b&gt;{name}&lt;/b&gt;"))

        with it("should draw no card named after a context or a section heading"):
            expect("&lt;b&gt;Layout&lt;/b&gt;" in self.drawing).to(be_false)
            expect("&lt;b&gt;Customer&lt;/b&gt;" in self.drawing).to(be_false)

        with it("should write the file back unchanged from its drawing"):
            back = self.practice.render("markdown", self.drawing, source="drawio", previous=TEXT).content
            expect(back).to(equal(TEXT))

        with it("should write the repository as its own Python class, with its property and operations"):
            code = self.practice.render("python", TEXT, source="markdown").content
            expect(code).to(contain("class CredentialsRepository"))
            repository = code.split("class CredentialsRepository", 1)[1].split("\nclass ", 1)[0]
            expect(repository).to(contain("accounts"))
            expect(repository).to(contain("def load("))
            credentials = code.split("class Credentials", 1)[1].split("\nclass ", 1)[0]
            expect("def load(" in credentials).to(be_false)


BOOKSHOP_ORDERING = Path(__file__).resolve().parents[1] / "fixtures" / "bookshop" / "ordering-model.md"
CART_REPOSITORY = """
**CartRepository** «Repository»

------
+ carts: Collection<Cart>
----
+ load(customer_id: str): Cart
+ save(cart: Cart): Cart
"""


with description("a class card in the class-model template with its repository written inside it") as self:
    with before.all:
        written = BOOKSHOP_ORDERING.read_text(encoding="utf-8")
        self.text = written.replace("\t// an empty cart is refused\n", "\t// an empty cart is refused\n" + CART_REPOSITORY, 1)
        self.practice = CleanEngineering(fidelity="model")
        self.drawing = self.practice.render("drawio", self.text, source="markdown").content
        self.code = self.practice.render("python", self.text, source="markdown").content

    with it("should draw the repository as a card of its own"):
        expect(self.drawing).to(contain("&lt;b&gt;CartRepository&lt;/b&gt;"))

    with it("should write the repository as its own Python class, with its property"):
        repository = self.code.split("class CartRepository", 1)[1].split("\nclass ", 1)[0]
        expect(repository).to(contain("carts"))

    with it("should leave the repository's operations off the root class in Python"):
        cart = self.code.split("class Cart:", 1)[1].split("\nclass ", 1)[0]
        expect("def load(" in cart).to(be_false)

    with it("should write the file back unchanged from its drawing"):
        back = self.practice.render("markdown", self.drawing, source="drawio", previous=self.text).content
        expect(back).to(equal(self.text))
