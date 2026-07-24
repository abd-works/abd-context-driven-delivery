"""Python code channel for the CleanEngineering model — module-first.

ONE parse surface for transform + validate: regex for design stubs, ast for
executable Python (fills Operation metrics). Scanners must not import ast
directly — call parse / parse_detailed instead.
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

from context_tools.clean_engineering.class_model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    companion_interface_name,
    is_interface_name,
)
from context_tools.clean_engineering.class_model.update_report import UpdateReport

_MODULE_MARKER = re.compile(r"^#\s*===\s*(.+?)\s*===$", re.MULTILINE)
_CLASS_PATTERN = re.compile(r'class\s+(\w+)[^:]*:\s*\n\s+"""([^"]*?)"""', re.DOTALL)
_CLASS_NAME_ONLY = re.compile(r"class\s+(\w+)")

_NESTING_TYPES = (
    ast.If,
    ast.For,
    ast.While,
    ast.AsyncFor,
    ast.Try,
    ast.With,
    ast.AsyncWith,
)


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
    def create_child_class(self, source: OoadClass) -> PythonOoadClass:
        return PythonOoadClass(name=source.name, sequential_order=source.sequential_order)


class PythonCleanEngineeringModel(CleanEngineeringModel):

    def create_child_module(self, source: Module) -> PythonModule:
        return PythonModule(name=source.name, sequential_order=source.sequential_order)

    @classmethod
    def parse(cls, text: str) -> "PythonCleanEngineeringModel":
        return cls.parse_detailed(text).model

    @classmethod
    def parse_detailed(cls, text: str) -> ParsedPython:
        """Single parse entry — prefer ast (metrics); fall back to regex stubs."""
        lines = text.split("\n")
        try:
            tree = ast.parse(text)
        except SyntaxError:
            model = cls._parse_regex(text)
            return ParsedPython(model=model, content=text, lines=lines, tree=None)
        model = cls._parse_ast(text, tree)
        return ParsedPython(model=model, content=text, lines=lines, tree=tree)

    @classmethod
    def parse_file(cls, path: Path) -> ParsedPython | None:
        if not path.is_file():
            return None
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None
        try:
            return cls.parse_detailed(content)
        except SyntaxError:
            return None

    @classmethod
    def render(cls, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        header = "from __future__ import annotations\nfrom abc import ABC, abstractmethod\n"
        parts = [header]
        for module in canonical.modules:
            if module.name:
                parts.append(f"# === {module.name} ===")
                if module.description:
                    for line in module.description.splitlines():
                        parts.append(f"# {line}" if line.strip() else "#")
                parts.append("")
            known = [c.name for c in module.classes]
            for oclass in module.classes:
                parts.append(_render_class(oclass, known_names=known))
        return "\n\n".join(parts) + "\n"

    @classmethod
    def sync(cls, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(cls.parse(text))

    @classmethod
    def _parse_regex(cls, text: str) -> "PythonCleanEngineeringModel":
        model = cls(name="", sequential_order=1)
        segments = _MODULE_MARKER.split(text)

        if len(segments) <= 1:
            module = PythonModule(name="", sequential_order=1)
            _populate_classes_regex(text, module)
            if module.classes:
                model.modules.append(module)
        else:
            module_order = 1
            for i in range(1, len(segments), 2):
                name = segments[i].strip()
                body = segments[i + 1] if i + 1 < len(segments) else ""
                module = PythonModule(name=name, sequential_order=module_order)
                _populate_classes_regex(body, module)
                model.modules.append(module)
                module_order += 1
        return model

    @classmethod
    def _parse_ast(cls, text: str, tree: ast.AST) -> "PythonCleanEngineeringModel":
        model = cls(name="", sequential_order=1)
        module = PythonModule(name="", sequential_order=1)
        class_order = 1
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            intent = ast.get_docstring(node) or ""
            oclass = PythonOoadClass(
                name=node.name,
                sequential_order=class_order,
                intent=intent.strip(),
                line=node.lineno,
            )
            name_words = set(node.name.lower().replace("_", " ").split())
            doc_words = set(intent.lower().strip(".").split()) if intent else set()
            oclass.docstring_parrots_name = bool(
                name_words and doc_words and doc_words <= name_words
            )
            oclass.operations = _operations_from_class(node)
            oclass.properties = _properties_from_class(node)
            narr, code_c = _file_comment_issues(text)
            oclass.narration_comment_lines = narr
            oclass.commented_code_lines = code_c
            module.classes.append(oclass)
            class_order += 1
        # Module-level functions as a synthetic class when no classes present
        top_ops = [
            _operation_from_function(n)
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        narr, code_c = _file_comment_issues(text)
        if top_ops and not module.classes:
            holder = PythonOoadClass(name="_module", sequential_order=1)
            holder.operations = top_ops
            holder.narration_comment_lines = narr
            holder.commented_code_lines = code_c
            module.classes.append(holder)
        elif top_ops and module.classes:
            module.classes[0].operations.extend(top_ops)
        if module.classes:
            model.modules.append(module)
        return model


def _operations_from_class(class_node: ast.ClassDef) -> list[Operation]:
    ops: list[Operation] = []
    for node in class_node.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            ops.append(_operation_from_function(node))
    return ops


def _operation_from_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> Operation:
    params = [a.arg for a in node.args.args if a.arg != "self"]
    params += [a.arg for a in node.args.kwonlyargs]
    ret = ""
    if node.returns is not None:
        ret = ast.unparse(node.returns)
    line_count = 0
    if getattr(node, "end_lineno", None) and node.lineno:
        line_count = node.end_lineno - node.lineno + 1
    bare_except_lines, swallowed_except_lines = _collect_except_issues(node)
    doc = (ast.get_docstring(node) or "").strip()
    name_words = set(node.name.lower().replace("_", " ").split())
    doc_words = set(doc.lower().strip(".").split()) if doc else set()
    return Operation(
        name=node.name,
        parameters=params,
        return_type=ret,
        description=doc,
        line=node.lineno,
        line_count=line_count,
        nesting_depth=_max_nesting(node.body, 0),
        callees=_collect_callees(node),
        literals=_collect_literals(node),
        param_count=len(params),
        has_calculation=_has_calculation(node),
        has_validation=_has_validation(node),
        bare_except_lines=bare_except_lines,
        swallowed_except_lines=swallowed_except_lines,
        assigned_names=_collect_assigned_names(node),
        loop_target_names=_collect_loop_targets(node),
        body_fingerprint=_body_fingerprint(node),
        constructed_types=_constructed_types(node),
        public_attr_assigns=_public_attr_assigns(node),
        is_property=_is_property(node),
        returns_private_attr=_returns_private_attr(node),
        magic_numbers=_magic_numbers(node),
        docstring_parrots_name=bool(name_words and doc_words and doc_words <= name_words),
    )


def _properties_from_class(class_node: ast.ClassDef) -> list[Property]:
    props: list[Property] = []
    for node in class_node.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            hint = ast.unparse(node.annotation) if node.annotation else ""
            props.append(Property(name=node.target.id, type_hint=hint))
    return props


def _max_nesting(body: list, depth: int) -> int:
    deepest = depth
    for node in body:
        if isinstance(node, _NESTING_TYPES):
            child_depth = depth + 1
            for field_name in ("body", "orelse", "handlers", "finalbody"):
                children = getattr(node, field_name, None)
                if children:
                    deepest = max(deepest, _max_nesting(children, child_depth))
        elif hasattr(node, "body") and isinstance(node.body, list):
            deepest = max(deepest, _max_nesting(node.body, depth))
    return deepest


def _collect_callees(func: ast.AST) -> list[str]:
    names: list[str] = []
    for child in ast.walk(func):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                names.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                names.append(child.func.attr)
    return names


def _collect_literals(func: ast.AST) -> list[str]:
    out: list[str] = []
    for child in ast.walk(func):
        if isinstance(child, ast.Constant) and isinstance(child.value, str):
            out.append(child.value)
    return out


_CALC_OPS = (
    ast.BinOp,
    ast.BoolOp,
    ast.Compare,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)


def _has_calculation(func: ast.AST) -> bool:
    return any(isinstance(child, _CALC_OPS) for child in ast.walk(func))


def _has_validation(func: ast.AST) -> bool:
    for child in ast.walk(func):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
            if any(
                child.func.attr.startswith(v)
                for v in ("validate", "check", "verify", "assert", "ensure")
            ):
                return True
        if isinstance(child, ast.If) and isinstance(child.test, ast.Compare):
            if any(isinstance(stmt, ast.Raise) for stmt in child.body):
                return True
    return False


def _collect_except_issues(func: ast.AST) -> tuple[list[int], list[int]]:
    bare: list[int] = []
    swallowed: list[int] = []
    for child in ast.walk(func):
        if not isinstance(child, ast.ExceptHandler):
            continue
        line = child.lineno
        if child.type is None:
            bare.append(line)
        body = child.body
        if len(body) == 1 and isinstance(body[0], ast.Pass):
            swallowed.append(line)
        elif (
            len(body) == 1
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            swallowed.append(line)
    return bare, swallowed


def _collect_assigned_names(func: ast.AST) -> list[tuple[str, int]]:
    names: list[tuple[str, int]] = []
    for child in ast.walk(func):
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            names.append((child.id, child.lineno))
        elif isinstance(child, ast.arg) and child.arg not in {"self", "cls"}:
            names.append((child.arg, getattr(child, "lineno", 0) or 0))
    return names


def _collect_loop_targets(func: ast.AST) -> list[tuple[str, int]]:
    targets: list[tuple[str, int]] = []
    for child in ast.walk(func):
        if isinstance(child, (ast.For, ast.AsyncFor)):
            if isinstance(child.target, ast.Name):
                targets.append((child.target.id, child.target.lineno))
            elif isinstance(child.target, ast.Tuple):
                for elt in child.target.elts:
                    if isinstance(elt, ast.Name):
                        targets.append((elt.id, elt.lineno))
    return targets


def _body_fingerprint(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    import hashlib

    normalized = ast.dump(ast.Module(body=node.body, type_ignores=[]))
    return hashlib.sha256(normalized.encode()).hexdigest()


def _constructed_types(func: ast.AST) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for child in ast.walk(func):
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
            if child.func.id and child.func.id[0].isupper():
                out.append((child.func.id, child.lineno))
    return out


def _public_attr_assigns(func: ast.AST) -> list[tuple[str, int]]:
    out: list[tuple[str, int]] = []
    for child in ast.walk(func):
        if not isinstance(child, ast.Assign):
            continue
        for target in child.targets:
            if (
                isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == "self"
                and not target.attr.startswith("_")
            ):
                out.append((target.attr, child.lineno))
    return out


def _is_property(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(isinstance(d, ast.Name) and d.id == "property" for d in node.decorator_list)


def _returns_private_attr(func: ast.AST) -> bool:
    for child in ast.walk(func):
        if not isinstance(child, ast.Return) or child.value is None:
            continue
        val = child.value
        if (
            isinstance(val, ast.Attribute)
            and isinstance(val.value, ast.Name)
            and val.value.id == "self"
            and val.attr.startswith("_")
        ):
            return True
    return False


def _magic_numbers(func: ast.AST) -> list[tuple[float, int]]:
    safe = {0, 1, 2, -1, 0.0, 1.0, 0.5, 100, 10, True, False, None}
    out: list[tuple[float, int]] = []
    for child in ast.walk(func):
        if isinstance(child, ast.Constant) and isinstance(child.value, (int, float)):
            if child.value not in safe:
                out.append((float(child.value), child.lineno))
    return out


def _file_comment_issues(text: str) -> tuple[list[int], list[int]]:
    import re

    narration = re.compile(
        r"^\s*#\s*(get|set|return|handle|create|init|import|increment|decrement|define|declare)\s",
        re.I,
    )
    commented = re.compile(
        r"^\s*#\s*(def |class |import |from |if |for |while |return |raise |try:)",
    )
    useful = re.compile(
        r"^\s*#\s*(TODO|FIXME|HACK|NOTE|XXX|BUG|WARN|WHY|REASON|LEGAL|LICENSE|COPYRIGHT|type:\s*ignore|noqa)",
        re.I,
    )
    narr_lines: list[int] = []
    code_lines: list[int] = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("#") or useful.match(stripped):
            continue
        if narration.match(stripped):
            narr_lines.append(i)
        elif commented.match(stripped):
            code_lines.append(i)
    return narr_lines, code_lines


def _populate_classes_regex(text: str, module: PythonModule) -> None:
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


def _render_class(oclass: OoadClass, known_names: List[str] | None = None) -> str:
    known_names = known_names or []
    iface = companion_interface_name(oclass.name, known_names)
    if is_interface_name(oclass.name):
        bases = "ABC"
    elif iface:
        bases = iface
    else:
        bases = "ABC"
    lines: List[str] = [f"class {oclass.name}({bases}):"]
    if oclass.intent:
        lines.append(f'    """{oclass.intent}"""')
        lines.append("")
    # Properties: on I{Class}, same empty-interface treatment as operations.
    for prop in oclass.properties:
        hint = prop.type_hint or "object"
        if is_interface_name(oclass.name) or not iface:
            lines.append("    @property")
            lines.append("    @abstractmethod")
            lines.append(f"    def {prop.name}(self) -> {hint}: ...")
            lines.append("")
        else:
            lines.append(f"    {prop.name}: {hint}")
    if oclass.properties and not is_interface_name(oclass.name) and iface:
        lines.append("")
    if oclass.properties and (is_interface_name(oclass.name) or not iface):
        param_sig = ", ".join(
            f"{p.name}: {p.type_hint}" if p.type_hint else p.name
            for p in oclass.properties
        )
        lines.append("    @abstractmethod")
        lines.append(f"    def __init__(self, {param_sig}) -> None: ...")
        lines.append("")
    elif oclass.properties and iface:
        param_sig = ", ".join(
            f"{p.name}: {p.type_hint}" if p.type_hint else p.name
            for p in oclass.properties
        )
        lines.append("    @abstractmethod")
        lines.append(f"    def __init__(self, {param_sig}) -> None: ...")
        lines.append("")
    for op in oclass.operations:
        params = ", ".join(op.parameters)
        ret = op.return_type or "None"
        lines.append("    @abstractmethod")
        lines.append(f"    def {op.name}(self, {params}) -> {ret}: ...")
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    # Only emit pass when the class has no members yet.
    body = [ln for ln in lines[1:] if ln.strip()]
    if not body:
        lines.append("    pass")
    return "\n".join(lines)
