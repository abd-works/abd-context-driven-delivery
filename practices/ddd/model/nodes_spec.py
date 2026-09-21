"""BDD spec for DDD practice model nodes."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect, have_length
from mamba import description, it

from practices.clean_engineering.model.base_class_model import OoadClass
from practices.ddd.model import (
    Aggregate,
    BoundedContext,
    Entity,
    EntityRoot,
    Repository,
    ddd_class_for,
    ddd_class_kind,
    parse_bounded_context_map,
)
from practices.knowledge_graph.model import Kind, PracticeGraph
from practices.knowledge_graph.model.loader import _wire_ddd_relationships
from practices.knowledge_graph.model.nodes import (
    GraphAggregate,
    GraphBoundedContext,
    GraphEntityRoot,
    GraphProperty,
    GraphRepository,
    GraphValueObject,
)
from practices.knowledge_graph.model.practice_graph import PracticeGraph


with description("DDD model nodes"):
    with it("should classify tactical stereotypes from decorated class names"):
        expect(ddd_class_kind("**ShoppingCart** <<Aggregate Root>> <<Entity>>")).to(
            equal("EntityRoot")
        )
        expect(ddd_class_kind("**CartItem** <<Value Object>>")).to(equal("ValueObject"))
        expect(ddd_class_kind("**ShoppingCartRepository** <<Repository>>")).to(
            equal("Repository")
        )

    with it("should map CE classes to DDD stereotypes via ddd_class_for"):
        source = OoadClass("**Discount** <<Value Object>>", sequential_order=1)
        target = ddd_class_for(source)
        expect(target.semantic_type()).to(equal("ValueObject"))
        expect(target.name).to(equal("Discount"))

    with it("should reconcile BoundedContext aggregates in child_collections"):
        bc = BoundedContext("Sales", 1)
        agg = Aggregate("ShoppingCart", 1)
        bc.aggregates.append(agg)
        other = BoundedContext("Sales", 1)
        other.aggregates.append(Aggregate("ShoppingCart", 1))
        bc.translate_from(other)
        expect(len(bc.aggregates)).to(equal(1))
        expect(bc.aggregates[0].name).to(equal("ShoppingCart"))

    with it("should parse bounded context map BC to Aggregate tree"):
        text = """# Bounded Context Map — Shop

## Sales | custom

### ShoppingCart

- CartItem

## Catalog | custom

### Product

- Product
"""
        contexts = parse_bounded_context_map(text)
        expect(len(contexts)).to(equal(2))
        expect(contexts[0].name).to(equal("Sales"))
        expect(contexts[0].aggregates[0].name).to(equal("ShoppingCart"))
        expect("CartItem" in contexts[0].aggregates[0].concepts).to(equal(True))


with description("PracticeGraph DDD wiring"):
    with it("should load bounded contexts and aggregates from examples map"):
        graph = PracticeGraph.load(_REPO_ROOT / "practices" / "ddd" / "examples")
        bc_nodes = graph.nodes_of_type(GraphBoundedContext)
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
        agg = GraphAggregate("Customer", 1)
        graph.register(agg)
        graph.index_module(agg)

        identity_vo = GraphValueObject("Identity", 1)
        id_prop = GraphProperty("id", 1, type_hint="string")
        identity_vo.property_nodes = [id_prop]
        graph.register(identity_vo)
        graph.register(id_prop)
        graph.relate(identity_vo, Kind.OWNS, id_prop)
        graph.relate(id_prop, Kind.BELONGS_TO, identity_vo)

        root = GraphEntityRoot("Customer", 1)
        ident_prop = GraphProperty("identity", 1, type_hint="Identity")
        root.property_nodes = [ident_prop]
        graph.register(root)
        graph.register(ident_prop)
        graph.relate(root, Kind.OWNS, ident_prop)
        graph.relate(ident_prop, Kind.BELONGS_TO, root)

        repo = GraphRepository("CustomerRepository", 2)
        graph.register(repo)

        agg.classes = [identity_vo, root, repo]
        for oclass in agg.classes:
            graph.relate(agg, Kind.OWNS, oclass)
            graph.relate(oclass, Kind.BELONGS_TO, agg)

        _wire_ddd_relationships(graph)

        kinds = {r.kind for r in graph.relationships}
        expect(Kind.ROOT in kinds).to(equal(True))
        expect(Kind.ACCESSES in kinds).to(equal(True))
        expect(Kind.HAS_IDENTITY in kinds).to(equal(True))
        expect(agg.root).to(equal(root))
        expect(root.aggregate).to(equal(agg))
        expect(repo.accesses).to(equal(root))
