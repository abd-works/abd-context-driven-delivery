"""CodeQL graph types for Clean Engineering — wrap live CE types."""

from __future__ import annotations

from pathlib import Path
import re
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
from practices.clean_engineering.model.property import Property as SourceProperty
from practices.ddd.model.nodes import Aggregate, BoundedContext
from practices.ddd.model.stereotypes import ddd_class_kind

from practices.stories.model.source_location import SourceLocation
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
        if self._unresolved_init_call(callee):
            return
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


class File(_Members, OoadNode, Node):
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
        if location.file.endswith(".py"):
            hi = max(hi, self._python_block_end(lines, lo - 1) + 1)
        elif location.file.endswith((".ts", ".tsx", ".js", ".jsx")):
            hi = max(hi, self._brace_block_end(lines, lo - 1) + 1)
        hi = min(hi, len(lines))
        return lo, hi, "\n".join(lines[lo - 1 : hi])

    def _python_block_end(self, lines: list[str], start_index: int) -> int:
        header = lines[start_index]
        matched = re.match(r"^(\s*)(?:async\s+)?(?:class|def)\b", header)
        if not matched:
            return start_index
        indent = len(matched.group(1))
        end = self._signature_end(lines, start_index)
        for index in range(end + 1, len(lines)):
            line = lines[index]
            if line.strip() == "":
                end = index
                continue
            if len(line) - len(line.lstrip(" ")) <= indent:
                break
            end = index
        return end

    def _signature_end(self, lines: list[str], start_index: int) -> int:
        depth = 0
        for index in range(start_index, len(lines)):
            line = lines[index]
            depth += line.count("(") - line.count(")")
            if depth <= 0 and ":" in line:
                return index
        return start_index

    def _brace_block_end(self, lines: list[str], start_index: int) -> int:
        depth = 0
        seen = False
        for index in range(start_index, len(lines)):
            for ch in lines[index]:
                if ch == "{":
                    depth += 1
                    seen = True
                elif ch == "}":
                    depth -= 1
                    if seen and depth == 0:
                        return index
        return start_index


class GraphMemberRows:
    def __init__(self, classes: List[dict], properties: List[dict]) -> None:
        self.classes = classes
        self.properties = properties
        self.operations: List[dict] = []
        self.parameters: List[dict] = []


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


    def ensure(self, graph: "PracticeGraph", rows: GraphMemberRows) -> None:
        self._rows = rows
        self._graph = graph
        if graph.ce_model is None and (rows.classes or rows.properties or rows.operations):
            graph.ce_model = type(self)("CleanEngineering", 1)
            graph.register(graph.ce_model)
        self._model = graph.ce_model
        self._modules = {mod.name.lower(): mod for mod in graph.nodes_of_type(Module)}
        self._classes, self._files = self._indexed_types()
        self._order = 1
        self._span = SourceSpan(getattr(graph, "root", None))
        self._ensure_classes()
        self._ensure_properties()
        self._ensure_operations()

    def _indexed_types(self) -> tuple[Dict[str, OoadClass], Dict[str, File]]:
        classes: Dict[str, OoadClass] = {}
        files: Dict[str, File] = {}
        for node in self._graph.nodes.values():
            if isinstance(node, OoadClass):
                classes[node.name.lower()] = node
            if isinstance(node, File):
                files[node.name.replace("\\", "/").lower()] = node
        return classes, files

    def _ensure_classes(self) -> None:
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
            if name.lower() in self._classes:
                self._span.bind(self._classes[name.lower()], entry)
                continue
            self._classes[name.lower()] = mod.accept_class(name, entry.get("stereotypes") or [])
            self._span.bind(self._classes[name.lower()], entry)

    def _ensure_properties(self) -> None:
        for prop in self._rows.properties:
            owned = self._classes.get(str(prop.get("class_name") or "").replace("\\", "/").lower())
            if owned is None:
                continue
            owned.accept_property(prop.get("name") or "", prop.get("type_hint") or "")
            node = next((p for p in owned.property_nodes if p.name == (prop.get("name") or "")), None)
            if node is not None:
                self._span.bind(node, prop)

    def _ensure_operations(self) -> None:
        for op in self._rows.operations:
            owned = self._member_owner(op)
            if owned is None:
                continue
            owned.accept_operation(op.get("name") or "", op.get("return_type") or "", op.get("parameters") or [])
            node = next((o for o in owned.operation_nodes if o.name == (op.get("name") or "")), None)
            if node is not None:
                self._span.bind(node, op)
        for row in self._rows.parameters:
            owned = self._member_owner(row)
            if owned is None:
                continue
            operation = next((o for o in owned.operation_nodes if o.name == row.get("operation")), None)
            if operation is None:
                continue
            operation.accept_parameter(row.get("name") or "")
            param = next((p for p in operation.parameters if p.name == (row.get("name") or "")), None)
            if param is not None:
                self._span.bind(param, row)

    def _member_owner(self, row):
        class_name = str(row.get("class_name") or "").replace("\\", "/")
        owned = self._classes.get(class_name.lower())
        if owned is not None:
            return owned
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
            caller = graph.operation_named(call.get("caller_class") or "", call.get("caller_operation") or "")
            callee = graph.operation_named(call.get("callee_class") or "", call.get("callee_operation") or "")
            if isinstance(caller, Operation) and isinstance(callee, Operation):
                caller.invokes(callee)
