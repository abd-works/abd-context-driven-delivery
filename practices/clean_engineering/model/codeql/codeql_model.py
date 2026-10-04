"""CodeQL graph types for Clean Engineering — wrap live CE types."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel as SourceModel,
    Module as SourceModule,
    OoadClass as SourceClass,
    OoadNode,
)
from practices.clean_engineering.model.operation import (
    Operation as SourceOperation,
    Parameter as SourceParameter,
)
from practices.clean_engineering.model.property import (
    Property as SourceProperty,
    bind_property_relationship,
)
from practices.clean_engineering.model.type_refs import domain_type_names
from practices.ddd.model.nodes import Aggregate, BoundedContext
from practices.ddd.model.stereotypes import ddd_class_kind, inferred_tactical_kind, tactical_tags

from practices.stories.model.source_location import SourceLocation
from harness.knowledge_graph.model.graph_node import Kind, Node, ownership_kind

if TYPE_CHECKING:
    from harness.knowledge_graph.model.practice_graph import PracticeGraph


class CodeQLOoadNode(Node):
    """Shared graph behavior for every CodeQL class-model type."""

    practice = "clean_engineering"

    def relate_once(self, kind: str, to: Optional[Node], cardinality: str = "") -> None:
        if to is None:
            return
        if to.node_id in {node.node_id for node in self.related(kind)}:
            return
        self.relate(kind, to, cardinality=cardinality)

    def named(self, name: str, semantic_type: str) -> Optional[Node]:
        plain = (name or "").strip()
        graph = getattr(self, "_graph", None)
        if not plain or graph is None:
            return None
        for node in graph.nodes.values():
            if getattr(node, "name", None) == plain and node.semantic_type() == semantic_type:
                return node
        return None


class Property(SourceProperty, CodeQLOoadNode):
    practice = "clean_engineering"
    _semantic_type_name = "Property"

    def load_invokes(self, callee) -> None:
        if callee is None:
            return
        self.relate_once(Kind.INVOKES, callee)

    def load_has_type(self) -> None:
        names = domain_type_names(getattr(self, "type_hint", "") or "")
        target = self.named(names[0], "OoadClass") if names else None
        if target is None and names and getattr(self, "_graph", None) is not None:
            target = self.graph.class_named(names[0])
        self.relate_once(Kind.HAS_TYPE, target)

    def load_relationship(self) -> None:
        if self.relationship is None:
            return
        owner = next(iter(self.related(Kind.BELONGS_TO)), None)
        if owner is None:
            return
        kind = ownership_kind(self.relationship.kind)
        if kind == Kind.RELATIVE:
            owner.relate_once(Kind.RELATIVE, self, cardinality=self.relationship.cardinality)
            return
        names = domain_type_names(getattr(self, "type_hint", "") or "")
        target = self.named(names[0], "OoadClass") if names else None
        if target is None and names and getattr(self, "_graph", None) is not None:
            target = self.graph.class_named(names[0])
        owner.relate_once(kind, target, cardinality=self.relationship.cardinality)


class Parameter(SourceParameter, CodeQLOoadNode):
    practice = "clean_engineering"
    _semantic_type_name = "Parameter"


class Operation(SourceOperation, CodeQLOoadNode):
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
        self.relate_once(Kind.HAS_PARAMETER, param)
        param.relate_once(Kind.BELONGS_TO, self)
        return param

    def invokes(self, callee: "Operation") -> None:
        if self._unresolved_init_call(callee):
            return
        self.relate_once(Kind.INVOKES, callee)
        caller_cls = next(iter(self.related(Kind.BELONGS_TO)), None)
        callee_cls = next(iter(callee.related(Kind.BELONGS_TO)), None)
        if caller_cls is not None and callee_cls is not None and caller_cls is not callee_cls:
            caller_cls.relate_once(Kind.DEPENDS_ON, callee_cls)
        caller_mod = caller_cls.home_module if caller_cls is not None else None
        callee_mod = callee_cls.home_module if callee_cls is not None else None
        if caller_mod is None or callee_mod is None or caller_mod is callee_mod:
            return
        caller_mod.relate_once(Kind.DEPENDS_ON, callee_mod)
        names = getattr(caller_mod, "dependencies", None)
        if names is not None and callee_mod.name not in names:
            names.append(callee_mod.name)

    def load_invokes(self, callee: "Operation") -> None:
        self.invokes(callee)

    def load_returns(self, return_type: str) -> None:
        plain = (return_type or "").split("|")[0].strip().rstrip("[]")
        target = self.named(plain, "OoadClass")
        if target is None and getattr(self, "_graph", None) is not None:
            target = self.graph.class_named(plain)
        self.relate_once(Kind.RETURNS, target)

    def _unresolved_init_call(self, callee: "Operation") -> bool:
        if self.name != "__init__" or callee.name != "__init__":
            return False
        caller_cls = next(iter(self.related(Kind.BELONGS_TO)), None)
        callee_cls = next(iter(callee.related(Kind.BELONGS_TO)), None)
        if caller_cls is None or callee_cls is None or caller_cls is callee_cls:
            return False
        callee_name = getattr(callee_cls, "name", "") or ""
        source = getattr(self, "source", None)
        text = str(getattr(source, "text", "") or "")
        if callee_name and callee_name in text:
            return False
        return True

    @property
    def called_by(self) -> List["Operation"]:
        return [op for op in self.used_by if isinstance(op, Operation)]


class _Members:
    def load_property(self, source: SourceProperty) -> Property:
        return Property.from_field(source, source.sequential_order)

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

    def accept_property(
        self,
        name: str,
        type_hint: str = "",
        stereotype: str = "",
        cardinality: str = "",
        origin: str = "",
    ) -> Optional[Property]:
        if any(p.name == name for p in self.property_nodes):
            return None
        if not self.property_nodes and self.properties:
            self.sync_tree_from_legacy()
        node = self.load_property(Property(name, len(self.property_nodes) + 1, type_hint=type_hint))
        node.stereotype = stereotype
        node.cardinality = cardinality
        node.origin = origin
        bind_property_relationship(node)
        self.property_nodes.append(node)
        self.graph.register(node)
        self.relate_once(Kind.OWNS, node)
        node.relate_once(Kind.BELONGS_TO, self)
        node._graph = self.graph
        node.load_has_type()
        node.load_relationship()
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
        self.relate_once(Kind.OWNS, node)
        node.relate_once(Kind.BELONGS_TO, self)
        node._graph = self.graph
        node.load_returns(return_type)
        return node


class OoadClass(_Members, SourceClass, CodeQLOoadNode):
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


class Module(SourceModule, CodeQLOoadNode):
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

    def accept_file(self, path: str) -> "File":
        node = File(path.replace("\\", "/"), len(self.classes) + 1)
        self.graph.register(node)
        self.relate(Kind.OWNS, node)
        node.relate(Kind.BELONGS_TO, self)
        return node

    @property
    def external_classes(self) -> List[OoadClass]:
        return [cls for cls in self.related(Kind.DEPENDS_ON) if isinstance(cls, OoadClass)]

    @property
    def dependency_modules(self) -> List["Module"]:
        return [mod for mod in self.related(Kind.DEPENDS_ON) if isinstance(mod, Module)]

    @property
    def callers(self) -> List["Module"]:
        return [mod for mod in self.used_by if isinstance(mod, Module)]


class File(_Members, OoadNode, CodeQLOoadNode):
    practice = "clean_engineering"
    _semantic_type_name = "File"

    def __init__(self, name: str, sequential_order: int) -> None:
        OoadNode.__init__(self, name, sequential_order)
        self.property_nodes: List[Property] = []
        self.operation_nodes: List[Operation] = []
        self.properties: List = []
        self.operations: List = []

    def sync_tree_from_legacy(self) -> None:
        return

    def update_self(self, source: OoadNode) -> None:
        self.name = source.name

    def child_collections(self, source: OoadNode):
        return []


class SourceSpan:
    def __init__(self, root: Path | None) -> None:
        self._root = root

    def bind(self, node: Node, row: dict) -> None:
        file = str(row.get("file") or "").replace("\\", "/")
        start = int(row.get("line") or 0)
        end = int(row.get("end_line") or start)
        if not file:
            return
        text = str(row.get("text") or "")
        location = SourceLocation(file=file, line=start, end_line=end or start, text=text)
        if self._root is not None and start > 0:
            location = self.read(location)
        node.source = location

    def read(self, location: SourceLocation) -> SourceLocation:
        start, end, text = self._read_span(location)
        if not text:
            return SourceLocation(
                file=location.file,
                line=location.line,
                end_line=location.end_line or location.line,
                text=location.text,
            )
        return SourceLocation(file=location.file, line=start, end_line=end, text=text)

    def _read_span(self, location: SourceLocation) -> tuple[int, int, str]:
        path = Path(self._root) / location.file
        if not path.is_file():
            return location.line, location.end_line or location.line, ""
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        lo = max(location.line, 1)
        hi = max(location.end_line or lo, lo)
        if lo > len(lines):
            return lo, hi, ""
        hi = min(hi, len(lines))
        return lo, hi, "\n".join(lines[lo - 1 : hi])


class GraphMemberRows:
    def __init__(self, classes: List[dict], properties: List[dict]) -> None:
        self.classes = classes
        self.properties = properties
        self.operations: List[dict] = []
        self.parameters: List[dict] = []


class CleanEngineeringModel(SourceModel, CodeQLOoadNode):
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


    def save(self) -> str:
        return ""

    @classmethod
    def load_content(cls, database) -> "CleanEngineeringModel":
        """One run over the database, through CodeQL.populate."""
        from pathlib import Path

        from harness.knowledge_graph.model.codeql import CodeQL
        from harness.knowledge_graph.model.practice_graph import PracticeGraph

        root = Path(database)
        graph = PracticeGraph(root)
        CodeQL(root).populate(graph, database=root)
        return graph.ce_model

    def ensure(self, graph: "PracticeGraph", rows: GraphMemberRows) -> None:
        self._rows = rows
        self._graph = graph
        if graph.ce_model is None and (rows.classes or rows.properties or rows.operations):
            graph.ce_model = type(self)("CleanEngineering", 1)
            graph.register(graph.ce_model)
        self._model = graph.ce_model
        self._modules = self._indexed_modules()
        self._classes, self._files = self._indexed_types()
        self._order = 1
        self._span = SourceSpan(getattr(graph, "root", None))
        self._ensure_classes()
        self._ensure_properties()
        self._ensure_operations()

    def _indexed_modules(self) -> Dict[str, Module]:
        indexed: Dict[str, Module] = {}
        for mod in self._graph.nodes_of_type(Module):
            indexed[mod.name.lower()] = mod
            folder = str(getattr(mod, "folder", "") or "").replace("\\", "/").strip("/")
            if not folder:
                continue
            indexed[folder.lower()] = mod
            indexed[folder.replace("/", ".").lower()] = mod
        return indexed

    def _indexed_types(self) -> tuple[Dict[str, List[OoadClass]], Dict[str, File]]:
        classes: Dict[str, List[OoadClass]] = {}
        files: Dict[str, File] = {}
        for node in self._graph.nodes.values():
            if node.semantic_type() in {
                "OoadClass",
                "Entity",
                "EntityRoot",
                "ValueObject",
                "Repository",
                "DomainEvent",
                "DomainService",
                "Specification",
            }:
                classes.setdefault(node.name.lower(), []).append(node)
            if isinstance(node, File):
                files[node.name.replace("\\", "/").lower()] = node
        return classes, files

    def _remember_class(self, name: str, node: OoadClass) -> None:
        bucket = self._classes.setdefault(name.lower(), [])
        if node not in bucket:
            bucket.append(node)

    def _class_in_file(self, row: dict) -> Optional[OoadClass]:
        name = str(row.get("name") or "").replace("\\", "/").split("/")[-1].lower()
        file_name = str(row.get("file") or "").replace("\\", "/")
        for node in self._classes.get(name, []):
            if file_name and self._node_file(node) == file_name:
                return node
        return None

    def _class_for(self, row: dict, *, name_key: str = "class_name") -> Optional[OoadClass]:
        name = str(row.get(name_key) or "").replace("\\", "/").split("/")[-1].lower()
        hits = self._classes.get(name, [])
        file_name = str(row.get("file") or "").replace("\\", "/")
        for node in hits:
            if file_name and self._node_file(node) == file_name:
                return node
        if len(hits) == 1 and (not file_name or not self._node_file(hits[0])):
            return hits[0]
        return None

    def _node_file(self, node) -> str:
        source = getattr(node, "source", None)
        return str(getattr(source, "file", "") or "").replace("\\", "/")

    def _ensure_classes(self) -> None:
        names = {str(entry.get("name") or "") for entry in self._rows.classes if entry.get("name")}
        for entry in self._rows.classes:
            module_name = entry.get("module") or ""
            name = entry.get("name") or ""
            if not name or not module_name:
                continue
            mod = self._modules.get(module_name.lower())
            if mod is None:
                mod = self._model.module_named(module_name, order=self._order)
                self._order += 1
                self._modules[module_name.lower()] = mod
            if not getattr(mod, "folder", None):
                mod.folder = module_name.replace(".", "/")
            existing = self._class_in_file(entry)
            if existing is not None:
                self._span.bind(existing, entry)
                continue
            kind = inferred_tactical_kind(name, names)
            marks = list(entry.get("stereotypes") or []) or tactical_tags(kind or "")
            created = mod.accept_class(name, marks)
            self._remember_class(name, created)
            self._span.bind(created, entry)
        self._ensure_bounded_contexts()

    def _ensure_bounded_contexts(self) -> None:
        from practices.ddd.model.codeql.codeql_model import Aggregate, BoundedContext

        kinds = {
            "Entity",
            "EntityRoot",
            "ValueObject",
            "Repository",
            "DomainEvent",
            "DomainService",
            "Specification",
        }
        contexts: dict[str, BoundedContext] = {}
        grouped: dict[str, dict] = {}
        for node in list(self._graph.nodes.values()):
            if node.semantic_type() not in kinds:
                continue
            module = next(
                (
                    owner
                    for owner in node.related(Kind.BELONGS_TO)
                    if owner.semantic_type() == "Module"
                ),
                None,
            )
            folder = str(getattr(module, "folder", "") or getattr(module, "name", "") or "").replace(
                "\\", "/"
            )
            parts = [part for part in folder.split("/") if part]
            if parts and parts[0] in {"src", "domain"} and len(parts) > 1:
                bc_name = parts[1]
            else:
                bc_name = parts[-1] if parts else "Domain"
            folder_key = "/".join(parts).lower() if parts else bc_name.lower()
            bucket = grouped.get(folder_key)
            if bucket is None:
                bucket = {"bc_name": bc_name, "parts": parts, "nodes": []}
                grouped[folder_key] = bucket
            bucket["nodes"].append(node)
        for folder_key, bucket in grouped.items():
            bc_name = bucket["bc_name"]
            parts = bucket["parts"]
            nodes = bucket["nodes"]
            key = bc_name.lower()
            context = contexts.get(key)
            if context is None:
                context = BoundedContext(bc_name.replace("-", " ").title(), len(contexts) + 1)
                self._graph.register(context)
                contexts[key] = context
            roots = [node for node in nodes if node.semantic_type() == "EntityRoot"]
            owner = context
            if roots:
                label = (parts[-1] if parts else bc_name).replace("-", " ").title()
                aggregate = Aggregate(label, len(context.aggregates) + 1)
                aggregate.root = roots[0]
                self._graph.register(aggregate)
                context.relate(Kind.OWNS, aggregate)
                context.aggregates.append(aggregate)
                owner = aggregate
            for node in nodes:
                if node.node_id not in {item.node_id for item in owner.related(Kind.OWNS)}:
                    owner.relate(Kind.OWNS, node)


    def _owned_member(self, owner, collection: str, name: str):
        return next((node for node in getattr(owner, collection, []) if node.name == name), None)

    def _keep_on_graph(self, owner, node) -> None:
        if node is None or getattr(node, "_graph", None) is not None:
            return
        self._graph.register(node)
        if hasattr(owner, "relate_once"):
            owner.relate_once(Kind.OWNS, node)
        else:
            owner.relate(Kind.OWNS, node)
        node.relate(Kind.BELONGS_TO, owner)

    def _ensure_properties(self) -> None:
        for prop in self._rows.properties:
            owned = self._class_for(prop)
            if owned is None:
                continue
            name = prop.get("name") or ""
            if hasattr(owned, "accept_property"):
                owned.accept_property(
                    name,
                    prop.get("type_hint") or "",
                    prop.get("stereotype") or "",
                    prop.get("cardinality") or "",
                    prop.get("origin") or "",
                )
            node = self._owned_member(owned, "property_nodes", name)
            if node is None:
                node = Property(name, len(getattr(owned, "property_nodes", [])) + 1, type_hint=prop.get("type_hint") or "")
                if hasattr(owned, "property_nodes"):
                    owned.property_nodes.append(node)
            self._keep_on_graph(owned, node)
            self._span.bind(node, prop)

    def _ensure_operations(self) -> None:
        for op in self._rows.operations:
            owned = self._member_owner(op)
            if owned is None:
                continue
            name = op.get("name") or ""
            if hasattr(owned, "accept_operation"):
                owned.accept_operation(name, op.get("return_type") or "", op.get("parameters") or [])
            node = self._owned_member(owned, "operation_nodes", name)
            if node is None:
                node = Operation(name, len(getattr(owned, "operation_nodes", [])) + 1, return_type=op.get("return_type") or "")
                if hasattr(owned, "operation_nodes"):
                    owned.operation_nodes.append(node)
            self._keep_on_graph(owned, node)
            self._span.bind(node, op)
        for row in self._rows.parameters:
            owned = self._member_owner(row)
            if owned is None:
                continue
            operation = self._owned_member(owned, "operation_nodes", row.get("operation") or "")
            if operation is None or not hasattr(operation, "accept_parameter"):
                continue
            operation.accept_parameter(row.get("name") or "")
            param = next((p for p in operation.parameters if p.name == (row.get("name") or "")), None)
            if param is not None:
                self._span.bind(param, row)

    def _member_owner(self, row):
        owned = self._class_for(row)
        if owned is not None:
            return owned
        class_name = str(row.get("class_name") or "").replace("\\", "/")
        if "/" not in class_name and not class_name.endswith(".py"):
            return None
        key = class_name.lower()
        if key not in self._files:
            file_path = str(row.get("file") or class_name).replace("\\", "/")
            self._files[key] = self._module_for_path(file_path).accept_file(file_path)
            self._span.bind(self._files[key], {"file": file_path, "line": 1, "end_line": 1})
        return self._files[key]

    def _module_for_path(self, path: str):
        normalized = path.replace("\\", "/")
        matches = [
            mod
            for mod in self._modules.values()
            if normalized == mod.name.replace(".", "/")
            or normalized.startswith(mod.name.replace(".", "/") + "/")
            or normalized.startswith(mod.name + "/")
        ]
        if matches:
            return max(matches, key=lambda mod: len(mod.name))
        folder = str(Path(normalized).parent).replace("\\", "/")
        if folder in (".", ""):
            folder = normalized
        key = folder.lower()
        if key not in self._modules:
            self._modules[key] = self._model.module_named(folder, order=self._order)
            self._order += 1
        return self._modules[key]

    def wire_calls(self, graph: "PracticeGraph", calls: List[dict]) -> None:
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
            caller = self._member_named(
                graph, call.get("caller_class") or "", call.get("caller_operation") or ""
            )
            callee = self._member_named(
                graph, call.get("callee_class") or "", call.get("callee_operation") or ""
            )
            if caller is not None and callee is not None and caller is not callee and hasattr(caller, "load_invokes"):
                caller.load_invokes(callee)

    def _member_named(self, graph, owner_name: str, member_name: str):
        owner = graph.class_named(owner_name)
        if owner is None:
            wanted = (owner_name or "").lower()
            for node in graph.nodes.values():
                if node.semantic_type() == "OoadClass" and node.name.lower() == wanted:
                    owner = node
                    break
        if owner is None:
            return None
        for kind in ("Operation", "Property"):
            for node in owner.related(Kind.OWNS):
                if node.semantic_type() == kind and node.name == member_name:
                    return node
        return None
