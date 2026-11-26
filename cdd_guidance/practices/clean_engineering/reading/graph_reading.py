"""How Clean Engineering takes part in the graph: it reads each source file with the class model of its language, from
its own formats, and adds the folders, classes, properties, operations, and parameters it parsed to its graph as nodes;
a class its model documents describe is the same node as the class its code declares, and is added on its own while
no code declares it, so the rules check a design whose code is not written; and it keeps the class models those
documents describe, so a realization can follow an interaction the model gives a member.

The practice holds two parts for as long as it lives, its code index and its model documents, and makes a code read,
with the folders that read takes, for each read: what one read finds stays on that read, not on the practice."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.agent_tools.progress import report_progress
from harness.graph.graph import Node
from harness.guidance.guidance import PracticeGuidance
from harness.graph.node_metric import NodeMetric
from harness.graph.practice_reading import PracticeReading
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder
from harness.graph.schema_conformance import EXEMPT_FACT

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER, CleanEngineeringModel, OoadClass
from cdd_guidance.practices.clean_engineering.measures.checked_measures import CheckedCodeMeasures
from cdd_guidance.practices.clean_engineering.measures.code_measures import MEASURES, NODE_TYPES, SHOWN_WITHOUT_LIMIT, ChosenTools
from cdd_guidance.practices.clean_engineering.measures.measuring_tools import TOOLS, MeasuringTool
from cdd_guidance.practices.clean_engineering.reading.call_links import CallLinks, ClassLinks, FieldLinks
from cdd_guidance.practices.clean_engineering.reading.statement_links import StatementLinks
from cdd_guidance.practices.clean_engineering.model import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.reading.code_file import CREATED_IN_THE_CONSTRUCTOR, CREATED_ON_EACH_CALL, CodeFile, CodeSpan, MemberAnswers
from cdd_guidance.practices.clean_engineering.reading.code_read import PRODUCTION_FACT, CodeRead
from cdd_guidance.practices.clean_engineering.measures.read_facts import DESCRIBED_FACT
from cdd_guidance.practices.clean_engineering.reading.compared_facts import ComparedFacts
from cdd_guidance.practices.clean_engineering.reading.folder_facts import FOLDER_TYPES, folders_of
from cdd_guidance.practices.clean_engineering.reading.card_lines import CardLines
from cdd_guidance.practices.clean_engineering.reading.node_evidence import CodeNodeTypes
from cdd_guidance.practices.source_code import ClassReference, HoldsProjectTestCode, ScriptImports
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property


class GraphReading(HoldsProjectTestCode, PracticeReading):
    """How Clean Engineering takes part in the graph: it reads the model documents, then the code, and holds a class a
    document describes and code declares as one node, written in both. Its classes are the classes the source view
    opens and folds, their operations and properties the members it opens a call to, and its checks run on each class
    as a whole. Every practice that links to the code asks its code index; a realization asks its model documents."""

    class_types = ("OoadClass",)
    member_types = ("Operation", "Property")
    class_node_type = "OoadClass"
    folder_types = frozenset(FOLDER_TYPES)
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
        # The tools a project's choices name, by that name; a spec stands its own in for an outside tool here.
        self.measuring_tools: dict[str, type[MeasuringTool]] = dict(TOOLS)
        self._chosen_tools: tuple[str, ChosenTools] | None = None

    @property
    def chosen_tools(self) -> ChosenTools:
        """The tool and the limit the project it reads chose for each code measure, read once for each project: the
        project of the session the practice works in, else the folder the graph reads the practice from. No folder
        above that one is looked in, so a sample or a fixture kept inside a project that measures its code is not
        measured by that project's choices."""
        session = self.practice.session
        folder = session.checkout.root if session is not None else self.in_graph.source_root_path if self.in_graph is not None else None
        root = str(folder) if folder is not None else ""
        if self._chosen_tools is None or self._chosen_tools[0] != root:
            self._chosen_tools = (root, ChosenTools.of_project(Path(root).resolve()) if root else ChosenTools(None))
        return self._chosen_tools[1]

    metric_node_types = tuple(node_type for node_types in NODE_TYPES.values() for node_type in node_types)

    def metrics_of(self, node: Node) -> list[NodeMetric]:
        """The measures of production code a limit rule reads on node, each with its value and the project's limit:
        the one list the limit rules and the explorer tree's metrics group both read. After them come the measures
        shown for information (``SHOWN_WITHOUT_LIMIT``), each with its value and no limit. A project that holds its
        code to no limit has none, and neither does test code, which no production rule judges."""
        chosen = self.chosen_tools
        if node.type not in self.metric_node_types or not chosen.measures_code or self.test_code.is_test_code(node.source.file):
            return []
        limited = [(measure, chosen.limit(measure)) for measure in MEASURES if node.type in NODE_TYPES[measure.of]]
        held = [(measure, limit, measure.value_on(node)) for measure, limit in limited if limit is not None or measure in SHOWN_WITHOUT_LIMIT]
        return [NodeMetric(measure.name, measure.label, value, limit, measure.least) for measure, limit, value in held if value is not None]

    def keep_code_measures(self, files: list[Path]) -> None:
        """Keep the code measures of files as facts on the functions, classes and modules read from them, each supplied
        by the tool the project chose for the measure in the file's language, so the limit rules read them as they read
        any fact. A project whose config chooses no tools keeps none."""
        if files and self.chosen_tools.measures_code:
            report_progress("clean_engineering · code measures")
            CheckedCodeMeasures(self, files, self.chosen_tools, self.measuring_tools).take()

    def read_working_copy(self) -> None:
        """Keep the class model each model document describes, then read each source file with its language's class
        model, adding the folders, classes, properties, operations, and parameters it parsed as nodes, and each class a
        document describes. A read that names its files, as the refresh a validate asks for does, keeps the code
        measures of those files as facts too; a read of the whole working copy keeps none, because a measuring tool run
        over every file would slow every load of the graph."""
        self.code_index.forget()
        # The project's choices are read again with each read, so a limit changed in its config holds from the next one.
        self._chosen_tools = None
        with schema_sync_paused():
            self.model_documents.read()
            CodeRead(self).read()
        ClassLinks(self).link()
        CallLinks(self).link()
        StatementLinks(self).link()
        FieldLinks(self).link()
        ComparedFacts(self).record()
        self.keep_code_measures(list(self.graph.scope.edited_files or []))
        self._exempt_test_code()

    def _exempt_test_code(self) -> None:
        """A spec, a test, or test support is no part of the model the schema describes, as no production rule judges it
        either: none of its nodes, and no folder holding only them, is held to the relationships its type requires."""
        requirements = self.in_graph.rule_run.schema.requirements
        for node in self.in_graph.nodes():
            if not self.test_code.is_test_code(node.source.file) and node.get_fact(PRODUCTION_FACT, True):
                continue
            fields = {requirement.field for requirement in requirements if node.type in requirement.owner.node_types}
            if fields:
                node.merge_fact(EXEMPT_FACT, list(fields))


