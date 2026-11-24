"""Model fidelity — the aggregate model converts to Clean Engineering code and back."""

from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

_MODEL = (Path(__file__).resolve().parent / "_examples" / "expected" / "domain-model.md").read_text(encoding="utf-8")


def _round_trip(code_format):
    code = Ddd(fidelity="model").render(code_format, _MODEL, source="markdown").content
    back = Ddd(fidelity="model").render("markdown", code, source=code_format).content
    return code, MarkdownBoundedContextMap().parse(back)


def _written_class(name):
    """The python class the map writes for the card called name."""
    code = PythonCleanEngineeringModel()
    MarkdownBoundedContextMap().parse(_MODEL).write_classes(code)
    return next(oclass for oclass in code.every_class() if oclass.name == name)


def _aggregate(model, context_name, aggregate_name):
    found = next(item for item in model.contexts if item.name == context_name)
    return next(item for item in found.aggregates if item.name == aggregate_name)


def _keeps_contexts(code_format):
    _code, model = _round_trip(code_format)
    expect([(item.name, item.owner) for item in model.contexts]).to(
        equal([("Customer", "custom"), ("Service", "custom")])
    )
    expect([item.name for item in model.contexts[0].aggregates]).to(equal(["Customer Profile", "KYC"]))


def _keeps_cards(code_format):
    _code, model = _round_trip(code_format)
    aggregate = _aggregate(model, "Customer", "Customer Profile")
    expect([(card.name, card.stereotypes) for card in aggregate.classes]).to(
        equal([
            ("CustomerProfile", ["Aggregate Root", "Entity"]),
            ("CustomerProfileRepository", ["Repository"]),
            ("Identity", ["Value Object"]),
            ("Address", ["Value Object"]),
        ])
    )
    expect([item.name for item in aggregate.repository.operations]).to(equal(["create", "load", "update"]))


def _keeps_operations(code_format):
    _code, model = _round_trip(code_format)
    root = _aggregate(model, "Customer", "Customer Profile").root
    expect([item.name for item in root.operations]).to(equal(["enterProfileDetails", "sendSupportRequest"]))


def _composes_members(code_format):
    _code, model = _round_trip(code_format)
    root = _aggregate(model, "Customer", "Customer Profile").root
    kinds = {item.name: item.stereotype for item in root.properties}
    expect((kinds["identity"], kinds["address"])).to(equal(("composition", "composition")))


def _keeps_integrations(code_format):
    _code, model = _round_trip(code_format)
    integration = _aggregate(model, "Service", "Subscription").integrations[0]
    expect((integration.context, integration.pattern)).to(equal(("Customer", "Customer/Supplier")))


