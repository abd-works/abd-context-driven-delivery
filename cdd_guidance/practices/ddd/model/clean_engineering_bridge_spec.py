"""Model fidelity — the aggregate model converts to Clean Engineering code and back."""

from pathlib import Path

from expects import be_true, contain, equal, expect
from mamba import context, description, it

from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ddd.model.markdown.nodes import MarkdownBoundedContextMap

_MODEL = (Path(__file__).resolve().parent / "_examples" / "expected" / "domain-model.md").read_text(encoding="utf-8")


def _round_trip(code_format):
    code = Ddd(fidelity="model").render(code_format, _MODEL, source="markdown")["content"]
    back = Ddd(fidelity="model").render("markdown", code, source=code_format)["content"]
    return code, MarkdownBoundedContextMap().parse(back)


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
    expect([(card.node.name, card.stereotypes) for card in aggregate.cards]).to(
        equal([
            ("CustomerProfile", ["Aggregate Root", "Entity"]),
            ("CustomerProfileRepository", ["Repository"]),
            ("Identity", ["Value Object"]),
            ("Address", ["Value Object"]),
        ])
    )
    expect([item.name for item in aggregate.repository.node.operations]).to(equal(["create", "load", "update"]))


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

    with context("to python"):
        with it("should write generics python can read back"):
            code, _model = _round_trip("python")
            expect(code).to(contain("Collection[CustomerProfile]"))
            expect("Collection<" in code).to(equal(False))

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
            back = Ddd(fidelity="model").render("markdown", code, source="python")["content"]
            model = MarkdownBoundedContextMap().parse(back)
            aggregate = model.contexts[0].aggregates[0]
            expect([card.node.name for card in aggregate.cards]).to(equal(["Cart", "CartRepository", "CartLine"]))
            expect(aggregate.repository is not None).to(be_true)
