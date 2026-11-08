"""BDD spec for DDD practice model nodes."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("cdd_guidance/practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be, contain, equal, expect
from mamba import before, context, description, it

from harness.graph.graph import Graph

from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.ddd.model.markdown.class_cards import ClassCard
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, Entity, ValueObject
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass


def _class(name: str, stereotypes: list[str]) -> TacticalClass:
    oclass = OoadClass(name, 1)
    oclass.stereotypes = stereotypes
    return TacticalClass(oclass)


with description("a class as DDD reads it"):
    with it("should name the aggregate root its heading marks"):
        expect(TacticalClass(ClassCard.from_heading("**ShoppingCart** <<Aggregate Root>> <<Entity>>")).kind()).to(equal("EntityRoot"))

    with it("should name the value object its heading marks"):
        expect(TacticalClass(ClassCard.from_heading("**CartItem** <<Value Object>>")).kind()).to(equal("ValueObject"))

    with it("should name the repository its heading marks"):
        expect(TacticalClass(ClassCard.from_heading("**ShoppingCartRepository** <<Repository>>")).kind()).to(equal("Repository"))

    with it("should read the repository stereotype the graph reads from a @repository decorator"):
        expect(_class("CartRepository", ["Repository"]).kind()).to(equal("Repository"))

    with it("should not infer a building block for a screen registry class name"):
        expect(_class("OnboardingStepScreen", []).inferred_kind(set())).to(equal(None))

    with it("should not make a capitalised class with no stereotype an entity"):
        expect(_class("Invoice", []).inferred_kind({"Invoice", "Customer"})).to(equal(None))

    with it("should name an aggregate root by the repository beside it"):
        expect(_class("Invoice", []).inferred_kind({"Invoice", "InvoiceRepository"})).to(equal("EntityRoot"))


with description("a bounded context on a graph"):
    with before.each:
        self.graph = Graph()
        self.context = BoundedContext("orders", graph=self.graph)
        self.aggregate = Aggregate("account")
        self.entity = Entity("Account")
        self.aggregate.classes.append(self.entity)
        self.context.append_aggregate(self.aggregate)

    with it("should be the graph node for the aggregate"):
        expect(self.aggregate.node).to(be(self.aggregate))

    with it("should keep the aggregate on the context graph"):
        expect(self.aggregate.graph).to(be(self.graph))
        expect(self.entity.graph).to(be(self.graph))

    with it("should record the aggregate and belongsTo"):
        practice = self.graph.practice("ddd")
        aggregates = [(edge.parent.name, edge.child.name) for edge in practice.in_graph.edges("aggregates")]
        belongs = [(edge.parent.name, edge.child.name) for edge in practice.in_graph.edges("belongsTo")]
        expect(aggregates).to(contain(("orders", "account")))
        expect(belongs).to(contain(("account", "orders"), ("Account", "account")))




with description("a module holding a value object"):
    with before.each:
        self.module = Aggregate("cart")
        money = ValueObject("Money", 1, intent="an amount in one currency")
        money.stereotypes = ["Value Object"]
        money.properties.append(Property("amount", 1, "int"))
        money.operations.append(Operation("add", 1))
        self.module.classes.append(money)

    with context("that is cloned"):
        with before.each:
            self.cloned = self.module.clone().classes[0]

        with it("should keep the value object's stereotypes"):
            expect(self.cloned.stereotypes).to(equal(["Value Object"]))

        with it("should keep the value object's properties"):
            expect([item.name for item in self.cloned.properties]).to(equal(["amount"]))

        with it("should keep the value object's operations"):
            expect([item.name for item in self.cloned.operations]).to(equal(["add"]))
