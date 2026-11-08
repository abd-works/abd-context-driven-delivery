"""Practice-wide checks (imports, module depth) — read folder and class facts across the graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.production_code import ProductionCodeRule, is_test_code
from cdd_guidance.practices.clean_engineering.rules.class_graph import ClassGraph

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_MAX_SIBLING_IMPORTS = 8
_MAX_PUBLIC_SHARE = 0.4
# A module of one or two classes cannot keep 60% private while exposing anything, so it is not measured.
_MIN_MEASURED_CLASSES = 3
_FOLDER_TYPES = ("Module", "Package")


class OneWayDeps(PracticeGraphRule):
    """Reports every import between two modules of the same cycle, so the whole cycle shows, not one pair of it; then
    every import between two files of one folder that import each other in a cycle.

    A cycle between files in different folders is also a cycle between those folders, so the folder report already
    names it. The imports read are production code's, wherever a file makes them: at the top, inside a function, or
    through ``importlib``. An import under ``if TYPE_CHECKING:`` never runs, so it is no dependency. Specs are not
    judged: a spec may import the module above the one it tests, so its imports are left out.
    """

    slug = "one-way-deps"
    node_types = ("Module", "Package")

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        return self._folder_cycles(context) + self._file_cycles(context)

    def _folder_cycles(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        imports = {
            folder.node_id: {imported.node_id for imported in context.targets(folder, "dependsOn")}
            for folder in _folders(context)
        }
        hits: list[tuple[str, str]] = []
        for cycle in _strongly_connected(imports):
            for importer in sorted(cycle):
                first = context.node(importer)
                for imported in sorted(imports.get(importer, set()) & cycle):
                    second = context.node(imported)
                    hits.append(
                        (
                            importer,
                            f"Circular import: '{first.name}' imports '{second.name}', which imports back into "
                            f"'{first.name}' through a cycle of {len(cycle)} modules; dependencies must flow one way.",
                        )
                    )
        return hits

    def _file_cycles(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        for folder in _folders(context):
            if not folder.has_fact("sibling_imports"):
                continue
            imports = {file: set(imported) for file, imported in (folder.get_fact("sibling_imports") or {}).items()}
            for cycle in _strongly_connected(imports):
                for importer in sorted(cycle):
                    for imported in sorted(imports[importer] & cycle):
                        hits.append(
                            (
                                folder.node_id,
                                f"Circular import in '{folder.name}': '{importer}' imports '{imported}', which imports "
                                f"back into '{importer}' through a cycle of {len(cycle)} files; move the shared code "
                                "to the file that owns it so dependencies flow one way.",
                            )
                        )
        return hits


class LowCoupling(ProductionCodeRule):
    slug = "low-coupling"
    node_types = ("Module",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
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
    a name starting with ``_`` keeps it private. Tests and test fixtures neither count as classes nor make a class
    public. The callers read include those outside a validated scope, which the reading keeps on the practice's root.
    """

    slug = "deep-module"
    node_types = ("Module",)

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        modules = sorted(
            (module for module in context.nodes("Module") if module.source.file),
            key=lambda module: -len(module.source.file),
        )
        classes: dict[str, list[str]] = {}
        for node in context.nodes("OoadClass"):
            owner = _owning_module(node.source.file, modules)
            if owner is not None and node.name != "_module" and not is_test_code(node.source.file):
                classes.setdefault(owner.node_id, []).append(node.name)
        importers = _importers_by_name(context, modules)
        hits: list[tuple[str, str]] = []
        for module in modules:
            names = classes.get(module.node_id, [])
            public = sorted(
                name for name in set(names) if not name.startswith("_") and importers.get(name, set()) - {module.source.file}
            )
            if len(names) < _MIN_MEASURED_CLASSES or len(public) <= _allowed_public(len(names)):
                continue
            hits.append(
                (
                    module.node_id,
                    f"Module '{module.name}' exposes {len(public)} of {len(names)} classes to other modules, more "
                    f"than the {_allowed_public(len(names))} that {round(100 * _MAX_PUBLIC_SHARE)}% allows: "
                    f"{', '.join(public)}. Keep most classes behind a few public ones.",
                )
            )
        return hits


def _allowed_public(classes: int) -> int:
    """How many of a module's classes may be public: 40% of them, rounded down, since a count over it fails."""
    return int(round(_MAX_PUBLIC_SHARE * classes, 9))


def _owning_module(file: str | None, modules: list["Node"]) -> "Node | None":
    """The deepest module folder holding the file; ``modules`` is ordered deepest first."""
    return next((module for module in modules if _is_under(file, module.source.file)), None)


def _importers_by_name(context: "RuleCheckContext", modules: list["Node"]) -> dict[str, set[str]]:
    """Each class name production code imports or qualifies, with the folders of the modules whose code does it: the
    names each folder's files import, which the reading kept on the folder, and the names the files outside the scope
    import, which it kept on the practice's root."""
    importers: dict[str, set[str]] = {}
    for folder in _folders(context):
        importer = _owning_module(f"{folder.source.file}/", modules)
        for name in folder.get_fact("imported_names", []) or []:
            importers.setdefault(name, set()).add(importer.source.file if importer else "")
    root = context.practice.in_graph.root
    outside = root.get_fact("imported_names_outside") if root.has_fact("imported_names_outside") else {}
    for name, folders in outside.items():
        importers.setdefault(name, set()).update(folders)
    return importers


class ExtensionsLiveWithTheDomain(ProductionCodeRule):
    """A class that joins one of its own package's types with the class of another package it is named after extends
    that other package's domain, so it belongs beside the class it extends: kept in the base package, it makes the base
    package depend on every domain it is extended for. `GraphEpic(Epic, Node)` in the framework that declares `Node`
    is the case; in the package that declares `Epic` it is where it belongs."""

    slug = "extensions-live-with-the-domain"
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        classes = context.index(ClassGraph)
        own_folder = _parent_folder(node.source.file or "")
        homes = {base: {_parent_folder(declared.source.file or "") for declared in classes.by_name.get(base, [])} for base in classes.bases_of(node)}
        own = [base for base, folders in homes.items() if own_folder in folders]
        # The domain class an extension extends is the one it is named after: `GraphEpic` extends `Epic`.
        extended = [base for base, folders in homes.items() if folders and own_folder not in folders and node.name.endswith(base)]
        if not own or not extended:
            return []
        home = sorted(homes[extended[0]])[0]
        return [
            f"Class '{node.name}' extends {', '.join(extended)} from '{home}' with this package's {', '.join(own)}: "
            f"it is an extension of '{home}' and belongs there, so this package does not depend on it."
        ]


class SourceParses(PracticeGraphRule):
    """A source file its language cannot parse is read into no class, so every other rule passes it without a look.
    Specs are judged too: a spec that does not parse cannot run, and nothing else reports it."""

    slug = "source-parses"
    node_types = ("Module",)

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        return [
            f"Source file {entry}; fix it so its classes can be checked."
            for entry in node.get_fact("unreadable_sources", []) or []
        ]


def _folders(context: "RuleCheckContext") -> list["Node"]:
    return [folder for kind in _FOLDER_TYPES for folder in context.nodes(kind)]


def _is_under(path: str | None, folder: str | None) -> bool:
    if not path or not folder:
        return False
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def _sibling_modules(node: "Node", context: "RuleCheckContext") -> list[str]:
    """Folder paths of the other modules (folders with module-context.md) next to this one."""
    parent = _parent_folder(node.source.file or "")
    return [
        other.source.file
        for other in context.nodes("Module")
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
        for imported in context.targets(folder, "dependsOn"):
            if imported.source.file:
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
