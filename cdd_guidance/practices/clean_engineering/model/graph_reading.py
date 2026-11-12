"""How Clean Engineering takes part in the graph: it reads each source file with the class model of its language, from
its own formats, and adds the folders, classes, properties, operations, and parameters it parsed to its graph as nodes;
and it keeps the class models its model documents describe, so a realization can follow an interaction the model gives
a member.

The practice holds two parts for as long as it lives, its code index and its model documents, and makes a code read,
with the folders that read takes, for each read: what one read finds stays on that read, not on the practice."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.graph import Node
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.practice_reading import PracticeReading
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import skips_folder
from harness.graph.schema_conformance import EXEMPT_FACT

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.code_read import CodeRead
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

# A member called on another object (`board.select(`), and a property read on one (`board.shown`, no call after it).
_ABSTRACT_MARK = re.compile(r"@abstractmethod|^\s*(?:public\s+|protected\s+)?abstract\s", re.MULTILINE)
_DOCSTRING = re.compile(r'(?s)\A\s*(?:"""|\'\'\').*?(?:"""|\'\'\')')
# The marker the source view puts after a line for each call on it, `/* call:show */`, which is no code.
_CALL_MARKER = re.compile(r"\s*/\* call:[^*]*\*/")
_NO_BODY = {"", "...", "pass", "raise NotImplementedError", "raise NotImplementedError()"}
_MEMBER_CALL = re.compile(r"\.([A-Za-z_$][\w$]*)\s*\(")
_MEMBER_READ = re.compile(r"\.([A-Za-z_$][\w$]*)\b(?!\s*\()")


class GraphReading(PracticeReading):
    """How Clean Engineering takes part in the graph: it reads the code, then the model documents. Its classes are the
    classes the source view opens and folds, their operations and properties the members it opens a call to, and its
    checks run on each class as a whole. Every practice that links to the code asks its code index; a realization asks
    its model documents."""

    class_types = ("OoadClass",)
    member_types = ("Operation", "Property")
    class_node_type = "OoadClass"
    anchor_types = {
        "module": "Module",
        "class": "OoadClass",
        "property": "Property",
        "operation": "Operation",
        "parameter": "Parameter",
        "package": "Package",
    }

    def __init__(self, practice: PracticeGuidance) -> None:
        super().__init__(practice)
        self.code_index = CodeIndex(self)
        self.model_documents = ModelDocuments(self)

    def read_working_copy(self) -> None:
        """Read each source file with its language's class model, adding the folders, classes, properties, operations,
        and parameters it parsed as nodes, and keep the class model each model document describes."""
        self.code_index.forget()
        with schema_sync_paused():
            CodeRead(self).read()
            self.model_documents.read()
        CallLinks(self).link()


class CallLinks:
    """The ``invokes`` edges of the code read: each operation and property to the operations and properties its body
    calls, found by the name each call ends in (``board.show()`` calls ``show``), a member of its own class before
    another class's member of that name."""

    def __init__(self, reading: GraphReading) -> None:
        self._reading = reading
        self._graph = reading.graph

    def link(self) -> None:
        """Record an ``invokes`` edge from every member the graph holds to each member it calls."""
        in_graph = self._reading.in_graph
        for caller in [*in_graph.nodes("Operation"), *in_graph.nodes("Property")]:
            called = self._called_by(caller)
            for member in called:
                self._graph.link("invokes", caller, member, "relationship")
            if not called and self._calls_nothing_by_design(caller):
                caller.set_fact(EXEMPT_FACT, ["invokes"])

    def _calls_nothing_by_design(self, caller: Node) -> bool:
        """Whether caller is a member that has nothing to call: an abstract one, whose subclasses do the work, or one
        that takes nothing and answers a value, which is a property in all but name."""
        return self._is_abstract(caller) or not self._graph.edges_from("hasParameter", caller)

    def _is_abstract(self, caller: Node) -> bool:
        """An abstract member: marked so (`@abstractmethod`, `abstract`), or with no body but `...`, `pass`, or a raise of
        NotImplementedError under its signature and docstring."""
        text = caller.source.text if caller.source.file else ""
        if _ABSTRACT_MARK.search(text) or self._declared_without_body(text):
            return True
        return _DOCSTRING.sub("", self._python_body(text)).strip() in _NO_BODY

    @staticmethod
    def _declared_without_body(text: str) -> bool:
        """A C-family member with no body: its signature ends in `;` and no brace opens a body (an interface's method,
        `draw(scale: number): void;`, or `void draw(double scale);`)."""
        code = _CALL_MARKER.sub("", text).strip()
        return bool(code) and "{" not in code and code.endswith(";")

    def _python_body(self, text: str) -> str:
        """What follows a Python member's signature, the line that ends its `def` with a colon; none for other code."""
        lines = text.splitlines()
        if not any(line.lstrip().startswith(("def ", "async def ")) for line in lines[:4]):
            return ""
        end = next((index for index, line in enumerate(lines) if line.rstrip().endswith(":")), len(lines))
        return "\n".join(lines[end + 1:])

    def _called_by(self, caller: Node) -> list[Node]:
        """The members caller calls, by the names its callees end in and the members its source calls on another object
        (``this.board.select()``, which its callees leave out when it shares caller's name), and the properties its
        source reads (``this.board.shown``); its own class's member of a name when its class has one."""
        text = caller.source.text if caller.source.file else ""
        calls = {str(callee).rsplit(".", 1)[-1] for callee in caller.get_fact("callees") or [] if callee}
        calls.update(_MEMBER_CALL.findall(text))
        reads = set(_MEMBER_READ.findall(text)) - calls
        found = [member for name in calls for member in self._named(name, caller)]
        found.extend(member for name in reads for member in self._named(name, caller) if member.type == "Property")
        return found

    def _named(self, name: str, caller: Node) -> list[Node]:
        """The members called name other than caller, only its own class's when its class has one."""
        owner = self._graph.direct_parent(caller)
        members = [member for member in self._reading.code_index.members_named(name) if member is not caller]
        return [member for member in members if self._graph.direct_parent(member) is owner] or members


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
        """The operations and properties called name, each class's operation before its property."""
        if self._members is None:
            in_graph = self._reading.in_graph
            self._members = self._indexed([*in_graph.nodes("Operation"), *in_graph.nodes("Property")])
        return self._members.get(name, [])

    def _class_index(self) -> dict[str, list[Node]]:
        if self._classes is None:
            self._classes = self._indexed(sorted(self._reading.in_graph.nodes("OoadClass"), key=lambda node: node.node_id))
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

    def __init__(self, reading: GraphReading) -> None:
        self._reading = reading
        # The format the practice's model documents are written in, which reads each into the class model it describes.
        self._format: type[CleanEngineeringModel] = reading.practice.model_document_format
        self._models: dict[str, CleanEngineeringModel] = {}
        # Whether the documents have been read for the graph the practice is in.
        self._read = False

    def read(self) -> None:
        """Read the documents of the folders in scope. A refresh reads only some documents, so the models the others
        describe stay; a whole load reads them all again."""
        graph = self._reading.graph
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
        return Path(self._reading.in_graph.source_root)

    def _files(self) -> list[Path]:
        """Each scoped folder's and each of its parents' ``.context/*-model.md``, up to the root, as the graph's scope
        names them. ``.context`` is a skipped folder, so the code scan never reaches them."""
        graph = self._reading.graph
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
