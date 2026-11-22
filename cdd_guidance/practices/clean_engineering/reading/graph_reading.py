"""How Clean Engineering takes part in the graph: it reads each source file with the class model of its language, from
its own formats, and adds the folders, classes, properties, operations, and parameters it parsed to its graph as nodes;
it adds each class its model documents describe, beside the code that implements it, so the rules check a design whose code
is not written; and it keeps the class models those documents describe, so a realization can follow an interaction the
model gives a member.

The practice holds two parts for as long as it lives, its code index and its model documents, and makes a code read,
with the folders that read takes, for each read: what one read finds stays on that read, not on the practice."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.agent_tools.progress import report_progress
from harness.graph.graph import Node
from harness.guidance.guidance import PracticeGuidance
from harness.graph.practice_reading import PracticeReading
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder
from harness.graph.schema_conformance import EXEMPT_FACT

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER, CleanEngineeringModel, OoadClass
from cdd_guidance.practices.clean_engineering.reading.call_links import CallLinks, ClassesInReach, ClassLinks
from cdd_guidance.practices.clean_engineering.reading.code_read import DESCRIBED_FACT, PRODUCTION_FACT, CodeRead
from cdd_guidance.practices.clean_engineering.reading.compared_facts import ComparedFacts
from cdd_guidance.practices.clean_engineering.reading.card_lines import CardLines
from cdd_guidance.practices.clean_engineering.reading.node_evidence import CodeNodeTypes
from cdd_guidance.practices.source_code import is_test_code
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property


class GraphReading(PracticeReading):
    """How Clean Engineering takes part in the graph: it reads the model documents, then the code, and holds each class
    a document describes as it holds the code's, each joined to the code class that implements it. Its classes are the classes the source view
    opens and folds, their operations and properties the members it opens a call to, and its checks run on each class
    as a whole. Every practice that links to the code asks its code index; a realization asks its model documents."""

    class_types = ("OoadClass",)
    member_types = ("Operation", "Property")
    class_node_type = "OoadClass"
    types = CodeNodeTypes()
    anchor_types = {
        "module": "Module",
        "class": "OoadClass",
        "property": "Property",
        "operation": "Operation",
        "parameter": "Parameter",
        "package": "Package",
    }

    def owner_of(self, node: Node) -> str:
        """The class an operation or property belongs to; none for a module's function, which the class model gathers
        under a holder of its own (``MODULE_FUNCTION_HOLDER``)."""
        owner = super().owner_of(node)
        return "" if owner == MODULE_FUNCTION_HOLDER else owner

    def __init__(self, practice: PracticeGuidance) -> None:
        super().__init__(practice)
        self.code_index = CodeIndex(self)
        self.model_documents = ModelDocuments(self)

    def read_working_copy(self) -> None:
        """Keep the class model each model document describes, then read each source file with its language's class
        model, adding the folders, classes, properties, operations, and parameters it parsed as nodes, and each class a
        document describes."""
        self.code_index.forget()
        reach = ClassesInReach(self)
        with schema_sync_paused():
            self.model_documents.read()
            CodeRead(self, reach).read()
        ClassLinks(self, reach).link()
        CallLinks(self, reach).link()
        ComparedFacts(self).record()
        self._exempt_test_code()

    def _exempt_test_code(self) -> None:
        """A spec, a test, or test support is no part of the model the schema describes, as no production rule judges it
        either: none of its nodes, and no folder holding only them, is held to the relationships its type requires."""
        requirements = self.in_graph.rule_run.schema.requirements
        for node in self.in_graph.nodes():
            if not is_test_code(node.source.file) and node.get_fact(PRODUCTION_FACT, True):
                continue
            fields = {requirement.field for requirement in requirements if node.type in requirement.owner.node_types}
            if fields:
                node.merge_fact(EXEMPT_FACT, list(fields))


class CodeIndex:
    """The code read into the practice's graph, by name: its classes, and its operations and properties. Made once after
    each read, the first time a reader asks, so the type linking, every rule, and every practice that links to the code
    ask one index, and a graph read back from its saved file answers from the nodes it restored."""

    def __init__(self, reading: GraphReading) -> None:
        self._reading = reading
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
        """The operations and properties called name, each class's operation before its property, the code's before
        those a model document describes."""
        if self._members is None:
            in_graph = self._reading.in_graph
            members = [*in_graph.nodes("Operation"), *in_graph.nodes("Property")]
            self._members = self._indexed(sorted(members, key=lambda node: not self._is_code(node)))
        return self._members.get(name, [])

    def _class_index(self) -> dict[str, list[Node]]:
        """The classes by name, the code's before those a model document describes, then in the order of their ids."""
        if self._classes is None:
            classes = sorted(self._reading.in_graph.nodes("OoadClass"), key=lambda node: (node.has_fact(DESCRIBED_FACT), node.node_id))
            self._classes = self._indexed(classes)
        return self._classes

    def _is_code(self, member: Node) -> bool:
        """Whether a member is read from code, not from a model document, whose files are markdown."""
        return not member.source.file.endswith(".md")

    def _indexed(self, nodes: list[Node]) -> dict[str, list[Node]]:
        found: dict[str, list[Node]] = {}
        for node in nodes:
            found.setdefault(node.name, []).append(node)
        return found


