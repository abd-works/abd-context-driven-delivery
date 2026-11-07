"""Practice-wide checks (imports, module depth) — read folder and class facts across the graph."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.rules_shared.typed_and_comments import is_test_code

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_MAX_SIBLING_IMPORTS = 8
_MAX_PUBLIC_SHARE = 0.4
# A module of one or two classes cannot keep 60% private while exposing anything, so it is not measured.
_MIN_MEASURED_CLASSES = 3
_FOLDER_TYPES = ("Module", "Package")
_CODE_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".jsx")
_PY_FROM_IMPORT = re.compile(r"^\s*from\s+[\w.]+\s+import\s+(\([^)]*\)|[^\n]+)", re.M)
_JS_IMPORT = re.compile(r"\bimport\s+(?:type\s+)?([\w$]+)?\s*,?\s*(?:\{([^}]*)\})?\s*from\b")
_QUALIFIED_CLASS = re.compile(r"\.([A-Z]\w*)\b")
_IMPORT_ALIAS = re.compile(r"\s+as\s+\w+")


class OneWayDeps(PracticeGraphRule):
    """Reports every import between two modules of the same cycle, so the whole cycle shows, not one pair of it."""

    slug = "one-way-deps"
    node_types = ("Module", "Package")

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        imports = {
            folder.node_id: set(folder.get_fact("dependencies", []))
            for folder in _folders(context)
        }
        hits: list[tuple[str, str]] = []
        for cycle in _strongly_connected(imports):
            for importer in sorted(cycle):
                first = context.practice.registered(importer)
                for imported in sorted(imports.get(importer, set()) & cycle):
                    second = context.practice.registered(imported)
                    hits.append(
                        (
                            importer,
                            f"Circular import: '{first.name}' imports '{second.name}', which imports back into "
                            f"'{first.name}' through a cycle of {len(cycle)} modules; dependencies must flow one way.",
                        )
                    )
        return hits


class LowCoupling(PracticeGraphRule):
    slug = "low-coupling"
    node_types = ("Module",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        siblings = _sibling_modules(node, context)
        if not siblings:
            return []
        imported = {
            sibling
            for target in _imports_under(node, context)
            for sibling in siblings
            if target == sibling or target.startswith(sibling + "/")
        }
        if len(imported) <= _MAX_SIBLING_IMPORTS:
            return []
        return [
            f"Module '{node.name}' imports from {len(imported)} sibling modules "
            f"(>{_MAX_SIBLING_IMPORTS}); reduce fan-out."
        ]


class DeepModule(PracticeGraphRule):
    """At most 40% of a first-class module's classes are public: named by code in another module.

    A first-class module is a folder with a module card; folders without one roll up into the nearest module above
    them. A class is public when production code outside its module imports it or reaches it as ``module.Class``;
    a name starting with ``_`` keeps it private. Tests do not make a class public.
    """

    slug = "deep-module"
    node_types = ("Module",)

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        modules = sorted(
            (module for module in context.practice.nodes.get("Module", []) if module.source.file),
            key=lambda module: -len(module.source.file),
        )
        classes: dict[str, list[str]] = {}
        for node in context.practice.nodes.get("OoadClass", []):
            owner = _owning_module(node.source.file, modules)
            if owner is not None and node.name != "_module" and not is_test_code(node.source.file):
                classes.setdefault(owner.node_id, []).append(node.name)
        importers = _importers_by_name(context, modules)
        hits: list[tuple[str, str]] = []
        for module in modules:
            names = classes.get(module.node_id, [])
            public = sorted(
                name for name in set(names) if not name.startswith("_") and importers.get(name, set()) - {module.node_id}
            )
            if len(names) < _MIN_MEASURED_CLASSES or len(public) <= _MAX_PUBLIC_SHARE * len(names):
                continue
            hits.append(
                (
                    module.node_id,
                    f"Module '{module.name}' exposes {len(public)} of {len(names)} classes "
                    f"({round(100 * len(public) / len(names))}%, max {round(100 * _MAX_PUBLIC_SHARE)}%) to other "
                    f"modules: {', '.join(public)}. Keep most classes behind a few public ones.",
                )
            )
        return hits


def _owning_module(file: str | None, modules: list["Node"]) -> "Node | None":
    """The deepest module folder holding the file; ``modules`` is ordered deepest first."""
    return next((module for module in modules if _is_under(file, module.source.file)), None)


def _importers_by_name(context: "RuleCheckContext", modules: list["Node"]) -> dict[str, set[str]]:
    """Each class name production code imports or qualifies, with the modules whose code does it."""
    if context.source_root is None:
        return {}
    importers: dict[str, set[str]] = {}
    for folder in _folders(context):
        directory = Path(context.source_root) / folder.source.file
        if not directory.is_dir():
            continue
        for file in directory.iterdir():
            relative = f"{folder.source.file}/{file.name}"
            if file.suffix.lower() not in _CODE_SUFFIXES or is_test_code(relative):
                continue
            importer = _owning_module(relative, modules)
            for name in _imported_names(file.read_text(encoding="utf-8", errors="replace")):
                importers.setdefault(name, set()).add(importer.node_id if importer else "")
    return importers


def _imported_names(text: str) -> set[str]:
    names: set[str] = set(_QUALIFIED_CLASS.findall(text))
    for match in _PY_FROM_IMPORT.finditer(text):
        names.update(_IMPORT_ALIAS.sub("", item).strip() for item in match.group(1).strip("()").split(","))
    for default, braced in _JS_IMPORT.findall(text):
        names.add(default)
        names.update(_IMPORT_ALIAS.sub("", item).strip() for item in (braced or "").split(","))
    names.discard("")
    return names


class ExtensionsLiveWithTheDomain(PracticeGraphRule):
    slug = "extensions-live-with-the-domain"
    node_types = ("OoadClass",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if not node.name.startswith("Graph") or "Epic" not in node.name or not node.has_fact("bases"):
            return []
        relative = (node.source.file or "").replace("\\", "/")
        if "/framework/" in relative or relative.startswith("framework/"):
            return []
        if any(base == "Epic" or base.endswith("Epic") for base in node.get_fact("bases")):
            return []
        return [
            f"Class '{node.name}' should extend the framework Epic in the domain module, "
            "not stand alone."
        ]


class SourceParses(PracticeGraphRule):
    """A source file its language cannot parse is read into no class, so every other rule passes it without a look."""

    slug = "source-parses"
    node_types = _FOLDER_TYPES

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        return [
            f"Source file {entry}; fix it so its classes can be checked."
            for entry in node.get_fact("unreadable_sources", []) or []
        ]


def _folders(context: "RuleCheckContext") -> list["Node"]:
    return [folder for kind in _FOLDER_TYPES for folder in context.practice.nodes.get(kind, [])]


def _is_under(path: str | None, folder: str | None) -> bool:
    if not path or not folder:
        return False
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def _sibling_modules(node: "Node", context: "RuleCheckContext") -> list[str]:
    """Folder paths of the other modules (folders with module-context.md) next to this one."""
    parent = _parent_folder(node.source.file or "")
    return [
        other.source.file
        for other in context.practice.nodes.get("Module", [])
        if other is not node and other.source.file and _parent_folder(other.source.file) == parent
    ]


def _parent_folder(path: str) -> str:
    return path.rsplit("/", 1)[0] if "/" in path else ""


def _imports_under(node: "Node", context: "RuleCheckContext") -> set[str]:
    """Folder paths imported by this module's folder and every folder beneath it."""
    targets: set[str] = set()
    for folder in _folders(context):
        if not _is_under(folder.source.file, node.source.file):
            continue
        for dependency in folder.get_fact("dependencies", []):
            imported = context.practice.registered(dependency)
            if imported is not None and imported.source.file:
                targets.add(imported.source.file)
    return targets


