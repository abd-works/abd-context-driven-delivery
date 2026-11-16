"""How a compared fact is written on a node, and the facts each folder of the code keeps about the other folders: the
imports of it that close a cycle, the sibling modules it imports, and which of the classes of a module's whole subtree
code outside that subtree names."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.import_cycles import ImportCycles

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes
    from harness.graph.saved_graph import FactValue

    from cdd_guidance.practices.clean_engineering.model.class_graph import ClassGraph

_FOLDER_TYPES = ("Module", "Package")


def record_fact(node: "Node", key: str, fact: "FactValue") -> None:
    """Record fact on node when it says something, or when the node holds an older answer the fact replaces: a node a
    refresh kept holds the facts of the build before, and a node that never found anything keeps no empty fact, so the
    saved graph stays small."""
    if fact or node.has_fact(key):
        node.set_fact(key, fact)


def is_under(path: str | None, folder: str | None) -> bool:
    """True for a path at or below folder, both from the source root."""
    if not path or not folder:
        return False
    return path == folder or path.startswith(folder.rstrip("/") + "/")


def parent_folder(path: str) -> str:
    """The folder that holds path, from the source root; empty for a path at the root."""
    return path.rsplit("/", 1)[0] if "/" in path else ""


def folders_of(in_graph: "PracticeNodes") -> list["Node"]:
    """Every folder the practice holds: its modules, then its packages."""
    return [folder for kind in _FOLDER_TYPES for folder in in_graph.nodes(kind)]


def imported_folders(folder: "Node") -> list["Node"]:
    """The folders folder depends on: the nodes its ``dependsOn`` edges lead to."""
    return [edge.child for edge in folder.graph.edges.from_parent("dependsOn", folder)]


class ImportCycleFacts:
    """Each folder's imports that close a cycle of folders (``import_cycles``: the folder imported and the cycle's size),
    and its files' imports that close a cycle of the folder's own files (``file_import_cycles``: importer, imported, and
    the cycle's size), each in name order; every folder keeps both, empty when it closes none."""

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._folders = folders_of(in_graph)

    def record(self) -> None:
        imports = {folder.node_id: {imported.node_id for imported in imported_folders(folder)} for folder in self._folders}
        names = {folder.node_id: folder.name for folder in self._folders}
        cycles: dict[str, list[list]] = {folder.node_id: [] for folder in self._folders}
        for importer, imported, size in ImportCycles(imports).imports_in_cycles():
            cycles[importer].append([names[imported], size])
        for folder in self._folders:
            folder.set_fact("import_cycles", cycles[folder.node_id])
            folder.set_fact("file_import_cycles", self._file_cycles(folder))

    def _file_cycles(self, folder: "Node") -> list[list]:
        """The imports between the folder's own files that close a cycle, from what its files import of one another."""
        if not folder.has_fact("sibling_imports"):
            return []
        imports = {file: set(imported) for file, imported in (folder.get_fact("sibling_imports") or {}).items()}
        return [[importer, imported, size] for importer, imported, size in ImportCycles(imports).imports_in_cycles()]


class SiblingFanOut:
    """The sibling modules each module imports from (``sibling_modules_imported``): the other modules in the folder that
    holds it, which it or any folder beneath it depends on, by their paths."""

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._modules = in_graph.nodes("Module")
        self._folders = folders_of(in_graph)

    def record(self) -> None:
        for module in self._modules:
            siblings = self._siblings(module)
            imported = {sibling for target in self._imports_under(module) for sibling in siblings if is_under(target, sibling)}
            module.set_fact("sibling_modules_imported", sorted(imported))

    def _siblings(self, module: "Node") -> list[str]:
        parent = parent_folder(module.source.file or "")
        return [
            other.source.file
            for other in self._modules
            if other is not module and other.source.file and parent_folder(other.source.file) == parent
        ]

    def _imports_under(self, module: "Node") -> set[str]:
        """Folder paths imported by the module's folder and every folder beneath it."""
        return {
            imported.source.file
            for folder in self._folders
            if is_under(folder.source.file, module.source.file)
            for imported in imported_folders(folder)
            if imported.source.file
        }


class ModuleExposure:
    """How much of each module's whole subtree code outside the subtree names. A module is measured over its own files,
    its packages, and the modules nested in it; each nested module is measured again over its own subtree. Each module
    keeps the count of the production classes in its subtree (``subtree_class_count``), the public ones with the folders
    outside the subtree that name them (``public_classes``), and how many are public and private (``public_class_count``,
    ``private_class_count``). A private record, such as a parser's ``_Section``, is neither seam nor hidden design, so it
    is not counted; a name starting with ``_`` is never public; tests and test support neither count nor name a class."""

    def __init__(self, in_graph: "PracticeNodes", classes: "ClassGraph") -> None:
        self._in_graph = in_graph
        self._classes = classes

    def record(self) -> None:
        counted = [
            (node.source.file, node.name)
            for node in self._classes.classes
            if not (node.name.startswith("_") and not self._classes.has_behavior(node))
        ]
        namers = self._namers()
        for module in self._in_graph.nodes("Module"):
            folder = module.source.file
            names = [name for file, name in counted if is_under(file, folder)]
            public = self._public(names, folder, namers)
            module.set_facts(
                {
                    "subtree_class_count": len(names),
                    "public_classes": public,
                    "public_class_count": len(public),
                    "private_class_count": len(names) - len(public),
                }
            )

    def _public(self, names: list[str], folder: str, namers: dict[str, set[str]]) -> dict[str, list[str]]:
        """The public classes among names, each with the folders outside the module's folder whose code names it."""
        public: dict[str, list[str]] = {}
        for name in sorted(set(names)):
            outside = sorted(namer for namer in namers.get(name, set()) if not is_under(namer, folder))
            if outside and not name.startswith("_"):
                public[name] = outside
        return public

    def _namers(self) -> dict[str, set[str]]:
        """Each class name production code imports or qualifies, with the folders whose code does it: the names each
        folder's files import, which the read kept on the folder by file, and the names the files outside an edited-file
        scope import, by the module that holds each, which it kept on the practice's root."""
        namers: dict[str, set[str]] = {}
        for folder in folders_of(self._in_graph):
            by_file = folder.get_fact("imported_names_by_file") if folder.has_fact("imported_names_by_file") else {}
            for name in {name for names in by_file.values() for name in names}:
                namers.setdefault(name, set()).add(folder.source.file or "")
        root = self._in_graph.root
        outside = root.get_fact("imported_names_outside") if root.has_fact("imported_names_outside") else {}
        for name, folders in outside.items():
            namers.setdefault(name, set()).update(folders)
        return namers
