"""Python code channel for the CleanEngineering model - module-first.

The model is read from Python's own syntax tree, so a file that does not parse raises UnreadableSource rather than
reading as a partial or empty model. Rules read the source themselves when the graph loads.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import List, Optional

from cdd_guidance.practices.clean_engineering.model.code_body import PYTHON, CodeBody
from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    UnreadableSource,
    companion_interface_name,
    is_interface_name,
)
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.class_stereotypes import (
    ClassHead,
    DocumentedIntent,
    snake_case_decorator,
    stereotype_named,
)
from cdd_guidance.practices.clean_engineering.model.code_class_model import CodeCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import operation_body_fingerprint

_FUTURE_IMPORT = "from __future__ import annotations"
_ABC_IMPORT = "from abc import ABC, abstractmethod"


class PythonModule(Module):
    def load_source_facts(self, text: str, file: Path, root: Path) -> None:
        super().load_source_facts(text, file, root)
        tree = _syntax_tree(text)
        if tree is None:
            return
        helpers = _module_private_functions(tree)
        for function, owner in _sole_calling_class(tree, set(helpers)).items():
            for oclass in self.classes:
                if oclass.name == owner:
                    oclass.module_helpers.append([function, helpers[function]])

    def import_targets(self, text: str, file: Path, root: Path) -> list[str]:
        """Root-relative paths each `import` / `from … import` names, absolute or relative."""
        tree = _syntax_tree(text)
        if tree is None:
            return []
        package = file.parent.relative_to(root).parts
        targets: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                targets.extend(alias.name.replace(".", "/") for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                targets.extend(_from_import_targets(node, package))
        return targets


def _bare_decorator_name(decorator: ast.expr) -> str:
    """The name of a decorator written with no arguments, `@entity` or `@entity()`; empty for any other."""
    if isinstance(decorator, ast.Call) and not decorator.args and not decorator.keywords:
        decorator = decorator.func
    return decorator.id if isinstance(decorator, ast.Name) else ""


def _syntax_tree(text: str) -> ast.Module | None:
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


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


class PythonCleanEngineeringModel(CodeCleanEngineeringModel):
    language = PYTHON

    def load_module(self, source: Module) -> PythonModule:
        return PythonModule(name=source.name, sequential_order=source.sequential_order)

    def parse(self, text: str) -> "PythonCleanEngineeringModel":
        """The model the Python text declares. Text that is not valid Python raises UnreadableSource."""
        self._text = text
        try:
            tree = ast.parse(text)
        except SyntaxError as error:
            raise UnreadableSource(f"Python does not parse at line {error.lineno}: {error.msg}") from error
        return self._parse_ast(tree)

    def _parse_ast(self, tree: ast.AST) -> "PythonCleanEngineeringModel":
        model = self
        model.modules = []
        module = PythonModule(name="", sequential_order=1)
        class_order = 1
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            module.classes.append(self._class_from_ast(node, class_order))
            class_order += 1
        self._attach_top_level_ops(module, tree)
        module.preamble = self._preamble_of(tree)
        if module.classes:
            model.modules.append(module)
        return model

    def _class_from_ast(self, node: ast.ClassDef, class_order: int) -> OoadClass:
        documented = DocumentedIntent.read(ast.get_docstring(node) or "")
        oclass = OoadClass(
            name=node.name,
            sequential_order=class_order,
            intent=documented.intent,
            line=node.lineno,
        )
        oclass.stereotypes = list(dict.fromkeys(self._stereotypes_above(node) + documented.stereotypes))
        oclass.end_line = getattr(node, "end_lineno", None) or node.lineno
        oclass.bases = [ast.unparse(base) for base in node.bases]
        oclass.operations = self._operations_from_class(node)
        oclass.properties = self._properties_from_class(node)
        return oclass

    def _stereotypes_above(self, node: ast.ClassDef) -> list[str]:
        """The stereotypes a comment line above the class marks, then each decorator with no arguments."""
        first = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
        above = ClassHead.above("\n".join(self._text.split("\n")[: first - 1])).stereotypes
        return above + [stereotype_named(name) for name in map(_bare_decorator_name, node.decorator_list) if name]

    def _attach_top_level_ops(self, module: PythonModule, tree: ast.AST) -> None:
        """The file's module functions, on a `_module` holder after its classes, as every language puts them."""
        top_ops = [
            self._operation_from_function(n)
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        if not top_ops:
            return
        holder = OoadClass(name="_module", sequential_order=len(module.classes) + 1)
        holder.operations = top_ops
        module.classes.append(holder)


    def _operations_from_class(self, class_node: ast.ClassDef) -> list[Operation]:
        ops: list[Operation] = []
        for node in class_node.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                ops.append(self._operation_from_function(node))
        return ops


    def _operation_from_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Operation:
        params = self._parameter_strings(node)
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
            body=self._body_of(node),
        )
        operation.is_static = any(
            isinstance(dec, ast.Name) and dec.id == "staticmethod" for dec in node.decorator_list
        )
        operation.is_classmethod = self._is_classmethod(node)
        operation.load_python_function_facts(node)
        return operation

    def _is_classmethod(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        return any(isinstance(dec, ast.Name) and dec.id == "classmethod" for dec in node.decorator_list)

    def _body_of(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> CodeBody:
        """The statements as written, with the comments above them; the docstring stays the description."""
        statements = node.body[1:] if ast.get_docstring(node) is not None else node.body
        if not statements:
            return CodeBody()
        source = self._text
        if statements[0].lineno == node.lineno:
            return CodeBody("\n".join(ast.get_source_segment(source, stmt) or "" for stmt in statements), self.language)
        lines = source.split("\n")
        boundary = node.body[0].end_lineno if statements is not node.body else node.lineno
        start = statements[0].lineno
        while start - 1 > boundary and lines[start - 2].strip().startswith("#"):
            start -= 1
        return CodeBody("\n".join(lines[start - 1 : node.end_lineno]), self.language)

    def _preamble_of(self, tree: ast.Module) -> CodeBody:
        """Imports and constants above the first class, as written."""
        first = next((node for node in tree.body if isinstance(node, ast.ClassDef)), None)
        if first is None:
            return CodeBody()
        start = min([first.lineno] + [decorator.lineno for decorator in first.decorator_list])
        above = self._text.split("\n")[: start - 1]
        return CodeBody("\n".join(above).rstrip(), self.language)

    def _parameter_strings(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        items: list[str] = []
        receivers = {"self", "cls"} if self._is_classmethod(node) else {"self"}
        for arg in list(node.args.args) + list(node.args.kwonlyargs):
            if arg.arg in receivers:
                continue
            if arg.annotation is not None:
                items.append(f"{arg.arg}: {ast.unparse(arg.annotation)}")
            else:
                items.append(arg.arg)
        return items

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



    def file_header(self, preamble: CodeBody) -> List[str]:
        lines = preamble.lines_in(self.language, "", "") or [_FUTURE_IMPORT]
        if lines[0] != _FUTURE_IMPORT:
            lines = [_FUTURE_IMPORT, ""] + lines
        if self._needs_abc() and _ABC_IMPORT not in lines:
            lines.insert(1, _ABC_IMPORT)
        return lines

    def class_open(self, oclass: OoadClass, known_names: List[str]) -> List[str]:
        bases = ", ".join(oclass.declared_bases(known_names) or (["ABC"] if is_interface_name(oclass.name) else []))
        heading = f"class {oclass.name}({bases}):" if bases else f"class {oclass.name}:"
        lines = ["", ""] + [f"@{snake_case_decorator(item)}" for item in oclass.stereotypes] + [heading]
        if oclass.intent:
            lines.extend([f'    """{oclass.intent}"""', ""])
        return lines

    def class_close(self, has_members: bool) -> List[str]:
        return [] if has_members else ["    pass"]

    def python_type(self, hint: str) -> str:
        """A type written the way Python writes generics: `Collection<Root>` from another language is
        `Collection[Root]`, so the file reads back as Python."""
        return (hint or "").replace("<", "[").replace(">", "]")

    def property_line(self, prop: Property, contract: bool) -> List[str]:
        hint = self.python_type(prop.type_hint) or "object"
        if contract:
            return ["    @property", "    @abstractmethod", f"    def {prop.name}(self) -> {hint}: ..."]
        return [f"    {prop.name}: {hint}"]

    def constructor_lines(self, oclass: OoadClass, constructor: Optional[Operation], body: List[str]) -> List[str]:
        parameters = ", ".join(
            f"{name}: {self.python_type(hint)}" if hint else name for name, hint in self.constructor_parameters(oclass, constructor)
        )
        receiver = f"self, {parameters}" if parameters else "self"
        return [f"    def __init__({receiver}) -> None:"] + (body or ["        pass"])

    def signature(self, operation: Operation, contract: bool) -> List[str]:
        lines = [f"    @{decorator}" for decorator in self._decorators(operation, contract)]
        parameters = ", ".join(self.python_type(parameter.save()) for parameter in operation.parameters)
        receiver = self._receiver(operation)
        head = ", ".join(part for part in (receiver, parameters) if part)
        definition = f"    def {operation.name}({head}) -> {self.python_type(operation.return_type) or 'None'}:"
        if contract:
            return lines + [f"{definition} ..."]
        lines.append(definition)
        doc = self.doc_text(operation)
        if doc:
            lines.append(f'        """{doc}"""')
        return lines

    def block_close(self) -> List[str]:
        return []

    def _decorators(self, operation: Operation, contract: bool) -> List[str]:
        marks = (
            ("property", operation.is_property),
            ("staticmethod", operation.is_static),
            ("classmethod", operation.is_classmethod),
            ("abstractmethod", contract),
        )
        return [name for name, applies in marks if applies]

    def _receiver(self, operation: Operation) -> str:
        if operation.is_static:
            return ""
        return "cls" if operation.is_classmethod else "self"

    def _needs_abc(self) -> bool:
        known = [oclass.name for oclass in self.every_class()]
        return any(
            is_interface_name(oclass.name) or companion_interface_name(oclass.name, known)
            for oclass in self.every_class()
        )
