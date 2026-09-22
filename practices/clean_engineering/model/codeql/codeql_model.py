"""CodeQL graph types for Clean Engineering — wrap live CE types."""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

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
from practices.ddd.model.stereotypes import ddd_class_kind

from harness.knowledge_graph.model.graph_node import Kind, Node

if TYPE_CHECKING:
    from harness.knowledge_graph.model.practice_graph import PracticeGraph


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

    def accept_parameter(self, name: str) -> Optional[Parameter]:
        if not name or any(p.name == name for p in self.parameters):
            return None
        param = self.load_parameter(SourceParameter(name, len(self.parameters) + 1))
        self.parameters.append(param)
        self.graph.register(param)
        self.relate(Kind.HAS_PARAMETER, param)
        param.relate(Kind.BELONGS_TO, self)
        return param

    def invokes(self, callee: "Operation") -> None:
        self.relate(Kind.INVOKES, callee)
        caller_cls = next(iter(self.related(Kind.BELONGS_TO)), None)
        callee_cls = next(iter(callee.related(Kind.BELONGS_TO)), None)
        if caller_cls is not None and callee_cls is not None and caller_cls is not callee_cls:
            caller_cls.relate(Kind.DEPENDS_ON, callee_cls)
        caller_mod = caller_cls.home_module if caller_cls is not None else None
        callee_mod = callee_cls.home_module if callee_cls is not None else None
        if caller_mod is None or callee_mod is None or caller_mod is callee_mod:
            return
        caller_mod.relate(Kind.DEPENDS_ON, callee_mod)
        names = getattr(caller_mod, "dependencies", None)
        if names is not None and callee_mod.name not in names:
            names.append(callee_mod.name)

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
        node.legacy_parameters = list(source.legacy_parameters)
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

    def accept_property(self, name: str, type_hint: str = "") -> Optional[Property]:
        if any(p.name == name for p in self.property_nodes):
            return None
        if not self.property_nodes and self.properties:
            self.sync_tree_from_legacy()
        node = self.load_property(Property(name, len(self.property_nodes) + 1, type_hint=type_hint))
        self.property_nodes.append(node)
        self.graph.register(node)
        self.relate(Kind.OWNS, node)
        node.relate(Kind.BELONGS_TO, self)
        target = self.graph.class_named((type_hint or "").split("|")[0].strip().rstrip("[]"))
        if target is not None:
            node.relate(Kind.HAS_TYPE, target)
        return node

    def accept_operation(self, name: str, return_type: str = "", parameters=None) -> Optional[Operation]:
        if any(o.name == name for o in self.operation_nodes):
            return None
        if not self.operation_nodes and self.operations:
            self.sync_tree_from_legacy()
        node = self.load_operation(Operation(name, len(self.operation_nodes) + 1, return_type=return_type))
        node.legacy_parameters = list(parameters or [])
        if hasattr(node, "_sync_parameters_from_legacy"):
            node._sync_parameters_from_legacy()
        self.operation_nodes.append(node)
        self.graph.register(node)
        self.relate(Kind.OWNS, node)
        node.relate(Kind.BELONGS_TO, self)
        ret = self.graph.class_named((return_type or "").split("|")[0].strip().rstrip("[]"))
        if ret is not None:
            node.relate(Kind.RETURNS, ret)
        return node

    @property
    def external_classes(self) -> List["OoadClass"]:
        return [cls for cls in self.related(Kind.DEPENDS_ON) if isinstance(cls, OoadClass)]


class Module(SourceModule, Node):
    practice = "clean_engineering"
    _semantic_type_name = "Module"

    def load_class(self, source: SourceClass) -> OoadClass:
        return OoadClass(source.name, source.sequential_order)

    def accept_class(self, name: str, stereotypes: List[str] | None = None) -> OoadClass:
        from practices.ddd.model.codeql.codeql_model import ddd_graph_class_for

        decorated = name
        marks = stereotypes or []
        if marks:
            decorated = f"{name} {' '.join(f'<<{s}>>' for s in marks)}"
        stub = OoadClass(decorated, len(self.classes) + 1)
        if marks or ddd_class_kind(decorated):
            cls = ddd_graph_class_for(stub)
        else:
            cls = self.load_class(stub)
        self.classes.append(cls)
        self.graph.register(cls)
        self.relate(Kind.OWNS, cls)
        cls.relate(Kind.BELONGS_TO, self)
        return cls

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
            from practices.ddd.model.codeql.codeql_model import BoundedContext as GraphBoundedContext

            return GraphBoundedContext(source.name, source.sequential_order)
        if isinstance(source, Aggregate):
            from practices.ddd.model.codeql.codeql_model import Aggregate as GraphAggregate

            return GraphAggregate(source.name, source.sequential_order)
        return Module(source.name, source.sequential_order)

    def module_named(self, name: str, *, order: int) -> Module:
        mod = self.load_module(Module(name, order))
        self.graph.register(mod)
        self.modules.append(mod)
        self.relate(Kind.OWNS, mod)
        return mod

    @classmethod
    def ensure(
        cls,
        graph: "PracticeGraph",
        class_rows: List[dict],
        property_rows: List[dict],
        operation_rows: List[dict],
        parameter_rows: List[dict] | None = None,
    ) -> None:
        if class_rows and graph.ce_model is None:
            graph.ce_model = cls("CleanEngineering", 1)
            graph.register(graph.ce_model)
        model: CleanEngineeringModel = graph.ce_model
        modules: Dict[str, Module] = {mod.name.lower(): mod for mod in graph.nodes_of_type(Module)}
        classes: Dict[str, OoadClass] = {}
        for node in graph.nodes.values():
            if isinstance(node, OoadClass):
                classes[node.name.lower()] = node
        order = 1
        for entry in class_rows:
            module_name = entry.get("module") or ""
            name = entry.get("name") or ""
            if not name or not module_name:
                continue
            mod = modules.get(module_name.lower())
            if mod is None:
                mod = model.module_named(module_name, order=order)
                order += 1
                modules[module_name.lower()] = mod
            if name.lower() in classes:
                continue
            classes[name.lower()] = mod.accept_class(name, entry.get("stereotypes") or [])
        for prop in property_rows:
            owned = classes.get((prop.get("class_name") or "").lower())
            if owned is None:
                continue
            owned.accept_property(prop.get("name") or "", prop.get("type_hint") or "")
        for op in operation_rows:
            owned = classes.get((op.get("class_name") or "").lower())
            if owned is None:
                continue
            owned.accept_operation(
                op.get("name") or "",
                op.get("return_type") or "",
                op.get("parameters") or [],
            )
        for row in parameter_rows or []:
            owned = classes.get((row.get("class_name") or "").lower())
            if owned is None:
                continue
            operation = next((o for o in owned.operation_nodes if o.name == row.get("operation")), None)
            if operation is None:
                continue
            operation.accept_parameter(row.get("name") or "")

    @classmethod
    def wire_calls(cls, graph: "PracticeGraph", calls: List[dict]) -> None:
        seen: set[tuple] = set()
        for call in calls:
            key = (
                call.get("caller_class"),
                call.get("caller_operation"),
                call.get("callee_class"),
                call.get("callee_operation"),
            )
            if key in seen:
                continue
            seen.add(key)
            caller = graph.operation_named(call.get("caller_class") or "", call.get("caller_operation") or "")
            callee = graph.operation_named(call.get("callee_class") or "", call.get("callee_operation") or "")
            if isinstance(caller, Operation) and isinstance(callee, Operation):
                caller.invokes(callee)
