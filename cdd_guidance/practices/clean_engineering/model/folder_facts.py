"""How a compared fact is written on a node, and the facts each folder of the code keeps about the other folders: the
imports of it that close a cycle and the sibling modules it imports. What of a module's subtree leaves it is
``module_exposure.py``'s."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.import_cycles import ImportCycles

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes
    from harness.graph.saved_graph import FactValue

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
