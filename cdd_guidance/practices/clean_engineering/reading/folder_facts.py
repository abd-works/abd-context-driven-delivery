"""How a compared fact is written on a node, and the facts each folder of the code keeps about the other folders: the
imports of it that close a cycle and the sibling modules it imports. What of a module's subtree leaves it is
``module_exposure.py``'s."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.reading.import_cycles import ImportCycles

if TYPE_CHECKING:
    from harness.graph.graph import Node, PracticeNodes
    from harness.graph.saved_graph import FactValue

# The node types a folder of code is read as: a module, which has a module card, or a package, which has none.
FOLDER_TYPES = ("Module", "Package")


def record_fact(node: "Node", key: str, fact: "FactValue") -> None:
    """Record fact on node when it says something, or when the node holds an older answer the fact replaces: a node a
    refresh kept holds the facts of the build before, and a node that never found anything keeps no empty fact, so the
    saved graph stays small."""
    if fact or node.has_fact(key):
        node.set_fact(key, fact)


def own_fact(node: "Node", key: str) -> "FactValue":
    """The fact node itself records, or none: what ``record_fact`` left. A node that records no fact of its own would
    otherwise answer the nearest ancestor's (``Node.get_fact``), so a module would report its parent module's finding."""
    return node.get_fact(key) if node.has_fact(key) else None


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
    return [folder for kind in FOLDER_TYPES for folder in in_graph.nodes(kind)]


def imported_folders(folder: "Node") -> list["Node"]:
    """The folders folder depends on: the nodes its ``dependsOn`` edges lead to."""
    return [edge.child for edge in folder.graph.edges.from_parent("dependsOn", folder)]


class FolderImportCycles:
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


class ModuleImports:
    """The imports between modules, which every module measure reads. A module is a folder that owns a module card; a
    folder with source and no card is a package, a part of the nearest module above it, so a module imports what it
    and every package inside it import, counted as the modules that hold the folders imported, never as packages and
    never as itself. Each module keeps the paths of the modules it imports (``imported_modules``), of the modules that
    import it (``importing_modules``), and the modules it imports that close a loop of modules (``module_import_loops``:
    the module imported and the loop's size). A package keeps none of them."""

    IMPORTED, IMPORTING, LOOPS = "imported_modules", "importing_modules", "module_import_loops"

    def __init__(self, in_graph: "PracticeNodes") -> None:
        self._modules = {module.source.file: module for module in in_graph.nodes("Module") if module.source.file}
        self._folders = folders_of(in_graph)

    def record(self) -> None:
        imports: dict[str, set[str]] = {path: set() for path in self._modules}
        for folder in self._folders:
            importer = self._owner(folder.source.file)
            for imported in imported_folders(folder):
                owner = self._owner(imported.source.file)
                if importer and owner and owner != importer:
                    imports[importer].add(owner)
        importing: dict[str, set[str]] = {path: set() for path in self._modules}
        for importer, imported in imports.items():
            for path in imported:
                importing[path].add(importer)
        loops: dict[str, list[list]] = {path: [] for path in self._modules}
        for importer, imported, size in ImportCycles(imports).imports_in_cycles():
            loops[importer].append([self._modules[imported].name, size])
        for path, module in self._modules.items():
            module.set_fact(self.IMPORTED, sorted(imports[path]))
            module.set_fact(self.IMPORTING, sorted(importing[path]))
            module.set_fact(self.LOOPS, loops[path])

    def _owner(self, path: str | None) -> str:
        """The path of the module that holds the folder at path: the nearest module at or above it; empty for none."""
        held = [module for module in self._modules if is_under(path, module)]
        return max(held, key=len, default="")


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
