"""Practice-wide checks (imports, module depth) — read folder and class facts across the graph."""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule
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
        for importer, imported, size in _ImportCycles(imports).imports_in_cycles():
            first, second = context.node(importer), context.node(imported)
            hits.append(
                (
                    importer,
                    f"Circular import: '{first.name}' imports '{second.name}', which imports back into "
                    f"'{first.name}' through a cycle of {size} modules; dependencies must flow one way.",
                )
            )
        return hits

    def _file_cycles(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        for folder in _folders(context):
            if not folder.has_fact("sibling_imports"):
                continue
            imports = {file: set(imported) for file, imported in (folder.get_fact("sibling_imports") or {}).items()}
            hits.extend(
                (
                    folder.node_id,
                    f"Circular import in '{folder.name}': '{importer}' imports '{imported}', which imports "
                    f"back into '{importer}' through a cycle of {size} files; move the shared code "
                    "to the file that owns it so dependencies flow one way.",
                )
                for importer, imported, size in _ImportCycles(imports).imports_in_cycles()
            )
        return hits


class _ImportCycles:
    """The groups of two or more modules of one import graph that import one another in a cycle, found with Tarjan's
    strongly connected components. Walking each path from every module is exponential on a repository-sized graph;
    this visits each module once."""

    def __init__(self, imports: dict[str, set[str]]) -> None:
        self._imports = imports
        self._index: dict[str, int] = {}
        self._lowest: dict[str, int] = {}
        self._stack: list[str] = []
        self._on_stack: set[str] = set()
        self._groups: list[set[str]] = []

    def imports_in_cycles(self) -> list[tuple[str, str, int]]:
        """Each import between two modules of one cycle, with the number of modules in that cycle, in name order."""
        return [
            (importer, imported, len(cycle))
            for cycle in self._cycles()
            for importer in sorted(cycle)
            for imported in sorted(self._imports.get(importer, set()) & cycle)
        ]

    def _cycles(self) -> list[set[str]]:
        for start in sorted(self._imports):
            if start not in self._index:
                self._walk_from(start)
        return [group for group in self._groups if len(group) > 1]

    def _walk_from(self, start: str) -> None:
        work = [self._enter(start)]
        while work:
            self._step(work)

    def _step(self, work: list[tuple[str, Iterator[str]]]) -> None:
        """Follow the next import of the module on top of the walk: leave it when it has none left, enter a module not
        yet reached, or lower its index to one still on the stack, which shares its group."""
        module, pending = work[-1]
        imported = next(pending, None)
        if imported is None:
            self._leave(work)
        elif imported not in self._index:
            work.append(self._enter(imported))
        elif imported in self._on_stack:
            self._lowest[module] = min(self._lowest[module], self._index[imported])

    def _enter(self, module: str) -> tuple[str, Iterator[str]]:
        self._index[module] = self._lowest[module] = len(self._index)
        self._stack.append(module)
        self._on_stack.add(module)
        return module, iter(sorted(self._imports.get(module, ())))

    def _leave(self, work: list[tuple[str, Iterator[str]]]) -> None:
        """Finish the module on top of the walk: hand its lowest index to the module that reached it, and close its
        group when it is the first of the group the walk entered."""
        module, _ = work.pop()
        if work:
            caller = work[-1][0]
            self._lowest[caller] = min(self._lowest[caller], self._lowest[module])
        if self._lowest[module] == self._index[module]:
            self._groups.append(self._pop_group(module))

    def _pop_group(self, root: str) -> set[str]:
        group: set[str] = set()
        while True:
            member = self._stack.pop()
            self._on_stack.discard(member)
            group.add(member)
            if member == root:
                return group


class LowCoupling(ProductionCodeRule):
    slug = "low-coupling"
    node_types = ("Module",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        siblings = self._sibling_modules(node, context)
        if not siblings:
            return []
        imported = {
            sibling
            for target in self._imports_under(node, context)
            for sibling in siblings
            if target == sibling or target.startswith(sibling + "/")
        }
        if len(imported) <= _MAX_SIBLING_IMPORTS:
            return []
        return [
            f"Module '{node.name}' imports from {len(imported)} sibling modules "
            f"(>{_MAX_SIBLING_IMPORTS}); reduce fan-out."
        ]

    def _sibling_modules(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        """Folder paths of the other modules (folders with module-context.md) next to this one."""
        parent = _parent_folder(node.source.file or "")
        return [
            other.source.file
            for other in context.nodes("Module")
            if other is not node and other.source.file and _parent_folder(other.source.file) == parent
        ]

    def _imports_under(self, node: "Node", context: "RuleCheckContext") -> set[str]:
        """Folder paths imported by this module's folder and every folder beneath it."""
        return {
            imported.source.file
            for folder in _folders(context)
            if _is_under(folder.source.file, node.source.file)
            for imported in context.targets(folder, "dependsOn")
            if imported.source.file
        }


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
        classes = self._classes_by_module(context, modules)
        importers = self._importers_by_name(context, modules)
        hits: list[tuple[str, str]] = []
        for module in modules:
            names = classes.get(module.node_id, [])
            public = sorted(
                name for name in set(names) if not name.startswith("_") and importers.get(name, set()) - {module.source.file}
            )
            if len(names) >= _MIN_MEASURED_CLASSES and len(public) > self._allowed_public(len(names)):
                hits.append((module.node_id, self._exposure_message(module, public, len(names))))
        return hits

    def _classes_by_module(self, context: "RuleCheckContext", modules: list["Node"]) -> dict[str, list[str]]:
        """The names of the classes each module holds, by the module's node id. A private record, such as a parser's
        `_Section`, is neither seam nor hidden design, so it is not counted."""
        graph_classes = context.index(ClassGraph)
        classes: dict[str, list[str]] = {}
        for node in graph_classes.classes:
            owner = self._owning_module(node.source.file, modules)
            if owner is not None and not (node.name.startswith("_") and not graph_classes.has_behavior(node)):
                classes.setdefault(owner.node_id, []).append(node.name)
        return classes

    def _exposure_message(self, module: "Node", public: list[str], class_count: int) -> str:
        return (
            f"Module '{module.name}' exposes {len(public)} of {class_count} classes to other modules, more "
            f"than the {self._allowed_public(class_count)} that {round(100 * _MAX_PUBLIC_SHARE)}% allows: "
            f"{', '.join(public)}. Keep most classes behind a few public ones."
        )

    def _allowed_public(self, classes: int) -> int:
        """How many of a module's classes may be public: 40% of them, rounded down, since a count over it fails."""
        return int(round(_MAX_PUBLIC_SHARE * classes, 9))

    def _owning_module(self, file: str | None, modules: list["Node"]) -> "Node | None":
        """The deepest module folder holding the file; ``modules`` is ordered deepest first."""
        return next((module for module in modules if _is_under(file, module.source.file)), None)

    def _importers_by_name(self, context: "RuleCheckContext", modules: list["Node"]) -> dict[str, set[str]]:
        """Each class name production code imports or qualifies, with the folders of the modules whose code does it: the
        names each folder's files import, which the reading kept on the folder, and the names the files outside the
        scope import, which it kept on the practice's root."""
        importers: dict[str, set[str]] = {}
        for folder in _folders(context):
            importer = self._owning_module(f"{folder.source.file}/", modules)
            for name in folder.get_fact("imported_names", []) or []:
                importers.setdefault(name, set()).add(importer.source.file if importer else "")
        root = context.practice.reading.in_graph.root
        outside = root.get_fact("imported_names_outside") if root.has_fact("imported_names_outside") else {}
        for name, folders in outside.items():
            importers.setdefault(name, set()).update(folders)
        return importers


class ExtensionsLiveWithTheDomain(ProductionCodeRule):
    """A class that joins one of its own package's types with the class of another package it is named after extends
    that other package's domain, so it belongs beside the class it extends: kept in the base package, it makes the base
    package depend on every domain it is extended for. `GraphEpic(Epic, Node)` in the framework that declares `Node`
    is the case; in the package that declares `Epic`, or a package nested under it (`ddd/model/markdown` under
    `ddd/model`), it is where it belongs."""

    slug = "extensions-live-with-the-domain"
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        classes = context.index(ClassGraph)
        own_folder = _parent_folder(node.source.file or "")
        homes = {base: {_parent_folder(declared.source.file or "") for declared in classes.named(base)} for base in classes.bases_of(node)}
        own = [base for base, folders in homes.items() if own_folder in folders]
        extended = self._extended_domain_bases(node.name, homes, own_folder)
        if not own or not extended or self._builds_on(own, homes[extended[0]], classes):
            return []
        home = sorted(homes[extended[0]])[0]
        return [
            f"Class '{node.name}' extends {', '.join(extended)} from '{home}' with this package's {', '.join(own)}: "
            f"it is an extension of '{home}' and belongs there, so this package does not depend on it."
        ]

    def _builds_on(self, own: list[str], home: set[str], classes: ClassGraph) -> bool:
        """True when a base of the class's own package already derives from a class of the package it extends: the
        package is a format built on that one (`DrawIOClass(DiagramClass)`), and the class is where it belongs, since
        moving it would make the base package import its format."""
        return any(
            _parent_folder(declared.source.file or "") in home
            for base in own
            for node in classes.named(base)
            for parent in classes.bases_of(node)
            for declared in classes.named(parent)
        )

    def _extended_domain_bases(self, name: str, homes: dict[str, set[str]], own_folder: str) -> list[str]:
        """The bases a class named name extends from another package's domain: the ones it is named after (`GraphEpic`
        extends `Epic`), declared in a package that is neither the class's own nor one it is nested under."""
        return [
            base
            for base, folders in homes.items()
            if folders and not any(_is_under(own_folder, folder) for folder in folders) and name.endswith(base)
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


def _parent_folder(path: str) -> str:
    return path.rsplit("/", 1)[0] if "/" in path else ""
