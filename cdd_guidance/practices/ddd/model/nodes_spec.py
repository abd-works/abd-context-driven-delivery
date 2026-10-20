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
from mamba import before, description, it

from harness.graph.graph import Graph

from cdd_guidance.practices.ddd.model import ddd_class_kind
from cdd_guidance.practices.ddd.model.nodes import Aggregate, BoundedContext, Entity
from cdd_guidance.practices.ddd.model.stereotypes import inferred_tactical_kind


with description("DDD model nodes"):
    with it("should classify tactical stereotypes from decorated class names"):
        expect(ddd_class_kind("**ShoppingCart** <<Aggregate Root>> <<Entity>>")).to(
            equal("EntityRoot")
        )
        expect(ddd_class_kind("**CartItem** <<Value Object>>")).to(equal("ValueObject"))
        expect(ddd_class_kind("**ShoppingCartRepository** <<Repository>>")).to(
            equal("Repository")
        )

    with it("should not infer tactical kinds for screen registry class names"):
        expect(inferred_tactical_kind("OnboardingStepScreen", set())).to(equal(None))

    with it("should read @repository decorators from class declarations"):
        from cdd_guidance.practices.ddd.model.stereotypes import class_declaration_decorated_name

        source = "@repository\nclass CartRepository:\n    pass\n"
        decorated = class_declaration_decorated_name(source, "CartRepository")
        expect(ddd_class_kind(decorated)).to(equal("Repository"))


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
        aggregates = [(edge.parent.name, edge.child.name) for edge in practice.edges.get("aggregates", [])]
        belongs = [(edge.parent.name, edge.child.name) for edge in practice.edges.get("belongsTo", [])]
        expect(aggregates).to(contain(("orders", "account")))
        expect(belongs).to(contain(("account", "orders"), ("Account", "account")))

    with it("should open the same context from the graph"):
        restored = BoundedContext(self.graph)
        expect(restored.aggregates[0].name).to(equal("account"))
        expect(restored.aggregates[0].classes[0].name).to(equal("Account"))

