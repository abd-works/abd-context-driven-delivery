"""Practice-wide checks (imports, module depth) — read the folder and class facts the build compared across the graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import PracticeGraphRule

from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

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
    judged: a spec may import the module above the one it tests, so its imports are left out. The cycles are found when
    the graph is built and kept on each folder (``import_cycles``, ``file_import_cycles``).
    """

    slug = "one-way-deps"
    node_types = ("Module", "Package")

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        folders = _folders(context)
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
    """At most 40% of a module's classes are public: classes that leave the module.

    A module is a folder with a module card, measured over its whole subtree: its own files, the packages under it, and
    the modules nested in it, each of which is measured again over its own subtree. A class definition is public when
    it leaves the subtree: production code outside the subtree imports it or reaches it as ``module.Class``, each
    import resolved to the one definition it names; a package registers it with a framework registry; or the installer
    publishes it as a toolset. Use inside the subtree, package to package or nested module to parent, keeps it private,
    and a name starting with ``_`` keeps it private. Tests, test support, examples, and test doubles neither count as
    classes nor make a class public. The build keeps the counts and the public classes, by ``file:Name`` with the
    routes that reach each, on each module (``subtree_class_count``, ``public_classes``), counting the callers outside a
    validated scope too; the operation counts beside them are for reading, not judged.
    """

    slug = "deep-module"
    node_types = ("Module",)

    def check_practice(self, context: "RuleCheckContext") -> list[tuple[str, str]]:
        hits: list[tuple[str, str]] = []
        for module in context.nodes("Module"):
            count = module.get_fact("subtree_class_count") or 0
            public = list(module.get_fact("public_classes") or {})
            if count >= _MIN_MEASURED_CLASSES and len(public) > self._allowed_public(count):
                hits.append((module.node_id, self._exposure_message(module, public, count)))
        return hits

    def _exposure_message(self, module: "Node", public: list[str], class_count: int) -> str:
        return (
            f"Module '{module.name}' exposes {len(public)} of {class_count} classes to other modules, more "
            f"than the {self._allowed_public(class_count)} that {round(100 * _MAX_PUBLIC_SHARE)}% allows: "
            f"{', '.join(self._named(public))}. Keep most classes behind a few public ones."
        )

    def _named(self, public: list[str]) -> list[str]:
        """Each public class (``file:Name``) by its name, with its file when another public class shares the name."""
        names = [key.rsplit(":", 1)[-1] for key in public]
        return [name if names.count(name) == 1 else key for name, key in zip(names, public)]

    def _allowed_public(self, classes: int) -> int:
        """How many of a module's classes may be public: 40% of them, rounded down, since a count over it fails."""
        return int(round(_MAX_PUBLIC_SHARE * classes, 9))


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
