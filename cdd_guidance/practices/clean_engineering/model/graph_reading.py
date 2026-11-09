"""How Clean Engineering takes part in the graph: it reads each source file with the class model of its language, from
its own formats, and adds the folders, classes, properties, operations, and parameters it parsed to its graph as nodes;
and it keeps the class models its model documents describe, so a realization can follow an interaction the model gives
a member.

The practice holds two parts for as long as it lives, its code index and its model documents, and makes a code read,
with the folders that read takes, for each read: what one read finds stays on that read, not on the practice."""

from __future__ import annotations

import os
from pathlib import Path

from harness.graph.graph import Graph, Node
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.code_read import CodeRead
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property


class GraphReading:
    """Clean Engineering's operations over the graph it is read in: reading the code, then the model documents. Every
    practice that links to the code asks its code index; a realization asks its model documents."""

    graph: Graph

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.code_index = CodeIndex(self)
        self.model_documents = ModelDocuments(self)

    def read_working_copy(self) -> None:
        """Read each source file with its language's class model, adding the folders, classes, properties, operations,
        and parameters it parsed as nodes, and keep the class model each model document describes."""
        self.code_index.forget()
        with schema_sync_paused():
            CodeRead(self).read()
            self.model_documents.read()


class CodeIndex:
    """The code read into the practice's graph, by name: its classes, and its operations and properties. Made once after
    each read, the first time a reader asks, so the type linking, every rule, and every practice that links to the code
    ask one index, and a graph read back from its saved file answers from the nodes it restored."""

    def __init__(self, practice: GraphReading) -> None:
        self._practice = practice
        self._classes: dict[str, list[Node]] | None = None
        self._members: dict[str, list[Node]] | None = None

    def forget(self) -> None:
        """Drop the index, so the next question after a read indexes what the read added."""
        self._classes = None
        self._members = None

    def classes_named(self, name: str) -> list[Node]:
        """The classes the graph holds called name, in the order of their node ids."""
        return self._class_index().get(name, [])

    def class_names(self) -> set[str]:
        """The name of every class the graph holds."""
        return set(self._class_index())

    def members_named(self, name: str) -> list[Node]:
        """The operations and properties called name, each class's operation before its property."""
        if self._members is None:
            in_graph = self._practice.in_graph
            self._members = self._indexed([*in_graph.nodes("Operation"), *in_graph.nodes("Property")])
        return self._members.get(name, [])

    def _class_index(self) -> dict[str, list[Node]]:
        if self._classes is None:
            self._classes = self._indexed(sorted(self._practice.in_graph.nodes("OoadClass"), key=lambda node: node.node_id))
        return self._classes

    @staticmethod
    def _indexed(nodes: list[Node]) -> dict[str, list[Node]]:
        found: dict[str, list[Node]] = {}
        for node in nodes:
            found.setdefault(node.name, []).append(node)
        return found


class ModelDocuments:
    """The class models the practice's model documents describe, ``{folder}/.context/*-model.md``, by each document's
    path from the source root. A realization follows an interaction into a class the load left out through them,
    without a second copy of the class among the code's nodes."""

    def __init__(self, practice: GraphReading) -> None:
        self._practice = practice
        # The format the practice's model documents are written in, which reads each into the class model it describes.
        self._format: type[CleanEngineeringModel] = practice.model_document_format
        self._models: dict[str, CleanEngineeringModel] = {}
        # Whether the documents have been read for the graph the practice is in.
        self._read = False

    def read(self) -> None:
        """Read the documents of the folders in scope. A refresh reads only some documents, so the models the others
        describe stay; a whole load reads them all again."""
        graph = self._practice.graph
        if graph.scope.edited_files is None or not self._read:
            self._models = {}
        self._read = True
        for file in self._files():
            relative = file.relative_to(self._root).as_posix()
            graph.report_progress(f"clean_engineering · model · {relative}")
            self._models[relative] = self._format().parse(file.read_text(encoding="utf-8"))

    def described_member(self, owner: str, name: str) -> Operation | Property | None:
        """The operation or property a document describes as owner.name; none when none does. A graph read back from a
        saved file reads the documents under its source root the first time it is asked."""
        if not self._read:
            self.read()
        found = (model.described_member(owner, name) for model in self._models.values())
        return next((member for member in found if member is not None), None)

    @property
    def _root(self) -> Path:
        return Path(self._practice.in_graph.source_root)

    def _files(self) -> list[Path]:
        """Each scoped folder's and each of its parents' ``.context/*-model.md``, up to the root, as the graph's scope
        names them. ``.context`` is a skipped folder, so the code scan never reaches them."""
        graph = self._practice.graph
        edited = graph.scope.edited_files
        folders = self._every_folder() if edited is None else {self._root, *(graph.scope.folders or [])}
        named = {path for path in (edited or []) if path.name.endswith("-model.md")}
        return sorted({model for folder in folders for model in (folder / ".context").glob("*-model.md")} | named)

    def _every_folder(self) -> set[Path]:
        folders = set()
        for dirpath, dirnames, _files in os.walk(self._root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            folders.add(Path(dirpath))
        return folders


def parameters_of(operation: Node) -> list[Node]:
    """The parameters an operation takes, in the order it declares them: the nodes its hasParameter edges lead to, which
    a graph read back from its saved file keeps too."""
    return [edge.child for edge in operation.graph.edges_from("hasParameter", operation)]
