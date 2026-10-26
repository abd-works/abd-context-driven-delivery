"""Practice-wide checks (imports, module depth) — read folder and class facts across the graph."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

_MAX_SIBLING_IMPORTS = 8
_MAX_SHALLOW_CLASSES = 5
_FOLDER_TYPES = ("Module", "Package")


class OneWayDeps(PracticeGraphRule):
    slug = "one-way-deps"
    node_types = ("Module", "Package")

    def check(self, node, context) -> list[str]:
        return []

    def check_practice(self, context) -> list[tuple[str, str]]:
        imports = {
            folder.node_id: set(folder.get_fact("dependencies", []))
            for folder in _folders(context)
        }
        for cycle in _find_cycles(imports):
            first, second = context.practice.registered(cycle[0]), context.practice.registered(cycle[1])
            return [
                (
                    first.node_id,
                    f"Circular import between '{first.name}' and '{second.name}' breaks one-way dependencies.",
                )
            ]
        return []


class LowCoupling(PracticeGraphRule):
    slug = "low-coupling"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
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
    slug = "deep-module"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        method_counts = [
            class_node.get_fact("method_count", 0)
            for class_node in context.practice.nodes.get("OoadClass", [])
            if _is_under(class_node.source.file, node.source.file)
        ]
        if len(method_counts) <= _MAX_SHALLOW_CLASSES:
            return []
        tiny = sum(1 for count in method_counts if count <= 1)
        if tiny < _MAX_SHALLOW_CLASSES:
            return []
        return [
            f"Module '{node.name}' splits into many tiny classes ({len(method_counts)}); "
            "prefer a deep module with a small public surface."
        ]


class ExtensionsLiveWithTheDomain(PracticeGraphRule):
    slug = "extensions-live-with-the-domain"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
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


def _folders(context) -> list:
    return [folder for kind in _FOLDER_TYPES for folder in context.practice.nodes.get(kind, [])]


def _is_under(path: str | None, folder: str | None) -> bool:
    if not path or not folder:
        return False
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def _sibling_modules(node, context) -> list[str]:
    """Folder paths of the other modules (folders with module-context.md) next to this one."""
    parent = _parent_folder(node.source.file or "")
    return [
        other.source.file
        for other in context.practice.nodes.get("Module", [])
        if other is not node and other.source.file and _parent_folder(other.source.file) == parent
    ]


def _parent_folder(path: str) -> str:
    return path.rsplit("/", 1)[0] if "/" in path else ""


def _imports_under(node, context) -> set[str]:
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


def _find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    # One DFS visit per module; enumerating every path is exponential on a repo-sized graph.
    cycles: list[list[str]] = []
    visited: set[str] = set()
    for start in graph:
        if start not in visited:
            cycles.extend(_cycles_reachable_from(graph, start, visited))
    return cycles


def _cycles_reachable_from(graph: dict[str, set[str]], start: str, visited: set[str]) -> list[list[str]]:
    cycles: list[list[str]] = []
    path = [start]
    on_path = {start}
    visited.add(start)
    pending = [iter(sorted(graph.get(start, ())))]
    while pending:
        nxt = next(pending[-1], None)
        if nxt is None:
            pending.pop()
            on_path.discard(path.pop())
            continue
        if nxt in on_path:
            cycles.append(path[path.index(nxt):] + [nxt])
            continue
        if nxt in visited:
            continue
        visited.add(nxt)
        on_path.add(nxt)
        path.append(nxt)
        pending.append(iter(sorted(graph.get(nxt, ()))))
    return cycles
