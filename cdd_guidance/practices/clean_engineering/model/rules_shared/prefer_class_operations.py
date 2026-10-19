"""prefer-class-operations — module-level private helpers used by one class (Python AST)."""

from __future__ import annotations

import ast
from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule


class PreferClassOperations(PracticeGraphRule):
    slug = "prefer-class-operations"
    node_types = ("Module", "Package", "OoadClass")

    def check(self, node, context) -> list[str]:
        return []

    def check_practice(self, context) -> list[tuple[str, str]]:
        if context.source_root is None:
            return []
        hits: list[tuple[str, str]] = []
        for path in sorted(context.source_root.rglob("*.py")):
            if any(part.startswith(".") or part in {"__pycache__", "node_modules"} for part in path.parts):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            module_privates = _module_private_functions(tree)
            if not module_privates:
                continue
            sole_owner = _sole_calling_class(tree, {name for name, _ in module_privates})
            relative = path.relative_to(context.source_root).as_posix()
            class_node_id = _class_node_for_file(context, relative, sole_owner.values())
            for fn_name, lineno in module_privates:
                owner = sole_owner.get(fn_name)
                if not owner:
                    continue
                target_id = class_node_id.get(owner)
                if not target_id:
                    continue
                hits.append(
                    (
                        target_id,
                        f"Module function '{fn_name}' (line {lineno}) is only used from '{owner}'. "
                        f"Move it onto '{owner}' as a method.",
                    )
                )
        return hits


def _module_private_functions(tree: ast.Module) -> list[tuple[str, int]]:
    return [
        (node.name, node.lineno)
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("_")
    ]


def _sole_calling_class(tree: ast.Module, fn_names: set[str]) -> dict[str, str]:
    class_calls: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for child in ast.walk(node):
            if (
                isinstance(child, ast.Call)
                and isinstance(child.func, ast.Name)
                and child.func.id in fn_names
            ):
                class_calls.setdefault(child.func.id, set()).add(node.name)
    return {fn: next(iter(classes)) for fn, classes in class_calls.items() if len(classes) == 1}


def _class_node_for_file(context, relative: str, class_names) -> dict[str, str]:
    out: dict[str, str] = {}
    for oclass in context.practice.nodes.get("OoadClass", []):
        if (oclass.source.file or "") != relative:
            continue
        out[oclass.name] = oclass.node_id
    return out
