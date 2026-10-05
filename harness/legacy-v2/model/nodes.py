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
    Repository,
    Specification,
    ValueObject,
)
from practices.ddd.model.stereotypes import plain_class_name
from practices.stories.model.story_model import (
    Background,
    Epic,
    Example,
    Increment,
    Scenario,
    Step,
    Story,
    StoryModel,
    Epic,
)

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
        return GraphProperty.from_field(source, source.sequential_order)

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
        return GraphProperty.from_field(source, source.sequential_order)

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


class GraphEntityRoot(Entity, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "EntityRoot"

    def __init__(self, name: str, sequential_order: int, **kwargs) -> None:
        super().__init__(name, sequential_order, **kwargs)
        self.is_root = True

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty.from_field(source, source.sequential_order)

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
        return GraphProperty.from_field(source, source.sequential_order)

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
        return GraphProperty.from_field(source, source.sequential_order)

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
        return GraphProperty.from_field(source, source.sequential_order)

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


class GraphSpecification(Specification, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "Specification"


class GraphDomainService(DomainService, GraphNodeMixin):
    practice = "ddd"
    _semantic_type_name = "DomainService"

    def load_property(self, source: Property) -> "GraphProperty":
        return GraphProperty.from_field(source, source.sequential_order)

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
    "Specification": GraphSpecification,
}


def graph_ddd_class_for(source: OoadClass) -> OoadClass:
    """Promote a CE class to the matching graph DDD stereotype."""
    from practices.ddd.model.stereotypes import ddd_class_kind

    kind = ddd_class_kind(source.name)
    if isinstance(source, Entity) and source.is_root:
        kind = "EntityRoot"
    elif isinstance(source, (Entity, ValueObject, Repository, DomainEvent, DomainService, Specification)):
        kind = source.semantic_type()
    if kind in (None, "OoadClass"):
        return GraphClass(
            plain_class_name(source.name),
            source.sequential_order,
            intent=source.intent,
        )
    if kind == "EntityRoot":
        node = GraphEntityRoot(
            plain_class_name(source.name),
            source.sequential_order,
            intent=source.intent,
        )
        node.is_root = True
        if isinstance(source, Entity) and source.aggregate is not None:
            node.aggregate = source.aggregate
        if isinstance(source, Entity) and source.identity:
            node.identity = list(source.identity)
        return node
    graph_cls = _GRAPH_DDD_BY_KIND[kind]
    node = graph_cls(
        plain_class_name(source.name),
        source.sequential_order,
        intent=source.intent,
    )
    if isinstance(source, Repository) and source.accesses is not None:
        node.accesses = source.accesses
    if isinstance(source, Entity) and source.identity:
        node.identity = list(source.identity)
    return node


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------


class GraphStoryModel(StoryModel, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "StoryModel"

    @classmethod
    def clone(cls, other: StoryModel) -> "GraphStoryModel":
        cloned = cls()
        for epic in other.epics:
            cloned.epics.append(GraphEpic.clone(epic))
        for increment in other.increments:
            cloned.increments.append(Increment.clone(increment))
        cloned.examples = other.examples.clone(cloned)
        return cloned

    def load_epic(self, source: Epic) -> "GraphEpic":
        return GraphEpic.clone(source)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample.clone(source)


class GraphEpic(Epic, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Epic"

    @classmethod
    def clone(cls, other: Epic) -> "GraphEpic":
        cloned = cls(other.name, other.sequential_order)
        cloned.estimate = other.estimate or ""
        for sub_epic in other.epics:
            cloned.epics.append(GraphEpic.clone(sub_epic))
        for story in other.stories:
            cloned.stories.append(GraphStory.clone(story))
        cloned.examples = other.examples.clone(cloned)
        return cloned

    def load_epic(self, source: Epic) -> "GraphEpic":
        return GraphEpic.clone(source)

    def load_story(self, source: Story) -> "GraphStory":
        return GraphStory.clone(source)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample.clone(source)


class GraphStory(Story, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Story"

    @classmethod
    def clone(cls, other: Story) -> "GraphStory":
        cloned = cls(other.name, other.sequential_order, other.story_type)
        cloned.actors = list(other.actors)
        cloned.domain_terms = list(other.domain_terms)
        cloned.evidence = list(other.evidence)
        for background in other.backgrounds:
            cloned.backgrounds.append(GraphBackground.clone(background))
        for scenario in other.scenarios:
            cloned.scenarios.append(GraphScenario.clone(scenario))
        return cloned

    def load_background(self, source: Background) -> "GraphBackground":
        return GraphBackground.clone(source)

    def load_scenario(self, source: Scenario) -> "GraphScenario":
        return GraphScenario.clone(source)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample.clone(source)


class GraphScenario(Scenario, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Scenario"

    @classmethod
    def clone(cls, other: Scenario) -> "GraphScenario":
        cloned = cls(other.name, other.sequential_order, other.story_name)
        cloned.is_outline = other.is_outline
        cloned.evidence = list(other.evidence)
        cloned.source = other.source
        for background in other.backgrounds:
            cloned.backgrounds.append(GraphBackground.clone(background))
        for step in other.steps:
            cloned.steps.append(GraphStep.clone(step))
        cloned.examples = other.examples.clone(cloned)
        return cloned

    def load_background(self, source: Background) -> "GraphBackground":
        return GraphBackground.clone(source)

    def load_step(self, source: Step) -> "GraphStep":
        return GraphStep.clone(source)

    def load_example(self, source: Example) -> "GraphExample":
        return GraphExample.clone(source)

class GraphBackground(Background, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Background"

    @classmethod
    def clone(cls, other: Background) -> "GraphBackground":
        cloned = cls(other.name, other.sequential_order)
        for step in other.steps:
            cloned.steps.append(GraphStep.clone(step))
        cloned.examples = other.examples.clone(cloned)
        return cloned

    def load_step(self, source: Step) -> "GraphStep":
        return GraphStep.clone(source)


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

    @classmethod
    def clone(cls, other: Description) -> "GraphDescription":
        cloned = cls(other.name, other.sequential_order)
        for context in other.contexts:
            cloned.contexts.append(GraphContext.clone(context))
        return cloned

    def load_context(self, source: Context) -> "GraphContext":
        return GraphContext.clone(source)


class GraphContext(Context, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Context"

    @classmethod
    def clone(cls, other: Context) -> "GraphContext":
        cloned = cls(other.name, other.sequential_order)
        for observation in other.observations:
            cloned.observations.append(GraphObservation.clone(observation))
        for context in other.contexts:
            cloned.contexts.append(GraphContext.clone(context))
        return cloned

    def load_observation(self, source: Observation) -> "GraphObservation":
        return GraphObservation.clone(source)

    def load_context(self, source: Context) -> "GraphContext":
        return GraphContext.clone(source)


class GraphObservation(Observation, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Observation"
