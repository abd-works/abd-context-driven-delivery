"""Practice-wide checks (imports, module depth) — read the folder and class facts the build compared across the graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.reading.folder_facts import FOLDER_TYPES
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext

_MAX_SIBLING_IMPORTS = 8
# The share of a module's methods its seam may hold: the public methods of the classes that leave it.
_MAX_SEAM_SHARE = 0.35
# A module of fewer methods than this cannot hide much behind any interface, so it is not measured.
_MIN_MEASURED_METHODS = 10


class OneWayDeps(PracticeGraphRule):
    """Reports every import between two modules of the same cycle, so the whole cycle shows, not one pair of it; then
    every import between two files of one folder that import each other in a cycle.

    A cycle between files in different folders is also a cycle between those folders, so the folder report already
    names it. The imports read are production code's, wherever a file makes them: at the top, inside a function, or
    through ``importlib``. An import under ``if TYPE_CHECKING:`` never runs, so it is no dependency. Specs are not
    judged: a spec may import the module above the one it tests, so its imports are left out. The cycles are found when
    the graph is built and kept on each folder (``import_cycles``, ``file_import_cycles``).
    """

    slug = "one-way-deps"
    node_types = FOLDER_TYPES

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        folders = self._folders(context)
        return [hit for folder in folders for hit in self._folder_cycles(folder)] + [
            hit for folder in folders for hit in self._file_cycles(folder)
        ]

    def _folder_cycles(self, folder: "Node") -> list[tuple[str, str]]:
        return [
            (
                folder.node_id,
                f"Circular import: '{folder.name}' imports '{imported}', which imports back into "
                f"'{folder.name}' through a cycle of {size} modules; dependencies must flow one way.",
            )
            for imported, size in folder.get_fact("import_cycles") or []
        ]

    def _file_cycles(self, folder: "Node") -> list[tuple[str, str]]:
        return [
            (
                folder.node_id,
                f"Circular import in '{folder.name}': '{importer}' imports '{imported}', which imports "
                f"back into '{importer}' through a cycle of {size} files; move the shared code "
                "to the file that owns it so dependencies flow one way.",
            )
            for importer, imported, size in folder.get_fact("file_import_cycles") or []
        ]

    def _folders(self, context: "RuleCheckContext") -> list["Node"]:
        return [folder for kind in FOLDER_TYPES for folder in context.nodes(kind)]


class LowCoupling(ProductionCodeRule):
    """A module imports from at most eight of the modules beside it: the sibling modules it or any folder beneath it
    depends on, which the build keeps on the module (``sibling_modules_imported``)."""

    slug = "low-coupling"
    node_types = ("Module",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        imported = node.get_fact("sibling_modules_imported") or []
        if len(imported) <= _MAX_SIBLING_IMPORTS:
            return []
        return [
            f"Module '{node.name}' imports from {len(imported)} sibling modules "
            f"(>{_MAX_SIBLING_IMPORTS}); reduce fan-out."
        ]


class DeepModule(PracticeGraphRule):
    """At most 35% of a module's methods are its seam: the public methods of the classes that leave the module.

    A module's interface is the methods callers can call; a deep module hides much behind a small interface. A module
    is a folder with a module card, measured over its whole subtree: its own files, the packages under it, and the
    modules nested in it, each of which is measured again over its own subtree. The build records, on each module, its
    methods (``operations_total``: every operation of its classes and every module function of its production files)
    and its seam methods (``seam_operations``: the public methods, constructors aside, of the classes that leave the
    subtree, named from outside it, registered with a framework registry, or published as a toolset). The rule compares
    the two with its limit; a module of fewer than 10 methods is not measured. The class counts beside them
    (``public_class_count``, ``subtree_class_count``) are context in the message, never a verdict.
    """

    slug = "deep-module"
    node_types = ("Module",)

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        for module in context.nodes("Module"):
            methods = module.get_fact("operations_total") or 0
            seam = module.get_fact("seam_operations") or 0
            if methods >= _MIN_MEASURED_METHODS and seam > self._allowed_seam(methods):
                hits.append((module.node_id, self._exposure_message(module, seam, methods)))
        return hits

    def _exposure_message(self, module: "Node", seam: int, methods: int) -> str:
        public = list(module.get_fact("public_classes") or {})
        return (
            f"Module '{module.name}' exposes {seam} of its {methods} methods to other modules, more than the "
            f"{self._allowed_seam(methods)} that {round(100 * _MAX_SEAM_SHARE)}% allows; they are the public methods of "
            f"its {len(public)} public classes of {module.get_fact('subtree_class_count') or 0}: "
            f"{', '.join(self._named(public))}. Hide more behind fewer public methods."
        )

    def _named(self, public: list[str]) -> list[str]:
        """Each public class (``file:Name``) by its name, with its file when another public class shares the name."""
        names = [key.rsplit(":", 1)[-1] for key in public]
        return [name if names.count(name) == 1 else key for name, key in zip(names, public)]

    def _allowed_seam(self, methods: int) -> int:
        """How many of a module's methods its seam may hold: 35% of them, rounded down, since a count over it fails."""
        return int(round(_MAX_SEAM_SHARE * methods, 9))


class ExtensionsLiveWithTheDomain(ProductionCodeRule):
    """A class that joins one of its own package's types with the class of another package it is named after extends
    that other package's domain, so it belongs beside the class it extends: kept in the base package, it makes the base
    package depend on every domain it is extended for. `GraphEpic(Epic, Node)` in the framework that declares `Node`
    is the case; in the package that declares `Epic`, or a package nested under it (`ddd/model/markdown` under
    `ddd/model`), it is where it belongs. The build keeps what a class extends on it (``extends_domain``)."""

    slug = "extensions-live-with-the-domain"
    node_types = ("OoadClass",)

    def check_production(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        extension = node.get_fact("extends_domain") or {}
        if not extension:
            return []
        home = extension["home"]
        return [
            f"Class '{node.name}' extends {', '.join(extension['extended'])} from '{home}' with this package's "
            f"{', '.join(extension['own'])}: it is an extension of '{home}' and belongs there, so this package does not "
            "depend on it."
        ]


class SourceParses(PracticeGraphRule):
    """A source file its language cannot parse is read into no class, so every other rule passes it without a look.
    The module that holds the file reports it, or the folder that holds it when no module does. Specs are judged too: a spec that does not parse cannot run, and nothing else reports it."""

    slug = "source-parses"
    node_types = FOLDER_TYPES

    def check(self, node: "Node", context: "RuleCheckContext") -> list[str]:
        if not node.has_fact("unreadable_sources"):
            # A folder reads its module's facts as its own, and the module has already reported these files.
            return []
        return [
            f"Source file {entry}; fix it so its classes can be checked."
            for entry in node.get_fact("unreadable_sources", []) or []
        ]
