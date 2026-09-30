"""BDD spec for DDD practice model nodes."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, have_length
from mamba import description, it

from practices.ddd.model import ddd_class_kind
from harness.knowledge_graph import model as kg
from harness.knowledge_graph.model import Kind, PracticeGraph


with description("DDD model nodes"):
    with it("should classify tactical stereotypes from decorated class names"):
        expect(ddd_class_kind("**ShoppingCart** <<Aggregate Root>> <<Entity>>")).to(
            equal("EntityRoot")
        )
        expect(ddd_class_kind("**CartItem** <<Value Object>>")).to(equal("ValueObject"))
        expect(ddd_class_kind("**ShoppingCartRepository** <<Repository>>")).to(
            equal("Repository")
        )


with description("PracticeGraph DDD wiring"):
    with it("should load bounded contexts and aggregates from examples map"):
        graph = PracticeGraph.load(_REPO_ROOT / "practices" / "ddd" / "examples")
        bc_nodes = graph.nodes_of_type(kg.BoundedContext)
        expect(bc_nodes).to(have_length(2))
        sales = next(bc for bc in bc_nodes if bc.name == "Sales")
        expect(sales.aggregates[0].name).to(equal("ShoppingCart"))
        owns_agg = [
            r
            for r in graph.relationships
            if r.kind == Kind.OWNS
            and any(
                n.name == "ShoppingCart"
                for n in graph.nodes.values()
                if n.node_id == r.to_id
            )
        ]
        expect(owns_agg).to(have_length(1))

    with it("should wire root, belongsTo, accesses, and hasIdentity edges"):
        graph = PracticeGraph(_REPO_ROOT)
        agg = kg.Aggregate("Customer", 1)
        graph.register(agg)

        identity_vo = kg.ValueObject("Identity", 1)
        id_prop = kg.Property("id", 1, type_hint="string")
        identity_vo.property_nodes = [id_prop]
        graph.register(identity_vo)
        graph.register(id_prop)
        identity_vo.relate(Kind.OWNS, id_prop)
        id_prop.relate(Kind.BELONGS_TO, identity_vo)

        root = kg.GraphEntityRoot("Customer", 1)
        ident_prop = kg.Property("identity", 1, type_hint="Identity")
        root.property_nodes = [ident_prop]
        graph.register(root)
        graph.register(ident_prop)
        root.relate(Kind.OWNS, ident_prop)
        ident_prop.relate(Kind.BELONGS_TO, root)

        repo = kg.Repository("CustomerRepository", 2)
        graph.register(repo)

        agg.classes = [identity_vo, root, repo]
        for oclass in agg.classes:
            agg.relate(Kind.OWNS, oclass)
            oclass.relate(Kind.BELONGS_TO, agg)

        graph.wire_ddd()

        kinds = {r.kind for r in graph.relationships}
        expect(Kind.ROOT in kinds).to(equal(True))
        expect(Kind.ACCESSES in kinds).to(equal(True))
        expect(Kind.HAS_IDENTITY in kinds).to(equal(True))
        expect(agg.root).to(equal(root))
        expect(root.aggregate).to(equal(agg))
        expect(repo.accesses).to(equal(root))