class CodeIndex:
    """The code read into the practice's graph, by name: its classes, and its operations and properties, and each file as
    its code names things (*CodeFile*). Made once after each read, the first time a reader asks, so the type linking,
    every rule, and every practice that links to the code ask one index, and a graph read back from its saved file
    answers from the nodes it restored."""

    def __init__(self, reading: GraphReading) -> None:
        self._reading = reading
        self._classes: dict[str, list[Node]] | None = None
        self._members: dict[str, list[Node]] | None = None
        # The classes each production file imports, by its path, as its folder kept them.
        self._imports: dict[str, list[ClassReference]] | None = None
        self._files: dict[str, CodeFile] = {}
        # The classes that extend or satisfy each class, by its id, read once the inheritance edges are linked.
        self._extended_by: dict[int, list[Node]] | None = None
        # What each member answers where the code writes no type hint for it, read once per index.
        self.answers = MemberAnswers(self)

    def forget(self) -> None:
        """Drop the index, so the next question after a read indexes what the read added."""
        self._classes = None
        self._members = None
        self._imports = None
        self._files = {}
        self._extended_by = None
        self.answers = MemberAnswers(self)

    @property
    def source_root(self) -> str:
        """The folder the code read is read from, which each node's file is named from."""
        return str(self._reading.in_graph.source_root)

    def class_declaring(self, member: Node) -> Node | None:
        """The class that declares member; none for a module's function."""
        owner = member.get_fact("owner")
        if not owner or owner == MODULE_FUNCTION_HOLDER:
            return None
        return next((node for node in self.classes_named(owner) if node.source.file == member.source.file), None)

    def constructors_of(self, declared: Node) -> list[Node]:
        """The constructor the class declared writes; none when it writes none."""
        return [
            member for constructor in sorted(CONSTRUCTOR_NAMES) for member in self.members_named(constructor)
            if member.type == "Operation" and member.get_fact("owner") == declared.name and member.source.file == declared.source.file
        ]

    def operations_of(self, declared: Node) -> list[Node]:
        """The operations the class declared owns, in the order the read added them."""
        return [edge.child for edge in self._reading.graph.edges.from_parent("owns", declared) if edge.child.type == "Operation"]

    def span_of(self, member: Node) -> CodeSpan:
        """The member's own code, the class that declares it, the type hint of each of its parameters, and how an object
        it builds is reached: in the constructor for a constructor or a field, whose initializer runs as its object is
        built, else on each call."""
        text = CodeSpan.code_of(member.source.text) if member.source.file else ""
        typed = {edge.child.name: str(edge.child.get_fact("type_hint") or "") for edge in self._reading.graph.edges.from_parent("hasParameter", member)}
        builds = member.name in CONSTRUCTOR_NAMES or (member.type == "Property" and not member.get_fact("is_property"))
        return CodeSpan(text, self.class_declaring(member), typed, creates=CREATED_IN_THE_CONSTRUCTOR if builds else CREATED_ON_EACH_CALL)

    def file(self, relative: str, imports: list[ClassReference] | None = None) -> CodeFile:
        """The file at relative, from the source root, as its code names things. A production file's imports are those
        its folder kept; a file the read keeps no imports for, such as a spec, is given the imports its text names."""
        if imports is not None:
            return CodeFile(self, relative, imports, self._reading.graph.scope.over_whole)
        if relative not in self._files:
            kept = self._imports_of(relative) if self.has_imports(relative) else self._imports_written_in(relative)
            self._files[relative] = CodeFile(self, relative, kept, self._reading.graph.scope.over_whole)
        return self._files[relative]

    def _imports_written_in(self, relative: str) -> list[ClassReference]:
        """The classes and functions the text of a file the read keeps no imports for imports, such as test support
        (`rule_examples.py`, `spec_support.py`) or a spec's own helpers, so a call it makes on a class it imports is
        joined as a production file's is; none for a file that cannot be read."""
        text = self.answers.text_of(relative)
        if not text:
            return []
        root = Path(self.source_root)
        return ScriptImports(text).class_references(root / relative, root)

    def has_imports(self, relative: str) -> bool:
        """Whether the read keeps the imports of the file at relative, as it does for each production file it read."""
        self._imports_of(relative)
        return relative in (self._imports or {})

    def _imports_of(self, relative: str) -> list[ClassReference]:
        if self._imports is None:
            self._imports = {}
            for folder in folders_of(self._reading.in_graph):
                kept = folder.get_fact("imported_classes_by_file") if folder.has_fact("imported_classes_by_file") else {}
                for file, references in kept.items():
                    self._imports[file] = [ClassReference(*reference) for reference in references]
        return self._imports.get(relative, [])

    def subclasses_of(self, declared: Node) -> list[Node]:
        """Every class that extends declared, at any depth, or satisfies it when it is a protocol, as the read's
        inheritance and realization edges (``baseClass``, ``realizes``) say."""
        if self._extended_by is None:
            self._extended_by = {}
            for edge in [*self._reading.in_graph.edge_index.of("baseClass"), *self._reading.in_graph.edge_index.of("realizes")]:
                self._extended_by.setdefault(id(edge.child), []).append(edge.parent)
        extended_by = self._extended_by
        found: list[Node] = []
        waiting = [declared]
        while waiting:
            for sub in extended_by.get(id(waiting.pop()), []):
                if sub not in found and sub is not declared:
                    found.append(sub)
                    waiting.append(sub)
        return found

    def is_protocol(self, declared: Node) -> bool:
        """Whether declared is a protocol, a class others satisfy by declaring its members (`class Washer(Protocol)`)."""
        return any(str(base).split("[")[0].rsplit(".", 1)[-1].strip() == "Protocol" for base in declared.get_fact("bases") or [])

    def common_base(self, classes: list[Node]) -> Node | None:
        """The nearest class every one of classes is or extends; none when they share none."""
        lines = [self._lineage(declared) for declared in classes]
        return next((candidate for candidate in lines[0] if all(candidate in line for line in lines[1:])), None) if lines else None

    def _lineage(self, declared: Node) -> list[Node]:
        """The class, then each class it extends, nearest first."""
        line = [declared]
        for current in line:
            line.extend(edge.child for edge in self._reading.graph.edges.from_parent("baseClass", current) if edge.child not in line)
        return line

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
    read joins each class they describe to the code's node of it, or adds it at the document's lines."""

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
