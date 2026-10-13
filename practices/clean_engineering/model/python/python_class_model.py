"""Python code channel for the CleanEngineering model - module-first.

Regex covers design stubs. The ast covers executable Python. Rules read the
source themselves when the graph loads.
"""
from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    companion_interface_name,
    is_interface_name,
)
from practices.clean_engineering.model.operation import operation_body_fingerprint
from practices.clean_engineering.model.operation_metrics import apply_python_function_metrics
from practices.clean_engineering.model.update_report import UpdateReport

_MODULE_MARKER = re.compile(r"^#\s*===\s*(.+?)\s*===$", re.MULTILINE)
_CLASS_PATTERN = re.compile(r'class\s+(\w+)[^:]*:\s*\n\s+"""([^"]*?)"""', re.DOTALL)
_CLASS_NAME_ONLY = re.compile(r"class\s+(\w+)")


@dataclass
class ParsedPython:
    """Result of the single Python parse surface."""

    model: "PythonCleanEngineeringModel"
    content: str
    lines: list[str]
    tree: ast.AST | None


class PythonOoadClass(OoadClass):
    pass


class PythonModule(Module):
    def load_class(self, source: OoadClass) -> PythonOoadClass:
        return PythonOoadClass(name=source.name, sequential_order=source.sequential_order)


