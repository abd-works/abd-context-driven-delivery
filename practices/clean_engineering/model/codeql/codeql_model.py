"""Clean Engineering types on the practice graph — wrap live CE types."""

from __future__ import annotations

from typing import List, Optional

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel as SourceModel,
    Module as SourceModule,
    OoadClass as SourceClass,
)
from practices.clean_engineering.model.operation import (
    Operation as SourceOperation,
    Parameter as SourceParameter,
)
from practices.clean_engineering.model.property import Property as SourceProperty
from practices.ddd.model.nodes import Aggregate, BoundedContext

from harness.knowledge_graph.model.graph_node import Kind, Node


class Property(SourceProperty, Node):
    practice = "clean_engineering"
    _semantic_type_name = "Property"


class Parameter(SourceParameter, Node):
    practice = "clean_engineering"
    _semantic_type_name = "Parameter"


class Operation(SourceOperation, Node):
    practice = "clean_engineering"
    _semantic_type_name = "Operation"

    def load_parameter(self, source: SourceParameter) -> Parameter:
        return Parameter(source.name, source.sequential_order, source.type_hint)

    @property
    def called_by(self) -> List["Operation"]:
        return [op for op in self.used_by if isinstance(op, Operation)]


class _Members:
    def load_property(self, source: SourceProperty) -> Property:
        return Property(
            source.name,
            source.sequential_order,
            type_hint=source.type_hint,
            description=source.description,
        )

    def load_operation(self, source: SourceOperation) -> Operation:
        node = Operation(
            source.name,
            source.sequential_order,
            return_type=source.return_type,
            description=source.description,
            callees=list(source.callees),
        )
        node._legacy_parameters = list(source._legacy_parameters)
        node.parameters = [
            Parameter(param.name, param.sequential_order, param.type_hint)
            for param in source.parameters
        ]
        return node


class OoadClass(_Members, SourceClass, Node):
    practice = "clean_engineering"
    _semantic_type_name = "OoadClass"

    def sync_tree_from_legacy(self) -> None:
        self.property_nodes = [
            Property.from_field(field, index)
            for index, field in enumerate(self.properties, start=1)
        ]
        self.operation_nodes = [
            Operation.from_field(field, index)
            for index, field in enumerate(self.operations, start=1)
        ]

    @property
    def external_classes(self) -> List["OoadClass"]:
        return [cls for cls in self.related(Kind.DEPENDS_ON) if isinstance(cls, OoadClass)]


class Module(SourceModule, Node):
    practice = "clean_engineering"
    _semantic_type_name = "Module"

    def load_class(self, source: SourceClass) -> OoadClass:
        return OoadClass(source.name, source.sequential_order)

    @property
    def external_classes(self) -> List[OoadClass]:
        return [cls for cls in self.related(Kind.DEPENDS_ON) if isinstance(cls, OoadClass)]

    @property
    def dependency_modules(self) -> List["Module"]:
        return [mod for mod in self.related(Kind.DEPENDS_ON) if isinstance(mod, Module)]

    @property
    def callers(self) -> List["Module"]:
        return [mod for mod in self.used_by if isinstance(mod, Module)]


class CleanEngineeringModel(SourceModel, Node):
    practice = "clean_engineering"
    _semantic_type_name = "CleanEngineeringModel"

    def load_module(self, source: SourceModule) -> Module:
        if isinstance(source, BoundedContext):
            from practices.ddd.model.codeql.ddd import BoundedContext as GraphBoundedContext

            return GraphBoundedContext(source.name, source.sequential_order)
        if isinstance(source, Aggregate):
            from practices.ddd.model.codeql.ddd import Aggregate as GraphAggregate

            return GraphAggregate(source.name, source.sequential_order)
        return Module(source.name, source.sequential_order)
