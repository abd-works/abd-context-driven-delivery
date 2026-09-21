"""Practice graph nodes — extend existing Stories, CE, DDD, and BDD model types."""

from __future__ import annotations

import re
from typing import List, Optional

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
)
from practices.stories.model.background import Background
from practices.stories.model.example import Example
from practices.stories.model.nodes import Epic, Story, StoryType, SubEpic
from practices.stories.model.scenario import Scenario
from practices.stories.model.step import Step
from practices.stories.model.story_map import StoryMap
from practices.stories.model.story_node import StoryNode

from .graph_node import GraphNodeMixin, Kind


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


# ---------------------------------------------------------------------------
# Clean Engineering
# ---------------------------------------------------------------------------


class GraphCleanEngineeringModel(CleanEngineeringModel, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "CleanEngineeringModel"

    def create_child_module(self, source: Module) -> "GraphModule":
        return GraphModule(source.name, source.sequential_order)


class GraphModule(Module, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "Module"

    def create_child_class(self, source: OoadClass) -> "GraphClass":
        return GraphClass(source.name, source.sequential_order)

    @property
    def external_classes(self) -> List["GraphClass"]:
        from .nodes import GraphClass

        return [c for c in self.related(Kind.DEPENDS_ON) if isinstance(c, GraphClass)]


class GraphClass(OoadClass, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "OoadClass"

    @property
    def home_module(self) -> GraphModule:
        owner = self.related(Kind.BELONGS_TO, direction="in")
        if not owner:
            raise RuntimeError(f"{self.name} has no owning Module")
        return owner[0]  # type: ignore[return-value]

    @property
    def external_classes(self) -> List["GraphClass"]:
        return [c for c in self.related(Kind.DEPENDS_ON) if isinstance(c, GraphClass)]


class GraphProperty(StoryNode, GraphNodeMixin):
    """Property as a first-class graph node (wraps CE Property fields)."""

    practice = "clean_engineering"
    _semantic_type_name = "Property"

    def __init__(self, prop: Property, sequential_order: int) -> None:
        super().__init__(name=prop.name, sequential_order=sequential_order)
        self.type_hint = prop.type_hint
        self.description = prop.description

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, GraphProperty)
        self.name = source.name
        self.type_hint = source.type_hint
        self.description = source.description

    def child_collections(self, source: StoryNode) -> list:
        return []


class GraphParameter(StoryNode, GraphNodeMixin):
    practice = "clean_engineering"
    _semantic_type_name = "Parameter"

    def __init__(self, name: str, type_hint: str, sequential_order: int) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.type_hint = type_hint

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, GraphParameter)
        self.name = source.name
        self.type_hint = source.type_hint

    def child_collections(self, source: StoryNode) -> list:
        return []


class GraphOperation(StoryNode, GraphNodeMixin):
    """Operation as a first-class graph node (wraps CE Operation fields)."""

    practice = "clean_engineering"
    _semantic_type_name = "Operation"

    def __init__(self, op: Operation, sequential_order: int) -> None:
        super().__init__(name=op.name, sequential_order=sequential_order)
        self.parameters = list(op.parameters)
        self.return_type = op.return_type
        self.description = op.description
        self.callees = list(op.callees)

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, GraphOperation)
        self.name = source.name
        self.parameters = list(source.parameters)
        self.return_type = source.return_type
        self.description = source.description
        self.callees = list(source.callees)

    def child_collections(self, source: StoryNode) -> list:
        return []


# ---------------------------------------------------------------------------
# DDD (specialises CE Module / Class)
# ---------------------------------------------------------------------------


class BoundedContext(GraphModule):
    practice = "ddd"
    _semantic_type_name = "BoundedContext"


class Aggregate(GraphModule):
    practice = "ddd"
    _semantic_type_name = "Aggregate"


class Entity(GraphClass):
    practice = "ddd"
    _semantic_type_name = "Entity"


class EntityRoot(Entity):
    practice = "ddd"
    _semantic_type_name = "EntityRoot"


class ValueObject(GraphClass):
    practice = "ddd"
    _semantic_type_name = "ValueObject"