class PythonCleanEngineeringModel(CleanEngineeringModel):

    def load_module(self, source: Module) -> PythonModule:
        return PythonModule(name=source.name, sequential_order=source.sequential_order)

    def parse(self, text: str) -> "PythonCleanEngineeringModel":
        return self.parse_detailed(text).model

    def parse_detailed(self, text: str) -> ParsedPython:
        """Single parse entry - prefer ast (metrics); fall back to regex stubs."""
        self._text = text
        lines = text.split("\n")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            model = self._parse_regex(text)
            return ParsedPython(model=model, content=text, lines=lines, tree=None)
        model = self._parse_ast(tree)
        return ParsedPython(model=model, content=text, lines=lines, tree=tree)

    def parse_file(self, path: Path) -> ParsedPython | None:
        if not path.is_file():
            return None
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        try:
            return self.parse_detailed(content)
        except SyntaxError:
            return None

    def render(self, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        known = [loaded.name for module in canonical.modules for loaded in module.classes]
        needs_abc = any(
            is_interface_name(oclass.name) or companion_interface_name(oclass.name, known)
            for module in canonical.modules
            for oclass in module.classes
        )
        header = "from __future__ import annotations\n"
        if needs_abc:
            header += "from abc import ABC, abstractmethod\n"
        parts = [header]
        for module in canonical.modules:
            if module.name:
                parts.append(f"# === {module.name} ===")
                if module.description:
                    for line in module.description.splitlines():
                        parts.append(f"# {line}" if line.strip() else "#")
                parts.append("")
            names = [c.name for c in module.classes]
            for oclass in module.classes:
                parts.append(self._render_class(oclass, known_names=names))
        return "\n\n".join(parts) + "\n"

    def sync(self, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    def _parse_regex(self, text: str) -> "PythonCleanEngineeringModel":
        model = type(self)(name="", sequential_order=1)
        segments = _MODULE_MARKER.split(text)

        if len(segments) <= 1:
            module = PythonModule(name="", sequential_order=1)
            self._populate_classes_regex(text, module)
            if module.classes:
                model.modules.append(module)
        else:
            module_order = 1
            for i in range(1, len(segments), 2):
                name = segments[i].strip()
                body = segments[i + 1] if i + 1 < len(segments) else ""
                module = PythonModule(name=name, sequential_order=module_order)
                self._populate_classes_regex(body, module)
                model.modules.append(module)
                module_order += 1
        return model

    def _parse_ast(self, tree: ast.AST) -> "PythonCleanEngineeringModel":
        model = type(self)(name="", sequential_order=1)
        module = PythonModule(name="", sequential_order=1)
        class_order = 1
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            module.classes.append(self._class_from_ast(node, class_order))
            class_order += 1
        self._attach_top_level_ops(module, tree)
        if module.classes:
            model.modules.append(module)
        return model

    def _class_from_ast(self, node: ast.ClassDef, class_order: int) -> PythonOoadClass:
        intent = ast.get_docstring(node) or ""
        oclass = PythonOoadClass(
            name=node.name,
            sequential_order=class_order,
            intent=intent.strip(),
            line=node.lineno,
        )
        oclass.operations = self._operations_from_class(node)
        oclass.properties = self._properties_from_class(node)
        return oclass

    def _attach_top_level_ops(self, module: PythonModule, tree: ast.AST) -> None:
        top_ops = [
            self._operation_from_function(n)
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        if not top_ops:
            return
        if not module.classes:
            holder = PythonOoadClass(name="_module", sequential_order=1)
            holder.operations = top_ops
            module.classes.append(holder)
            return
        module.classes[0].operations.extend(top_ops)


    def _operations_from_class(self, class_node: ast.ClassDef) -> list[Operation]:
        ops: list[Operation] = []
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ops.append(self._operation_from_function(node))
        return ops


    def _operation_from_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Operation:
        params = [a.arg for a in node.args.args if a.arg != "self"]
        params += [a.arg for a in node.args.kwonlyargs]
        ret = ""
        if node.returns is not None:
            ret = ast.unparse(node.returns)
        doc = (ast.get_docstring(node) or "").strip()
        end_line = getattr(node, "end_lineno", None) or node.lineno
        line_count = end_line - node.lineno + 1
        constructed: list[tuple[str, int]] = []
        if node.name in {"__init__", "constructor"}:
            constructed = self._constructed_types(node)
        body_text = "\n".join(ast.unparse(stmt) for stmt in node.body)
        operation = Operation(
            name=node.name,
            parameters=params,
            return_type=ret,
            description=doc,
            line=node.lineno,
            end_line=end_line,
            line_count=line_count,
            constructed_types=constructed,
            callees=self._collect_callees(node),
            is_property=self._is_property(node),
            body_fingerprint=operation_body_fingerprint(body_text),
        )
        apply_python_function_metrics(operation, node)
        return operation

    def _constructed_types(self, func: ast.AST) -> list[tuple[str, int]]:
        found: list[tuple[str, int]] = []
        for child in ast.walk(func):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                name = child.func.id
                if name and name[0].isupper():
                    found.append((name, child.lineno))
        return found


    def _properties_from_class(self, class_node: ast.ClassDef) -> list[Property]:
        props: list[Property] = []
        for node in class_node.body:
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                hint = ast.unparse(node.annotation) if node.annotation else ""
                props.append(Property(name=node.target.id, type_hint=hint))
        return props


    def _collect_callees(self, func: ast.AST) -> list[str]:
        names: list[str] = []
        for child in ast.walk(func):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    names.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    names.append(child.func.attr)
        return names

    def _is_property(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        return any(isinstance(d, ast.Name) and d.id == "property" for d in node.decorator_list)


    def _populate_classes_regex(self, text: str, module: PythonModule) -> None:
        order = len(module.classes) + 1
        for m in _CLASS_PATTERN.finditer(text):
            oclass = PythonOoadClass(
                name=m.group(1),
                sequential_order=order,
                intent=m.group(2).strip(),
            )
            module.classes.append(oclass)
            order += 1
        if not module.classes:
            for m in _CLASS_NAME_ONLY.finditer(text):
                module.classes.append(PythonOoadClass(name=m.group(1), sequential_order=order))
                order += 1


    def _render_class(self, oclass: OoadClass, known_names: List[str] | None = None) -> str:
        self._known_names = known_names or []
        contract = is_interface_name(oclass.name)
        bases = self._bases(oclass)
        heading = f"class {oclass.name}({bases}):" if bases else f"class {oclass.name}:"
        lines: List[str] = [heading]
        if oclass.intent:
            lines.append(f'    """{oclass.intent}"""')
            lines.append("")
        self._render_properties(lines, oclass, contract)
        self._render_init(lines, oclass, contract)
        for op in oclass.operations:
            if op.name == oclass.name:
                continue
            params = ", ".join(parameter.save() for parameter in op.parameters)
            ret = op.return_type or "None"
            if contract:
                lines.append("    @abstractmethod")
            signature = f"    def {op.name}(self, {params}) -> {ret}: ..."
            lines.append(signature)
            lines.append("")
        while lines and lines[-1] == "":
            lines.pop()
        if not [ln for ln in lines[1:] if ln.strip()]:
            lines.append("    pass")
        return "\n".join(lines)

    def _bases(self, oclass: OoadClass) -> str:
        if oclass.collaborators:
            return ", ".join(oclass.collaborators)
        iface = companion_interface_name(oclass.name, self._known_names)
        if is_interface_name(oclass.name):
            return "ABC"
        if iface:
            return iface
        return ""

    def _render_properties(self, lines: List[str], oclass: OoadClass, contract: bool) -> None:
        for prop in oclass.properties:
            hint = prop.type_hint or "object"
            if contract:
                lines.append("    @property")
                lines.append("    @abstractmethod")
                lines.append(f"    def {prop.name}(self) -> {hint}: ...")
                lines.append("")
            else:
                lines.append(f"    {prop.name}: {hint}")
        if oclass.properties and not contract:
            lines.append("")

    def _render_init(self, lines: List[str], oclass: OoadClass, contract: bool) -> None:
        constructors = [op for op in oclass.operations if op.name == oclass.name]
        if constructors:
            params = constructors[0].parameters
            param_sig = ", ".join(parameter.save() for parameter in params)
        elif oclass.properties:
            param_sig = ", ".join(
                f"{p.name}: {p.type_hint}" if p.type_hint else p.name for p in oclass.properties
            )
        else:
            return
        if contract:
            lines.append("    @abstractmethod")
        lines.append(f"    def __init__(self, {param_sig}) -> None: ...")
        lines.append("")
