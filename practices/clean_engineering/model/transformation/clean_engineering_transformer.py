"""Clean Engineering transformation channel — wrap live CE types with Transformer."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment

from harness.transformers.transformer import Transformer
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel as SourceModel,
    Module as SourceModule,
    OoadClass as SourceClass,
)
from practices.clean_engineering.model.codeql.codeql_model import File as SourceFile
from practices.clean_engineering.model.field_types import OperationField, PropertyField, Relationship
from practices.clean_engineering.model.operation import Operation as SourceOperation
from practices.clean_engineering.model.operation import Parameter as SourceParameter
from practices.clean_engineering.model.property import Property as SourceProperty

_LENS = "ce:"
_NEXT_LENSES = ("stories:", "bdd:", "ddd:", "ux:")
_SNAKE = re.compile(r"([^0-9a-z]+)")


class CleanEngineeringTransformer(Transformer, SourceModel):
    logical_template_root = Path(__file__).resolve().parent / "logical" / "python"
    _tests_folder = "src"

    def __init__(self, name: str = "", sequential_order: int = 1) -> None:
        super().__init__(name, sequential_order)
        self.class_index: dict[str, OoadClassTransformer] = {}

    @classmethod
    def load(cls, sketch: str) -> "CleanEngineeringTransformer":
        root = cls(name="", sequential_order=1)
        _parse_ce_sketch(root, sketch)
        return root

    def children(self) -> list:
        return list(self.modules)

    def attach_environment(self, environment: Environment, root: Transformer | None = None) -> None:
        environment.filters["snake"] = _to_snake
        environment.filters["kebab"] = _to_kebab
        super().attach_environment(environment, root)


class ModuleTransformer(Transformer, SourceModule):
    _logical_template = "module"

    def __init__(self, name: str, sequential_order: int, description: str = "") -> None:
        super().__init__(name, sequential_order, description=description)
        self.files: list[FileTransformer] = []

    def children(self) -> list:
        return list(self.modules) + list(self.files) + list(self.classes)

    def _output_path(self) -> str:
        return f"{self._child_folder()}/__init__.py"

    def _child_folder(self) -> str:
        return f"{self._tests_folder}/{_to_kebab(self.name)}"


class FileTransformer(Transformer, SourceFile):
    _logical_template = "file"

    def _output_path(self) -> str:
        name = self.name if self.name.endswith(".py") else f"{_to_snake(self.name)}.py"
        return f"{self._tests_folder}/{name}"


class ImportBinding:
    def __init__(self, module: str, name: str) -> None:
        self.module = module
        self.name = name


class OoadClassTransformer(Transformer, SourceClass):
    _logical_template = "class"

    @property
    def base_imports(self) -> list[ImportBinding]:
        index = getattr(self, "class_index", {})
        bindings = []
        for rel in self.relationships:
            if rel.kind != "inheritance":
                continue
            target = index.get(rel.target)
            if target is None:
                continue
            file_module = _to_snake(rel.target)
            if target.module_name == self.module_name:
                module = f".{file_module}"
            else:
                module = f"{_to_snake(target.module_name)}.{file_module}"
            bindings.append(ImportBinding(module, rel.target))
        return bindings

    def children(self) -> list:
        return list(self.property_nodes) + list(self.operation_nodes)

    def _output_path(self) -> str:
        return f"{self._tests_folder}/{_to_snake(self.name)}.py"


class OperationTransformer(Transformer, SourceOperation):
    def children(self) -> list:
        return list(self.parameters)


class PropertyTransformer(Transformer, SourceProperty):
    pass


class ParameterTransformer(Transformer, SourceParameter):
    pass


def _to_kebab(name: str) -> str:
    return _SNAKE.sub("-", name.strip().lower()).strip("-") or "unnamed"


def _to_snake(name: str) -> str:
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return _SNAKE.sub("_", spaced.strip().lower()).strip("_") or "unnamed"


def _parse_ce_sketch(root: CleanEngineeringTransformer, sketch: str) -> None:
    stack: list[ModuleTransformer] = []
    current_class: OoadClassTransformer | None = None
    current_operation: OperationTransformer | None = None
    for raw in _lens_body(sketch).splitlines():
        indent, stripped, comment = _split_line(raw)
        if stripped.startswith("build-order:"):
            continue
        if not stripped:
            _apply_comment(stack[-1] if stack else None, current_class, comment)
            continue
        level = indent // 2
        if stripped.startswith("->"):
            _add_callee(current_operation, stripped)
            continue
        if stripped == "----":
            current_class = None
            continue
        if _is_file_line(stripped):
            _add_file(stack[-1] if stack else None, stripped)
            continue
        if current_class is None or level <= 1:
            if _is_module_line(stripped, level):
                current_class = None
                current_operation = None
                _push_module(root, stack, level, stripped, comment)
                continue
        if _is_class_name(stripped.split(":", 1)[0].strip()):
            current_operation = None
            current_class = _add_class(stack, level, stripped)
            continue
        if current_class is None:
            continue
        current_operation = _add_member(current_class, stripped)


def _push_module(
    root: CleanEngineeringTransformer,
    stack: list[ModuleTransformer],
    level: int,
    stripped: str,
    comment: str,
) -> None:
    name = stripped.rstrip("/").strip()
    while len(stack) > level:
        stack.pop()
    module = ModuleTransformer(name, _next_order(stack[-1].modules if stack else root.modules))
    module.class_index = root.class_index
    _apply_inline_seams(module, comment)
    if stack:
        stack[-1].modules.append(module)
    else:
        root.modules.append(module)
    stack.append(module)


def _add_class(
    stack: list[ModuleTransformer],
    level: int,
    stripped: str,
) -> OoadClassTransformer | None:
    if not stack:
        return None
    while len(stack) > level:
        stack.pop()
    host = stack[-1] if stack else None
    if host is None:
        return None
    name, base = _split_base(stripped)
    oclass = OoadClassTransformer(name, _next_order(host.classes))
    oclass.module_name = host.name
    oclass.class_index = host.class_index
    host.class_index[name] = oclass
    if base:
        oclass.relationships.append(Relationship(target=base, kind="inheritance"))
    host.classes.append(oclass)
    return oclass


def _add_member(oclass: OoadClassTransformer, stripped: str) -> OperationTransformer | None:
    tokens = stripped.split()
    name = tokens[0]
    if name.endswith("()"):
        name = name[:-2]
        tokens = [name, *tokens[1:]]
    if len(tokens) == 1:
        prop = PropertyTransformer(name, len(oclass.property_nodes) + 1)
        oclass.property_nodes.append(prop)
        oclass.properties.append(PropertyField(name=name))
        return None
    param_names = [] if tokens[1:] == ["()"] else tokens[1:]
    operation = OperationTransformer(name, len(oclass.operation_nodes) + 1)
    for index, param_name in enumerate(param_names, start=1):
        operation.parameters.append(ParameterTransformer(param_name, index))
    operation.legacy_parameters = list(param_names)
    oclass.operation_nodes.append(operation)
    oclass.operations.append(OperationField(name=name, parameters=list(param_names)))
    return operation


def _add_callee(operation: OperationTransformer | None, stripped: str) -> None:
    if operation is None:
        return
    callee = stripped[2:].strip()
    if callee and callee not in operation.callees:
        operation.callees.append(callee)


def _add_file(module: ModuleTransformer | None, stripped: str) -> None:
    if module is None:
        return
    name = stripped.lstrip("#").strip()
    module.files.append(FileTransformer(name, len(module.files) + 1))


def _apply_comment(
    module: ModuleTransformer | None,
    oclass: OoadClassTransformer | None,
    comment: str,
) -> None:
    if not comment:
        return
    lower = comment.lower()
    if module is not None and lower.startswith("seam:"):
        module.seam = comment.split(":", 1)[1].strip()
        return
    if module is not None and lower.startswith("constraint:"):
        module.constraint = comment.split(":", 1)[1].strip()
        return
    if module is not None and lower.startswith("dep ->"):
        dep = comment.split("->", 1)[1].strip().split()[0]
        if dep and dep not in module.dependencies:
            module.dependencies.append(dep)
        return
    if module is not None and lower.startswith("standalone:"):
        module.description = comment.split(":", 1)[1].strip()
        return
    if oclass is not None and lower.startswith("invariant:"):
        oclass.intent = comment


def _apply_inline_seams(module: ModuleTransformer, comment: str) -> None:
    if not comment or comment.lower().startswith(("seam:", "constraint:", "dep ->", "standalone:")):
        _apply_comment(module, None, comment)
        return
    terms = [part.strip() for part in comment.split(",") if part.strip()]
    module.seam_terms.extend(terms)


def _is_module_line(stripped: str, level: int) -> bool:
    if stripped.endswith("/"):
        return True
    if _is_class_name(stripped.split(":", 1)[0].strip()):
        return False
    return level <= 1


def _is_class_name(name: str) -> bool:
    return bool(name) and name[0].isupper() and "/" not in name and " " not in name


def _is_file_line(stripped: str) -> bool:
    return stripped.startswith("#") and stripped.endswith(".py")


def _split_base(stripped: str) -> tuple[str, str]:
    if ":" not in stripped:
        return stripped.strip(), ""
    name, base = stripped.split(":", 1)
    return name.strip(), base.strip()


def _next_order(items: list) -> int:
    return len(items) + 1


def _split_line(raw: str) -> tuple[int, str, str]:
    indent = len(raw) - len(raw.lstrip(" "))
    body = raw.strip()
    if "//" in body:
        code, comment = body.split("//", 1)
        return indent, code.strip(), comment.strip()
    return indent, body, ""


def _lens_body(sketch: str) -> str:
    lines = sketch.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith(_LENS)), None)
    if start is None:
        return sketch
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if any(lines[i].startswith(marker) for marker in _NEXT_LENSES):
            end = i
            break
    return "\n".join(lines[start + 1 : end])
