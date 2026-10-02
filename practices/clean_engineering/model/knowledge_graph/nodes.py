"""Knowledge-graph channel for the Clean Engineering model."""

from __future__ import annotations

from harness.knowledge_graph.model.knowledge_graph_node import KnowledgeGraphNode
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from practices.clean_engineering.model.field_types import Relationship
from practices.clean_engineering.model.operation import Operation, Parameter
from practices.clean_engineering.model.property import Property


class KnowledgeGraphCleanEngineeringModel(CleanEngineeringModel, KnowledgeGraphNode):
    moduleType = None

    def __init__(self, source=None) -> None:
        CleanEngineeringModel.__init__(self, getattr(source, "name", ""), getattr(source, "sequential_order", 1))

    def save(self) -> str:
        return ""

    def load(self, path) -> "KnowledgeGraphCleanEngineeringModel":
        return self

    def parse(self, text: str) -> "KnowledgeGraphCleanEngineeringModel":
        return self

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphModule(Module, KnowledgeGraphNode):
    classType = None

    def __init__(self, source) -> None:
        Module.__init__(self, source.name, source.sequential_order)


class KnowledgeGraphOoadClass(OoadClass, KnowledgeGraphNode):
    propertyType = None
    operationType = None
    relationshipType = None

    def __init__(self, source) -> None:
        OoadClass.__init__(self, source.name, source.sequential_order)


class KnowledgeGraphProperty(Property, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Property.__init__(self, source.name)


class KnowledgeGraphRelationship(Relationship, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Relationship.__init__(
            self,
            source.target,
            source.kind,
            source.cardinality,
            source.description,
            source.sequential_order,
        )


class KnowledgeGraphOperation(Operation, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Operation.__init__(self, source.name)


class KnowledgeGraphParameter(Parameter, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Parameter.__init__(self, source.name)


KnowledgeGraphCleanEngineeringModel.moduleType = KnowledgeGraphModule
KnowledgeGraphModule.classType = KnowledgeGraphOoadClass
KnowledgeGraphOoadClass.propertyType = KnowledgeGraphProperty
KnowledgeGraphOoadClass.operationType = KnowledgeGraphOperation
KnowledgeGraphOoadClass.relationshipType = KnowledgeGraphRelationship