with description("Ddd.render at model fidelity"):
    with context("to python and back"):
        with it("should keep contexts, owners, and aggregates"):
            _keeps_contexts("python")

        with it("should keep each class's stereotypes and the root's repository"):
            _keeps_cards("python")

        with it("should keep domain operations without constructors"):
            _keeps_operations("python")

        with it("should compose the members the root holds"):
            _composes_members("python")

        with it("should keep the integrations from the map"):
            _keeps_integrations("python")

    with context("to typescript and back"):
        with it("should keep contexts, owners, and aggregates"):
            _keeps_contexts("typescript")

        with it("should keep each class's stereotypes and the root's repository"):
            _keeps_cards("typescript")

        with it("should keep domain operations without constructors"):
            _keeps_operations("typescript")

        with it("should compose the members the root holds"):
            _composes_members("typescript")

        with it("should keep the integrations from the map"):
            _keeps_integrations("typescript")

    with context("written into a python class model"):
        with it("should give each class the modules of its context and aggregate as its module path"):
            expect(_written_class("CustomerProfile").module_path).to(equal(["Customer | custom", "Customer Profile"]))

        with it("should leave the class's own intent free of its place"):
            expect("Customer Profile" in _written_class("CustomerProfile").intent).to(equal(False))

        with it("should give the root a dependency for each integration, with its facts as details"):
            arcs = [item for item in _written_class("Subscription").dependencies if item.details]
            expect([(item.target, item.label, item.details["direction"]) for item in arcs]).to(
                equal([("CustomerProfile", "Customer/Supplier", "downstream")])
            )

        with it("should keep the arc's target as its context, aggregate, and entity, each its own detail"):
            arc = next(item for item in _written_class("Subscription").dependencies if item.details)
            expect({key: arc.details.get(key) for key in ("context", "aggregate", "entity")}).to(
                equal({"context": "Customer", "aggregate": "Customer Profile", "entity": "CustomerProfile"})
            )

        with it("should leave the root's intent free of its integrations"):
            expect("Integrations" in _written_class("Subscription").intent).to(equal(False))

    with context("to python"):
        with it("should write each class's stereotypes as decorators"):
            code, _model = _round_trip("python")
            expect(code).to(contain("@aggregate_root\n@entity\nclass CustomerProfile"))

        with it("should name the class's module path in its doc comment"):
            code, _model = _round_trip("python")
            expect(code).to(contain('class CustomerProfile:\n    """Module: Customer | custom · Customer Profile"""'))

        with it("should keep each integration's direction and what it crosses"):
            _code, model = _round_trip("python")
            integration = _aggregate(model, "Service", "Subscription").integrations[0]
            expect((integration.direction, integration.crosses)).to(equal(("downstream", "customer identity")))

        with it("should write generics python can read back"):
            code, _model = _round_trip("python")
            expect(code).to(contain("Collection[CustomerProfile]"))
            expect("Collection<" in code).to(equal(False))

    with context("to typescript"):
        with it("should write each class's stereotypes as decorators"):
            code, _model = _round_trip("typescript")
            expect(code).to(contain("@AggregateRoot()\n@Entity()\nclass CustomerProfile"))

    with context("from code whose classes carry decorators that are not DDD's"):
        with it("should keep only the DDD stereotypes on each card"):
            code = "@dataclass\n@value_object\nclass Money:\n    amount: int\n\n@entity\nclass Wallet:\n    money: Money\n"
            back = Ddd(fidelity="model").render("markdown", code, source="python").content
            cards = MarkdownBoundedContextMap().parse(back).contexts[0].aggregates[0].classes
            expect(sorted((card.name, card.stereotypes) for card in cards)).to(
                equal([("Money", ["Value Object"]), ("Wallet", ["Entity"])])
            )

    with context("from code with no stereotypes or places"):
        with it("should group each repository and member with the class that holds it"):
            code = (
                "class Cart:\n"
                "    lines: list[CartLine]\n\n"
                "    def check_out(self) -> None: ...\n\n"
                "class CartLine:\n"
                "    quantity: int\n\n"
                "class CartRepository:\n"
                "    def load(self, cart_id: str) -> Cart: ...\n"
            )
            back = Ddd(fidelity="model").render("markdown", code, source="python").content
            model = MarkdownBoundedContextMap().parse(back)
            aggregate = model.contexts[0].aggregates[0]
            expect([card.name for card in aggregate.classes]).to(equal(["Cart", "CartRepository", "CartLine"]))
            expect(aggregate.repository is not None).to(be_true)


# Seen 2026-11-21 (r3-bolt-07): a model rendered from Python to TypeScript kept Python's type spellings, an operation's
# note and call became a Python body to translate, and TypeScript rendered back kept `-> boolean` and lost each note.
_SHOP = """# Domain Model

## Ordering | custom

### Cart

#### Cart <<Aggregate Root>> <<Entity>>

------
+ cartId: string
+ << composition >> lines: CartLine[]
+ checkedOut: boolean
----
+ addBook(bookId: string, quantity: number): CartLine
	// the title and price cross at the moment the book is added
	-> BookRepository.load(bookId)
+ isEmpty(): boolean

#### CartLine <<Value Object>>

------
+ bookId: string
+ quantity: number
----

#### CartRepository <<Repository>>

------
+ << aggregation >> carts: Collection<Cart>
----
+ load(cartId: string): Cart
+ search(customerId: string): Order[]
	// the Customer looks up their own orders
"""


def _rendered_through(*formats):
    """The shop's model rendered from markdown through each of formats in turn: the text of the last."""
    text, source = _SHOP, "markdown"
    for target in formats:
        text, source = Ddd(fidelity="model").render(target, text, source=source).content, target
    return text