class ModelDocuments:
    """The class models the practice's model documents describe, ``{folder}/.context/*-model.md``, by each document's
    path from the source root; a document another practice reads in a format of its own, such as DDD's domain model,
    is that practice's. A realization follows an interaction into a class the load left out through them, and the code
    read adds each class they describe, placed at the document's lines."""

    def __init__(self, reading: GraphReading) -> None:
        self._reading = reading
        # The format the practice's model documents are written in, which reads each into the class model it describes.
        self._format: type[CleanEngineeringModel] = reading.practice.model_document_format
        self._models: dict[str, CleanEngineeringModel] = {}
        # The documents the last read read, by path from the source root: a refresh reads only some.
        self._read_now: list[str] = []
        # Whether the documents have been read for the graph the practice is in.
        self._read = False

    def read(self) -> None:
        """Read the documents of the folders in scope. A refresh reads only some documents, so the models the others
        describe stay; a whole load reads them all again."""
        graph = self._reading.graph
        if graph.scope.edited_files is None or not self._read:
            self._models = {}
        self._read = True
        self._read_now = []
        for file in self._files():
            relative = file.relative_to(self._root).as_posix()
            report_progress(f"clean_engineering · model · {relative}")
            text = self._text_of(file)
            model = self._model_described_by(text)
            lines = CardLines(text)
            for oclass in self._classes_of(model):
                lines.place(oclass)
            self._models[relative] = model
            self._read_now.append(relative)

    def described_now(self) -> list[tuple[str, OoadClass]]:
        """Each class the documents the last read read describe, with its document's path from the source root, in the
        order the documents and their cards give them."""
        return [(relative, oclass) for relative in self._read_now for oclass in self._classes_of(self._models[relative])]

    def _classes_of(self, model: CleanEngineeringModel) -> list[OoadClass]:
        return [oclass for module in model.modules for oclass in module.classes]

    def _text_of(self, file: Path) -> str:
        """The text of one model document, as it is on disk now."""
        return file.read_text(encoding="utf-8")

    def _model_described_by(self, text: str) -> CleanEngineeringModel:
        """The class model a document's text describes, read in the practice's model document format."""
        return self._format().parse(text)

    def described_member(self, owner: str, name: str) -> Operation | Property | None:
        """The operation or property a document describes as owner.name; none when none does. A graph read back from a
        saved file reads the documents under its source root the first time it is asked."""
        if not self._read:
            self.read()
        found = (model.described_member(owner, name) for model in self._models.values())
        return next((member for member in found if member is not None), None)

    @property
    def _root(self) -> Path:
        return Path(self._reading.in_graph.source_root)

    def _files(self) -> list[Path]:
        """Each scoped folder's and each of its parents' ``.context/*-model.md``, up to the root, as the graph's scope
        names them. ``.context`` is a skipped folder, so the code scan never reaches them."""
        graph = self._reading.graph
        edited = graph.scope.edited_files
        folders = self._every_folder() if edited is None else {self._root, *(graph.scope.folders or [])}
        named = {path for path in (edited or []) if path.name.endswith("-model.md")}
        found = {model for folder in folders for model in (folder / ".context").glob("*-model.md")} | named
        return sorted(document for document in found if not self._read_by_another_practice(document))

    def _read_by_another_practice(self, document: Path) -> bool:
        """Whether another practice the graph holds reads the document in a model format of its own."""
        own = self._reading.practice
        held = self._reading.graph.practices.held.values()
        return any(practice is not own and practice.reading.reads_model_document(document) for practice in held)

    def _every_folder(self) -> set[Path]:
        folders = set()
        for dirpath, dirnames, _files in os.walk(self._root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            folders.add(Path(dirpath))
        return folders
