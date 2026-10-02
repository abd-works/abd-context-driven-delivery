"""Knowledge-graph channel for the Clean Engineering model."""

from __future__ import annotations

import json
from pathlib import Path

from harness.knowledge_graph.model.knowledge_graph_node import KnowledgeGraphNode
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    OoadNode,
)
from practices.clean_engineering.model.field_types import Relationship
from practices.clean_engineering.model.operation import Operation, Parameter
from practices.clean_engineering.model.property import Property
from practices.clean_engineering.model.update_report import ChildCollectionPair


class KnowledgeGraphCleanEngineeringModel(CleanEngineeringModel, KnowledgeGraphNode):
    moduleType = None

    def __init__(self, source=None) -> None:
        name = getattr(source, "name", "") if source is not None and not isinstance(source, str) else ""
        order = getattr(source, "sequential_order", 1) if source is not None and not isinstance(source, str) else 1
        CleanEngineeringModel.__init__(self, name, order)
        if source is not None and not isinstance(source, str):
            self.translate_from(source)

    def load_module(self, source: Module) -> "KnowledgeGraphModule":
        loaded = KnowledgeGraphModule(source)
        return loaded

    def save(self) -> str:
        return json.dumps(self.as_record(), indent=2)

    def load(self, path) -> "KnowledgeGraphCleanEngineeringModel":
        target = Path(path)
        if target.is_dir():
            target = target / "class-model.kg"
        if not target.is_file():
            return self
        return self.parse(target.read_text(encoding="utf-8"))

    def parse(self, text: str) -> "KnowledgeGraphCleanEngineeringModel":
        from practices.clean_engineering.model.json.json_class_model import JsonCleanEngineeringModel

        return type(self)(JsonCleanEngineeringModel().parse(text))

    def render(self, canonical=None, previous: str | None = None) -> str:
        del previous
        return (canonical or self).save()


class KnowledgeGraphModule(Module, KnowledgeGraphNode):
    classType = None

    def __init__(self, source=None) -> None:
        if source is None:
            Module.__init__(self, "", 1)
            return
        Module.__init__(self, source.name, source.sequential_order)
        self.update_self(source)

    def load_module(self, source: Module) -> "KnowledgeGraphModule":
        return KnowledgeGraphModule(source)

    def load_class(self, source: OoadClass) -> "KnowledgeGraphOoadClass":
        return KnowledgeGraphOoadClass(source)

    def child_collections(self, source: OoadNode) -> list:
        assert isinstance(source, Module)
        return [
            ChildCollectionPair(self.modules, source.modules, self.load_module),
            ChildCollectionPair(self.classes, source.classes, self.load_class),
        ]


class KnowledgeGraphOoadClass(OoadClass, KnowledgeGraphNode):
    propertyType = None
    operationType = None
    relationshipType = None

    def __init__(self, source=None) -> None:
        if source is None:
            OoadClass.__init__(self, "", 1)
            return
        OoadClass.__init__(self, source.name, source.sequential_order)
        self.update_self(source)

    def load_property_field(self, source: Property) -> "KnowledgeGraphProperty":
        return KnowledgeGraphProperty(source)

    def load_operation_field(self, source: Operation) -> "KnowledgeGraphOperation":
        return KnowledgeGraphOperation(source)

    def load_relationship(self, source: Relationship) -> "KnowledgeGraphRelationship":
        return KnowledgeGraphRelationship(source)

    def child_collections(self, source: OoadNode) -> list:
        assert isinstance(source, OoadClass)
        return [
            ChildCollectionPair(self.properties, source.properties, self.load_property_field),
            ChildCollectionPair(self.operations, source.operations, self.load_operation_field),
        ]


class KnowledgeGraphProperty(Property, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Property.__init__(
            self,
            source.name,
            source.sequential_order,
            getattr(source, "type_hint", ""),
            getattr(source, "description", ""),
        )
        self.update_self(source)


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
        Operation.__init__(
            self,
            source.name,
            source.sequential_order,
            return_type=getattr(source, "return_type", ""),
            description=getattr(source, "description", ""),
            callees=list(getattr(source, "callees", [])),
        )
        self.update_self(source)


class KnowledgeGraphParameter(Parameter, KnowledgeGraphNode):
    def __init__(self, source) -> None:
        Parameter.__init__(self, source.name, source.sequential_order, getattr(source, "type_hint", ""))


KnowledgeGraphCleanEngineeringModel.moduleType = KnowledgeGraphModule
KnowledgeGraphModule.classType = KnowledgeGraphOoadClass
KnowledgeGraphOoadClass.propertyType = KnowledgeGraphProperty
KnowledgeGraphOoadClass.operationType = KnowledgeGraphOperation
KnowledgeGraphOoadClass.relationshipType = KnowledgeGraphRelationship