with description("a domain model rendered from one code format to the other") as self:
    with context("from Python to TypeScript"):
        with before.all:
            self.code = _rendered_through("python", "typescript")

        with it("should write a list as a TypeScript array"):
            expect(self.code).to(contain("search(customerId: string): Order[] {"))

        with it("should write a generic type in TypeScript's brackets"):
            expect(self.code).to(contain("carts: Collection<Cart>;"))

        with it("should keep the relationship each property is marked with"):
            expect(self.code).to(contain("  // << composition >>\n  lines: CartLine[];"))

        with it("should write an operation's note as a TypeScript comment"):
            expect(self.code).to(contain("    // the Customer looks up their own orders\n"))

        with it("should write an operation's call in TypeScript, with its arguments"):
            expect(self.code).to(contain("    BookRepository.load(bookId);\n"))

        with it("should leave no Python body to translate"):
            expect(self.code).not_to(contain("python body to translate"))

    with context("from TypeScript back to Python"):
        with before.all:
            self.code = _rendered_through("python", "typescript", "python")

        with it("should write a boolean as Python writes one"):
            expect(self.code).to(contain("def isEmpty(self) -> bool:"))

        with it("should leave no TypeScript body to translate"):
            expect(self.code).not_to(contain("typescript body to translate"))

    with context("from Python whose operation has a docstring, to TypeScript and back"):
        with it("should keep the docstring"):
            code = (
                '@aggregate_root\n@entity\nclass Cart:\n    """Module: Ordering | custom · Cart"""\n\n'
                "    def add_book(self, book_id: str) -> bool:\n"
                '        """the title and price cross at the moment the book is added"""\n'
                "        raise NotImplementedError\n"
            )
            typescript = Ddd(fidelity="model").render("typescript", code, source="python").content
            back = Ddd(fidelity="model").render("python", typescript, source="typescript").content
            expect(back).to(contain('"""the title and price cross at the moment the book is added"""'))

    with context("from TypeScript to markdown"):
        with before.all:
            self.back = _rendered_through("python", "typescript", "markdown")

        with it("should keep each operation's note"):
            expect(self.back).to(contain("+ search(customerId: string): Order[]\n\t// the Customer looks up their own orders"))

        with it("should keep each call with its arguments"):
            expect(self.back).to(contain("\t-> BookRepository.load(bookId)"))


# Requested 2026-11-24 (r3-bolt-07): a domain model's bodies, written in code, are translated into the other language
# statement by statement, through the one translation Clean Engineering's render uses.
_CART_CODE = '''\
@aggregate_root
@entity
class Cart:
    """Module: Ordering | custom · Cart"""

    def add(self, book: Book, quantity: int) -> CartLine:
        if quantity <= 0:
            raise OutOfStock(book.title)
        for line in self.lines:
            if line.book == book:
                line.quantity += quantity
                return line
        line = CartLine(book, quantity)
        self.lines.append(line)
        return line
'''

_ADD_IN_TYPESCRIPT = """\
  add(book: Book, quantity: number): CartLine {
    if (quantity <= 0) {
      throw new OutOfStock(book.title);
    }
    for (const line of this.lines) {
      if (line.book === book) {
        line.quantity += quantity;
        return line;
      }
    }
    const line = new CartLine(book, quantity);
    this.lines.push(line);
    return line;
  }
"""

_ADD_IN_PYTHON = """\
    def add(self, book: Book, quantity: float) -> CartLine:
        if quantity <= 0:
            raise OutOfStock(book.title)
        for line in self.lines:
            if line.book == book:
                line.quantity += quantity
                return line
        line = CartLine(book, quantity)
        self.lines.append(line)
        return line
"""


with description("a domain model whose operation has a body written in code") as self:
    with context("rendered from Python to TypeScript"):
        with it("should translate the guard, the loop and the raise into TypeScript"):
            typescript = Ddd(fidelity="model").render("typescript", _CART_CODE, source="python").content
            expect(typescript).to(contain(_ADD_IN_TYPESCRIPT))

    with context("rendered from Python to TypeScript and back"):
        with it("should come back as the same Python statements"):
            typescript = Ddd(fidelity="model").render("typescript", _CART_CODE, source="python").content
            back = Ddd(fidelity="model").render("python", typescript, source="typescript").content
            expect(back).to(contain(_ADD_IN_PYTHON))