class Repository(GraphClass):
    practice = "ddd"
    _semantic_type_name = "Repository"


class DomainEvent(GraphClass):
    practice = "ddd"
    _semantic_type_name = "DomainEvent"


class DomainService(GraphClass):
    practice = "ddd"
    _semantic_type_name = "DomainService"


# ---------------------------------------------------------------------------
# Stories
# ---------------------------------------------------------------------------


class GraphStoryMap(StoryMap, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "StoryMap"

    def create_child_epic(self, source: Epic) -> "GraphEpic":
        return GraphEpic(source.name, source.sequential_order)


class GraphEpic(Epic, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Epic"

    def create_child_sub_epic(self, source: SubEpic) -> "GraphSubEpic":
        return GraphSubEpic(source.name, source.sequential_order)

    def create_child_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphSubEpic(SubEpic, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "SubEpic"

    def create_child_sub_epic(self, source: SubEpic) -> "GraphSubEpic":
        return GraphSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> "GraphStory":
        return GraphStory(source.name, source.sequential_order, source.story_type)

    def create_child_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphStory(Story, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Story"

    def create_child_scenario(self, source: Scenario) -> "GraphScenario":
        return GraphScenario(source.name, source.sequential_order, source.story_name)

    def create_child_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphScenario(Scenario, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Scenario"

    def create_child_background(self, source: Background) -> "GraphBackground":
        return GraphBackground(source.name, source.sequential_order)

    def create_child_step(self, source: Step) -> "GraphStep":
        return GraphStep(
            text=source.text,
            phase=source.phase,
            sequential_order=source.sequential_order,
            is_continuation=source.is_continuation,
            concepts=list(source.concepts),
            values=list(source.values),
            actor=source.actor,
            source=source.source,
            name=source.name,
        )

    def create_child_example(self, source: Example) -> "GraphExample":
        return GraphExample(source.name, source.sequential_order, dict(source.fields), source.scope)


class GraphBackground(Background, GraphNodeMixin):
    practice = "stories"
    _semantic_type_name = "Background"

    def create_child_step(self, source: Step) -> "GraphStep":
        return GraphStep(
            text=source.text,
            phase=source.phase,
            sequential_order=source.sequential_order,
            is_continuation=source.is_continuation,
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
# BDD
# ---------------------------------------------------------------------------


class GraphDescription(StoryNode, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Description"

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.contexts: List[GraphContext] = []

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, GraphDescription)
        self.name = source.name

    def child_collections(self, source: StoryNode) -> list:
        return []


class GraphContext(StoryNode, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Context"

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)
        self.observations: List[GraphObservation] = []
        self.contexts: List[GraphContext] = []

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, GraphContext)
        self.name = source.name

    def child_collections(self, source: StoryNode) -> list:
        return []


class GraphObservation(StoryNode, GraphNodeMixin):
    practice = "bdd"
    _semantic_type_name = "Observation"

    def __init__(self, name: str, sequential_order: int = 1) -> None:
        super().__init__(name=name, sequential_order=sequential_order)

    def update_self(self, source: StoryNode) -> None:
        assert isinstance(source, GraphObservation)
        self.name = source.name

    def child_collections(self, source: StoryNode) -> list:
        return []


def is_primitive_type(type_name: str) -> bool:
    if not type_name:
        return True
    lowered = type_name.lower().strip()
    if lowered in {
        "void",
        "none",
        "null",
        "string",
        "str",
        "number",
        "int",
        "integer",
        "float",
        "double",
        "boolean",
        "bool",
        "any",
        "unknown",
        "object",
    }:
        return True
    return type_name[0].islower()


def parse_parameter(name_and_type: str) -> tuple[str, str]:
    raw = name_and_type.strip()
    if ":" in raw:
        name, type_hint = raw.split(":", 1)
        return name.strip(), type_hint.strip()
    return raw, ""


def pascal_type_names(type_hint: str) -> List[str]:
    if not type_hint or is_primitive_type(type_hint):
        return []
    names: List[str] = []
    for token in re.split(r"[\[\]|&<>,\s]+", type_hint):
        token = token.strip()
        if token and token[0].isupper():
            names.append(token)
    return names
