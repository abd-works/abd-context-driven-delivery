"""Python code channel for the CleanEngineering model - module-first.

The model is read from Python's own syntax tree, so a file that does not parse raises UnreadableSource rather than
reading as a partial or empty model. Each Python class, property, and operation spells its own lines, and an operation
reads its own function from the tree.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    Module,
    UnreadableSource,
    companion_interface_name,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import (
    ClassHead,
    DocumentedIntent,
    snake_case_decorator,
    stereotype_named,
)
from cdd_guidance.practices.clean_engineering.model.code_body import PYTHON, CodeBody
from cdd_guidance.practices.clean_engineering.model.code_class_model import (
    CodeClass,
    CodeCleanEngineeringModel,
    CodeModule,
    CodeOperation,
    CodeProperty,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation, operation_body_fingerprint
from cdd_guidance.practices.clean_engineering.model.operation_metrics import PythonFunctionBody

_FUTURE_IMPORT = "from __future__ import annotations"
_ABC_IMPORT = "from abc import ABC, abstractmethod"


def python_type(hint: str) -> str:
    """A type written the way Python writes generics: `Collection<Root>` from another language is `Collection[Root]`,
    so the file reads back as Python."""
    return (hint or "").replace("<", "[").replace(">", "]")
Function = ast.FunctionDef | ast.AsyncFunctionDef


class PythonProperty(CodeProperty):
    language = PYTHON

    @classmethod
    def from_annotation(cls, node: ast.AnnAssign, order: int) -> "PythonProperty":
        """The field an annotated assignment in a class body declares."""
        prop = cls(name=node.target.id, sequential_order=order, type_hint=ast.unparse(node.annotation) if node.annotation else "")
        prop.line = node.lineno
        return prop

    def lines(self, contract: bool) -> List[str]:
        hint = python_type(self.type_hint) or "object"
        if contract:
            return ["    @property", "    @abstractmethod", f"    def {self.name}(self) -> {hint}: ..."]
        return [f"    {self.name}: {hint}"]


class PythonOperation(CodeOperation):
    language = PYTHON

    @classmethod
    def from_function(cls, node: Function, text: str) -> "PythonOperation":
        """The operation a function in text declares: its signature, its body as written, and what the rules measure
        in it, read from its own syntax tree."""
        end_line = getattr(node, "end_lineno", None) or node.lineno
        is_classmethod = _decorated(node, "classmethod")
        operation = cls(
            name=node.name,
            parameters=_parameter_strings(node, is_classmethod),
            return_type=ast.unparse(node.returns) if node.returns is not None else "",
            description=(ast.get_docstring(node) or "").strip(),
            line=node.lineno,
            end_line=end_line,
            line_count=end_line - node.lineno + 1,
            constructed_types=_constructed_types(node) if node.name in {"__init__", "constructor"} else [],
            callees=_callees(node),
            is_property=_decorated(node, "property"),
            body_fingerprint=operation_body_fingerprint("\n".join(ast.unparse(stmt) for stmt in node.body)),
            body=_body_of(node, text),
        )
        operation.is_static = _decorated(node, "staticmethod")
        operation.is_classmethod = is_classmethod
        operation.measure(PythonFunctionBody(node))
        return operation

    def measure(self, function: PythonFunctionBody) -> None:
        """Keep what the rules measure on its function."""
        self.max_control_flow_depth = function.control_flow_depth()
        self.has_bare_catch, self.swallows_exceptions = function.except_flags()
        self.unnamed_literal_numbers = function.unnamed_numbers()
        self.narrative_comment_lines = 0
        self.peer_private_access = function.reaches_peer_private()
        self.packed_parameters = function.packed_parameters()

    def signature(self, contract: bool) -> List[str]:
        lines = [f"    @{decorator}" for decorator in self._decorators(contract)]
        parameters = ", ".join(python_type(parameter.save()) for parameter in self.parameters)
        head = ", ".join(part for part in (self._receiver(), parameters) if part)
        definition = f"    def {self.name}({head}) -> {python_type(self.return_type) or 'None'}:"
        if contract:
            return lines + [f"{definition} ..."]
        lines.append(definition)
        doc = self.doc_text()
        if doc:
            lines.append(f'        """{doc}"""')
        return lines

    def _decorators(self, contract: bool) -> List[str]:
        marks = (
            ("property", self.is_property),
            ("staticmethod", self.is_static),
            ("classmethod", self.is_classmethod),
            ("abstractmethod", contract),
        )
        return [name for name, applies in marks if applies]

    def _receiver(self) -> str:
        if self.is_static:
            return ""
        return "cls" if self.is_classmethod else "self"


class PythonClass(CodeClass):
    language = PYTHON
    property_type = PythonProperty
    operation_type = PythonOperation

    def opening(self, known_names: List[str]) -> List[str]:
        bases = ", ".join(self.declared_bases(known_names) or (["ABC"] if self.is_contract else []))
        heading = f"class {self.name}({bases}):" if bases else f"class {self.name}:"
        lines = ["", ""] + [f"@{snake_case_decorator(item)}" for item in self.stereotypes] + [heading]
        if self.intent:
            lines.extend([f'    """{self.intent}"""', ""])
        return lines

    def closing(self, has_members: bool) -> List[str]:
        return [] if has_members else ["    pass"]

    def block_close(self) -> List[str]:
        return []

    def constructor_lines(self, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(f"{name}: {python_type(hint)}" if hint else name for name, hint in self.constructor_parameters(constructor))
        receiver = f"self, {parameters}" if parameters else "self"
        return [f"    def __init__({receiver}) -> None:"] + (body or ["        pass"])


class PythonModule(CodeModule):
    """A Python file's module. It keeps the syntax tree its file was read into, so its imports are read from that tree."""

    class_type = PythonClass

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.tree: ast.Module | None = None

    def keep_tree(self, tree: ast.Module) -> None:
        """Keep the file's syntax tree, and give each class the private module functions only it calls."""
        self.tree = tree
        helpers = _module_private_functions(tree)
        for function, owner in _sole_calling_class(tree, set(helpers)).items():
            for oclass in self.classes:
                if oclass.name == owner:
                    oclass.module_helpers.append([function, helpers[function]])

    def import_targets(self, file: Path, root: Path) -> list[str]:
        """Root-relative paths each `import` / `from … import` names, absolute or relative."""
        if self.tree is None:
            return []
        package = file.parent.relative_to(root).parts
        targets: list[str] = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                targets.extend(alias.name.replace(".", "/") for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                targets.extend(_from_import_targets(node, package))
        return targets


class PythonCleanEngineeringModel(CodeCleanEngineeringModel):
    language = PYTHON
    module_type = PythonModule
    suffixes = (".py",)

    def parse(self, text: str) -> "PythonCleanEngineeringModel":
        """The model the Python text declares. Text that is not valid Python raises UnreadableSource."""
        self._text = text
        try:
            tree = ast.parse(text)
        except SyntaxError as error:
            raise UnreadableSource(f"Python does not parse at line {error.lineno}: {error.msg}") from error
        self.modules = []
        module = PythonModule(name="", sequential_order=1)
        for order, node in enumerate((item for item in tree.body if isinstance(item, ast.ClassDef)), start=1):
            module.classes.append(self._class_from_ast(node, order))
        self._attach_top_level_ops(module, tree)
        module.preamble = self._preamble_of(tree)
        module.keep_tree(tree)
        module.take_lines(text)
        self._file_module = module
        if module.classes:
            self.modules.append(module)
        return self

    def _class_from_ast(self, node: ast.ClassDef, class_order: int) -> PythonClass:
        documented = DocumentedIntent.read(ast.get_docstring(node) or "")
        oclass = PythonClass(name=node.name, sequential_order=class_order, intent=documented.intent, line=node.lineno)
        oclass.stereotypes = list(dict.fromkeys(self._stereotypes_above(node) + documented.stereotypes))
        oclass.end_line = getattr(node, "end_lineno", None) or node.lineno
        oclass.bases = [ast.unparse(base) for base in node.bases]
        oclass.operations = [
            PythonOperation.from_function(child, self._text) for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        fields = [child for child in node.body if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name)]
        oclass.properties = [PythonProperty.from_annotation(child, order) for order, child in enumerate(fields, start=1)]
        return oclass

    def _stereotypes_above(self, node: ast.ClassDef) -> list[str]:
        """The stereotypes a comment line above the class marks, then each decorator with no arguments."""
        first = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
        above = ClassHead.above("\n".join(self._text.split("\n")[: first - 1])).stereotypes
        return above + [stereotype_named(name) for name in map(_bare_decorator_name, node.decorator_list) if name]

    def _attach_top_level_ops(self, module: PythonModule, tree: ast.Module) -> None:
        """The file's module functions, on a `_module` holder after its classes, as every language puts them."""
        top_ops = [PythonOperation.from_function(n, self._text) for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        if not top_ops:
            return
        holder = PythonClass(name="_module", sequential_order=len(module.classes) + 1, line=1)
        holder.end_line = 1
        holder.operations = top_ops
        module.classes.append(holder)

    def _preamble_of(self, tree: ast.Module) -> CodeBody:
        """Imports and constants above the first class, as written."""
        first = next((node for node in tree.body if isinstance(node, ast.ClassDef)), None)
        if first is None:
            return CodeBody()
        start = min([first.lineno] + [decorator.lineno for decorator in first.decorator_list])
        above = self._text.split("\n")[: start - 1]
        return CodeBody("\n".join(above).rstrip(), self.language)

    def file_header(self, preamble: CodeBody) -> List[str]:
        lines = preamble.lines_in(self.language, "", "") or [_FUTURE_IMPORT]
        if lines[0] != _FUTURE_IMPORT:
            lines = [_FUTURE_IMPORT, ""] + lines
        if self._needs_abc() and _ABC_IMPORT not in lines:
            lines.insert(1, _ABC_IMPORT)
        return lines

    def _needs_abc(self) -> bool:
        known = [oclass.name for oclass in self.every_class()]
        return any(
            is_interface_name(oclass.name) or companion_interface_name(oclass.name, known)
            for oclass in self.every_class()
        )


def _decorated(node: Function, name: str) -> bool:
    return any(isinstance(decorator, ast.Name) and decorator.id == name for decorator in node.decorator_list)


def _parameter_strings(node: Function, is_classmethod: bool) -> list[str]:
    items: list[str] = []
    receivers = {"self", "cls"} if is_classmethod else {"self"}
    for arg in list(node.args.args) + list(node.args.kwonlyargs):
        if arg.arg in receivers:
            continue
        items.append(f"{arg.arg}: {ast.unparse(arg.annotation)}" if arg.annotation is not None else arg.arg)
    return items


def _body_of(node: Function, source: str) -> CodeBody:
    """The statements as written, with the comments above them; the docstring stays the description."""
    statements = node.body[1:] if ast.get_docstring(node) is not None else node.body
    if not statements:
        return CodeBody()
    if statements[0].lineno == node.lineno:
        return CodeBody("\n".join(ast.get_source_segment(source, stmt) or "" for stmt in statements), PYTHON)
    lines = source.split("\n")
    boundary = node.body[0].end_lineno if statements is not node.body else node.lineno
    start = statements[0].lineno
    while start - 1 > boundary and lines[start - 2].strip().startswith("#"):
        start -= 1
    return CodeBody("\n".join(lines[start - 1 : node.end_lineno]), PYTHON)


def _constructed_types(func: ast.AST) -> list[tuple[str, int]]:
    return [
        (child.func.id, child.lineno)
        for child in ast.walk(func)
        if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id and child.func.id[0].isupper()
    ]


def _callees(func: ast.AST) -> list[str]:
    names: list[str] = []
    for child in ast.walk(func):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                names.append(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                names.append(child.func.attr)
    return names


def _bare_decorator_name(decorator: ast.expr) -> str:
    """The name of a decorator written with no arguments, `@entity` or `@entity()`; empty for any other."""
    if isinstance(decorator, ast.Call) and not decorator.args and not decorator.keywords:
        decorator = decorator.func
    return decorator.id if isinstance(decorator, ast.Name) else ""


def _from_import_targets(node: ast.ImportFrom, package: tuple[str, ...]) -> list[str]:
    base = list(package[: len(package) - node.level + 1]) if node.level else []
    module = base + (node.module.split(".") if node.module else [])
    if not module:
        return []
    joined = "/".join(module)
    return [joined] + [f"{joined}/{alias.name}" for alias in node.names if alias.name != "*"]


def _module_private_functions(tree: ast.Module) -> dict[str, int]:
    return {
        node.name: node.lineno
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("_")
    }


def _sole_calling_class(tree: ast.Module, function_names: set[str]) -> dict[str, str]:
    callers: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name) and child.func.id in function_names:
                callers.setdefault(child.func.id, set()).add(node.name)
    return {function: next(iter(classes)) for function, classes in callers.items() if len(classes) == 1}
