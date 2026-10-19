"""Practice-wide checks (imports, module depth) — not tied to one Operation field."""

from __future__ import annotations

import ast
from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule

_MAX_SIBLING_IMPORTS = 8
_MAX_SHALLOW_CLASSES = 5


class OneWayDeps(PracticeGraphRule):
    slug = "one-way-deps"
    node_types = ("Module", "Package")

    def check(self, node, context) -> list[str]:
        return []

    def check_practice(self, context) -> list[tuple[str, str]]:
        if context.source_root is None:
            return []
        hits: list[tuple[str, str]] = []
        modules = _python_modules(context.source_root)
        graph = _import_graph(modules)
        for cycle in _find_cycles(graph):
            if len(cycle) < 2:
                continue
            a, b = cycle[0], cycle[1]
            node_id = _module_node_id(context, a)
            if node_id:
                hits.append(
                    (
                        node_id,
                        f"Circular import between '{a}' and '{b}' breaks one-way dependencies.",
                    )
                )
            break
        return hits


class LowCoupling(PracticeGraphRule):
    slug = "low-coupling"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        folder = context.module_folder(node)
        if folder is None or context.source_root is None:
            return []
        sibling_names = _sibling_module_names(folder)
        if not sibling_names:
            return []
        imported: set[str] = set()
        for path in folder.rglob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            for item in ast.walk(tree):
                imported.update(_imported_sibling_names(item, sibling_names))
        if len(imported) <= _MAX_SIBLING_IMPORTS:
            return []
        return [
            f"Module '{node.name}' imports from {len(imported)} sibling modules "
            f"(>{_MAX_SIBLING_IMPORTS}); reduce fan-out."
        ]


class DeepModule(PracticeGraphRule):
    slug = "deep-module"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        folder = context.module_folder(node)
        if folder is None:
            return []
        classes = _classes_in_folder(folder)
        if len(classes) <= _MAX_SHALLOW_CLASSES:
            return []
        tiny = sum(1 for _name, methods in classes if methods <= 1)
        if tiny >= _MAX_SHALLOW_CLASSES:
            return [
                f"Module '{node.name}' splits into many tiny classes ({len(classes)}); "
                "prefer a deep module with a small public surface."
            ]
        return []


class ExtensionsLiveWithTheDomain(PracticeGraphRule):
    slug = "extensions-live-with-the-domain"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        if not node.name.startswith("Graph"):
            return []
        relative = (node.source.file or "").replace("\\", "/")
        if "/framework/" in relative or relative.startswith("framework/"):
            return []
        oclass = context.ce_class(node)
        if oclass is None:
            return []
        bases = _python_bases(context, node)
        if bases and any(b.endswith("Epic") or b == "Epic" for b in bases):
            return []
        if node.name.startswith("Graph") and "Epic" in node.name:
            return [
                f"Class '{node.name}' should extend the framework Epic in the domain module, "
                "not stand alone."
            ]
        return []


def _python_modules(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in root.rglob("*.py"):
        if path.name == "__init__.py":
            stem = path.parent.name
        else:
            stem = path.stem
        out[stem] = path
    return out


def _import_graph(modules: dict[str, Path]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {name: set() for name in modules}
    for name, path in modules.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base = alias.name.split(".")[0]
                    if base in graph and base != name:
                        graph[name].add(base)
            elif isinstance(node, ast.ImportFrom) and node.module:
                base = node.module.split(".")[0]
                if base in graph and base != name:
                    graph[name].add(base)
    return graph


def _find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    for start in graph:
        stack = [(start, [start])]
        while stack:
            node, path = stack.pop()
            for nxt in graph.get(node, ()):
                if nxt in path:
                    idx = path.index(nxt)
                    cycles.append(path[idx:] + [nxt])
                    continue
                stack.append((nxt, path + [nxt]))
    return cycles


def _module_node_id(context, stem: str) -> str | None:
    for module in context.practice.nodes.get("Module", []):
        if module.name.lower() == stem.lower() or stem.lower() in (module.source.file or "").lower():
            return module.node_id
    for package in context.practice.nodes.get("Package", []):
        if package.name.lower() == stem.lower():
            return package.node_id
    return None


def _sibling_module_names(module_folder: Path) -> set[str]:
    parent = module_folder.parent
    if not parent.is_dir():
        return set()
    return {
        child.name
        for child in parent.iterdir()
        if child.is_dir() and (child / ".context" / "module-context.md").is_file()
    }


def _imported_sibling_names(node: ast.AST, sibling_names: set[str]) -> set[str]:
    found: set[str] = set()
    if isinstance(node, ast.Import):
        for alias in node.names:
            base = alias.name.split(".")[0]
            if base in sibling_names:
                found.add(base)
    elif isinstance(node, ast.ImportFrom) and node.module:
        base = node.module.split(".")[0]
        if base in sibling_names:
            found.add(base)
    return found


def _classes_in_folder(folder: Path) -> list[tuple[str, int]]:
    items: list[tuple[str, int]] = []
    for path in folder.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                method_count = sum(
                    1 for child in node.body if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                )
                items.append((node.name, method_count))
    return items


def _python_bases(context, node) -> list[str]:
    if context.source_root is None or not node.source.file:
        return []
    path = context.source_root / node.source.file
    if not path.is_file():
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return []
    for item in tree.body:
        if isinstance(item, ast.ClassDef) and item.name == node.name:
            return [ast.unparse(base) for base in item.bases]
    return []
