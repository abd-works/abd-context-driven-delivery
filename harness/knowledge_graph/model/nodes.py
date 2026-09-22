"""Practice graph nodes — extend canonical practice model types."""

from __future__ import annotations

import re
from typing import List

from practices.bdd.model.nodes import Context, Description, Observation
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from practices.clean_engineering.model.operation import Operation, Parameter
from practices.clean_engineering.model.property import Property
from practices.clean_engineering.model.type_refs import (
    is_primitive_type,
    parse_parameter,
    pascal_type_names,
)
from practices.ddd.model.nodes import (
    Aggregate,
    BoundedContext,
    DomainEvent,
    DomainService,
    Entity,
    EntityRoot,
    Repository,
    ValueObject,
    ddd_class_for,
)
from practices.ddd.model.stereotypes import plain_class_name
from practices.stories.model.background import Background
from practices.stories.model.example import Example
from practices.stories.model.nodes import Epic, Story, SubEpic
from practices.stories.model.scenario import Scenario
from practices.stories.model.step import Step
from practices.stories.model.story_map import StoryMap

from .graph_node import GraphNodeMixin, Kind


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------------------------------------------------------------------------
# Clean Engineering
# ---------------------------------------------------------------------------


class GraphCleanEngineeringModel(CleanEngineeringModel, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "CleanEngineeringModel"

    def load_module(self, source: Module) -> "GraphModule":
        if isinstance(source, BoundedContext):
            return GraphBoundedContext(source.name, source.sequential_order)
        if isinstance(source, Aggregate):
            return GraphAggregate(source.name, source.sequential_order)
        return GraphModule(source.name, source.sequential_order)


class GraphModule(Module, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "Module"

    def load_class(self, source: OoadClass) -> "GraphClass":
        return GraphClass(source.name, source.sequential_order)

    @property
    def external_classes(self) -> List["GraphClass"]:
        return [c for c in self.related(Kind.DEPENDS_ON) if isinstance(c, GraphClass)]


class GraphClass(OoadClass, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "OoadClass"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: Operation) -> "GraphOperation":
        node = GraphOperation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        node.parameters = [
            GraphParameter(p.name, p.sequential_order, p.type_hint) for p in source.parameters
        ]
        return node

    def sync_tree_from_legacy(self) -> None:
        self.property_nodes = [
            GraphProperty.from_field(field, index)
            for index, field in enumerate(self.properties, start=1)
        ]
        self.operation_nodes = [
            GraphOperation.from_field(field, index)
            for index, field in enumerate(self.operations, start=1)
        ]

    @property
    def home_module(self) -> GraphModule:
        owner = self.related(Kind.BELONGS_TO, direction="in")
        if not owner:
            raise RuntimeError(f"{self.name} has no owning Module")
        return owner[0]  # type: ignore[return-value]

    @property
    def external_classes(self) -> List["GraphClass"]:
        return [c for c in self.related(Kind.DEPENDS_ON) if isinstance(c, GraphClass)]


class GraphProperty(Property, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "Property"


class GraphParameter(Parameter, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "Parameter"


class GraphOperation(Operation, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "Operation"

    def load_parameter(self, source: Parameter) -> GraphParameter:
        return GraphParameter(source.name, source.sequential_order, source.type_hint)


# ---------------------------------------------------------------------------
# DDD (graph specialisations)
# ---------------------------------------------------------------------------


class GraphBoundedContext(BoundedContext, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "BoundedContext"

    def load_aggregate(self, source: Aggregate) -> "GraphAggregate":
        return GraphAggregate(source.name, source.sequential_order)


class GraphAggregate(Aggregate, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "Aggregate"

    def load_class(self, source: OoadClass) -> OoadClass:
        return graph_ddd_class_for(source)


class GraphEntity(Entity, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "Entity"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: Operation) -> "GraphOperation":
        node = GraphOperation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        node.parameters = [
            GraphParameter(p.name, p.sequential_order, p.type_hint) for p in source.parameters
        ]
        return node


class GraphEntityRoot(EntityRoot, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "EntityRoot"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: Operation) -> "GraphOperation":
        node = GraphOperation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        node.parameters = [
            GraphParameter(p.name, p.sequential_order, p.type_hint) for p in source.parameters
        ]
        return node


class GraphValueObject(ValueObject, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "ValueObject"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: Operation) -> "GraphOperation":
        node = GraphOperation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        node.parameters = [
            GraphParameter(p.name, p.sequential_order, p.type_hint) for p in source.parameters
        ]
        return node


class GraphRepository(Repository, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "Repository"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: Operation) -> "GraphOperation":
        node = GraphOperation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        node.parameters = [
            GraphParameter(p.name, p.sequential_order, p.type_hint) for p in source.parameters
        ]
        return node


class GraphDomainEvent(DomainEvent, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "DomainEvent"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: Operation) -> "GraphOperation":
        node = GraphOperation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        node.parameters = [
            GraphParameter(p.name, p.sequential_order, p.type_hint) for p in source.parameters
        ]
        return node


class GraphDomainService(DomainService, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "DomainService"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: Operation) -> "GraphOperation":
        node = GraphOperation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node.legacy_parameters = list(source.legacy_parameters)
        node.parameters = [
            GraphParameter(p.name, p.sequential_order, p.type_hint) for p in source.parameters
        ]
        return node


_GRAPH_DDD_BY_KIND = {
    "EntityRoot": GraphEntityRoot,
    "Entity": GraphEntity,
    "ValueObject": GraphValueObject,
    "Repository": GraphRepository,
    "DomainEvent": GraphDomainEvent,
    "DomainService": GraphDomainService,
}


def graph_ddd_class_for(source: OoadClass) -> OoadClass:
    """Promote a CE class to the matching graph DDD stereotype."""
    base = ddd_class_for(source)
    kind = base.semantic_type()
    if kind == "OoadClass":
        return GraphClass(
            plain_class_name(source.name),
            source.sequential_order,
            intent=source.intent,
        )
    graph_cls = _GRAPH_DDD_BY_KIND[kind]
    node = graph_cls(
        plain_class_name(source.name),
        source.sequential_order,
        intent=source.intent,
    )
    if isinstance(base, Repository) and base.accesses is not None:
        node.accesses = base.accesses
    if isinstance(base, EntityRoot) and base.aggregate is not None:
        node.aggregate = base.aggregate
    if isinstance(base, Entity) and base.identity:
        node.identity = list(base.identity)
    return node


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------


class GraphStoryMap(StoryMap, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "StoryMap"

    def load_epic(self, source: Epic) -> "GraphEpic":
        return GraphEpic(source.name, source.sequential_order)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphEpic(Epic, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Epic"

    def load_sub_epic(self, source: SubEpic) -> "GraphSubEpic":
        return GraphSubEpic(source.name, source.sequential_order)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphSubEpic(SubEpic, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "SubEpic"

    def load_sub_epic(self, source: SubEpic) -> "GraphSubEpic":
        return GraphSubEpic(source.name, source.sequential_order)

    def load_story(self, source: Story) -> "GraphStory":
        return GraphStory(source.name, source.sequential_order, source.story_type)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphStory(Story, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Story"

    def load_background(self, source: Background) -> "GraphBackground":
        return GraphBackground(source.name, source.sequential_order)

    def load_scenario(self, source: Scenario) -> "GraphScenario":
        return GraphScenario(source.name, source.sequential_order, source.story_name)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphScenario(Scenario, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Scenario"

    def load_background(self, source: Background) -> "GraphBackground":
        return GraphBackground(source.name, source.sequential_order)

    def load_step(self, source: Step) -> "GraphStep":
        return GraphStep(
            text=source.text,
            phase=source.phase,
            sequential_order=source.sequential_order,
            is_continuation=source.is_continuation,
            keyword=getattr(source, "keyword", "") or "",
            concepts=list(source.concepts),
            values=list(source.values),
            actor=source.actor,
            source=source.source,
            name=source.name,
        )

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphBackground(Background, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Background"

    def load_step(self, source: Step) -> "GraphStep":
        return GraphStep(
            text=source.text,
            phase=source.phase,
            sequential_order=source.sequential_order,
            is_continuation=source.is_continuation,
            keyword=getattr(source, "keyword", "") or "",
            concepts=list(source.concepts),
            values=list(source.values),
            actor=source.actor,
            source=source.source,
            name=source.name,
        )


class GraphStep(Step, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Step"


class GraphExample(Example, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Example"


# ---------------------------------------------------------------------------
# BDD (graph specialisations)
# ---------------------------------------------------------------------------


class GraphDescription(Description, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Description"

    def load_context(self, source: Context) -> "GraphContext":
        return GraphContext(source.name, source.sequential_order)


class GraphContext(Context, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Context"

    def load_observation(self, source: Observation) -> "GraphObservation":
        return GraphObservation(source.name, source.sequential_order)

    def load_context(self, source: Context) -> "GraphContext":
        return GraphContext(source.name, source.sequential_order)


class GraphObservation(Observation, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Observation"