def _strongly_connected(graph: dict[str, set[str]]) -> list[set[str]]:
    """Every group of two or more modules that import one another in a cycle (Tarjan's strongly connected components).

    Walking each path from every module is exponential on a repository-sized graph; this visits each module once.
    """
    index: dict[str, int] = {}
    lowest: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    groups: list[set[str]] = []

    def enter(module: str) -> tuple[str, object]:
        index[module] = lowest[module] = len(index)
        stack.append(module)
        on_stack.add(module)
        return module, iter(sorted(graph.get(module, ())))

    for start in sorted(graph):
        if start in index:
            continue
        work = [enter(start)]
        while work:
            module, pending = work[-1]
            imported = next(pending, None)
            if imported is not None:
                if imported not in index:
                    work.append(enter(imported))
                elif imported in on_stack:
                    lowest[module] = min(lowest[module], index[imported])
                continue
            work.pop()
            if work:
                lowest[work[-1][0]] = min(lowest[work[-1][0]], lowest[module])
            if lowest[module] == index[module]:
                groups.append(_pop_group(stack, on_stack, module))
    return [group for group in groups if len(group) > 1]


def _pop_group(stack: list[str], on_stack: set[str], root: str) -> set[str]:
    group: set[str] = set()
    while True:
        member = stack.pop()
        on_stack.discard(member)
        group.add(member)
        if member == root:
            return group
