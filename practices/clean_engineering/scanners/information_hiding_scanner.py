"""Scanner: `information-hiding` — public signatures don't leak internal representations.

Flags return-type and parameter-type annotations on public methods when they
expose implementation-shaped structures. Leaky patterns detected:

- `dict`, `Dict[str, Any]`, `Dict[str, object]`, plain `Dict` — untyped mapping
  as a public type usually means an internal row / payload leaking out
- `Any` as a return type — the module has not committed to a domain type
- `list`, `List` untyped — leaking a collection without saying of what
- `tuple`, `Tuple` untyped — same

Only public operations (name does not begin with `_`) on public classes
(class name does not begin with `_`) are inspected.

FP profile: MEDIUM. `dict` return types on a service layer aren't automatically
wrong; the scanner catches obvious leaks but domain judgement is still needed.
"""
from __future__ import annotations

import ast
from pathlib import Path

from module_scanner import Module, ModuleScanner

_LEAKY_UNSUBSCRIPTED_NAMES = {"Any", "dict", "Dict", "list", "List", "tuple", "Tuple"}
_LEAKY_MAPPING_ROOTS = {"dict", "Dict"}
_LEAKY_MAPPING_VALUES = {"Any", "object"}


class InformationHidingScanner(ModuleScanner):

    def scan_module(self, root: Path, module: Module) -> list:
        violations: list = []
        for file_path in module.python_files:
            tree = self.parse_python(file_path)
            if tree is None:
                continue
            for class_node in _public_classes(tree):
                for method in _public_methods(class_node):
                    violations.extend(
                        self._check_annotations(class_node, method, file_path)
                    )
        return violations

    def _check_annotations(
        self,
        class_node: ast.ClassDef,
        method: ast.FunctionDef,
        file_path: Path,
    ) -> list:
        found: list = []
        for arg in _iter_public_args(method):
            issue = _leaky(arg.annotation) if arg.annotation is not None else None
            if issue is not None:
                found.append(
                    self.violation(
                        f"Public operation '{class_node.name}.{method.name}' accepts "
                        f"'{arg.arg}: {issue}' — wrap in a domain type instead of leaking "
                        f"an internal representation.",
                        location=str(file_path),
                        line=method.lineno,
                    )
                )
        returns_issue = _leaky(method.returns) if method.returns is not None else None
        if returns_issue is not None:
            found.append(
                self.violation(
                    f"Public operation '{class_node.name}.{method.name}' returns "
                    f"'{returns_issue}' — commit to a domain type in the public signature.",
                    location=str(file_path),
                    line=method.lineno,
                )
            )
        return found


def _public_classes(tree: ast.AST) -> list[ast.ClassDef]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
    ]


def _public_methods(class_node: ast.ClassDef) -> list[ast.FunctionDef]:
    return [
        node
        for node in class_node.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    ]


def _iter_public_args(method: ast.FunctionDef):
    for arg in method.args.args:
        if arg.arg in {"self", "cls"}:
            continue
        yield arg
    yield from method.args.kwonlyargs
    yield from method.args.posonlyargs


def _leaky(annotation: ast.AST) -> str | None:
    name = _annotation_name(annotation)
    if name in _LEAKY_UNSUBSCRIPTED_NAMES and not _is_subscripted(annotation):
        return name
    if isinstance(annotation, ast.Subscript):
        root = _annotation_name(annotation.value)
        if root in _LEAKY_MAPPING_ROOTS:
            value_type = _mapping_value_type(annotation)
            if value_type in _LEAKY_MAPPING_VALUES:
                return f"{root}[..., {value_type}]"
    return None


def _annotation_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Subscript):
        return _annotation_name(node.value)
    return ""


def _is_subscripted(node: ast.AST) -> bool:
    return isinstance(node, ast.Subscript)


def _mapping_value_type(subscript: ast.Subscript) -> str:
    slice_node = subscript.slice
    if isinstance(slice_node, ast.Tuple) and len(slice_node.elts) == 2:
        return _annotation_name(slice_node.elts[1])
    return ""


if __name__ == "__main__":
    from scanners import run_scanner_main
    from module_scanner import collect_module_files

    raise SystemExit(
        run_scanner_main(
            InformationHidingScanner,
            "information-hiding",
            collect_module_files,
        )
    )
