"""One read of the code into Clean Engineering's graph: the files it parses, the folders it takes, and the class nodes
it adds and links, each class a model document describes joined to the code's node of that class, or added on its own
while no code declares it. The practice makes one for each
read (``GraphReading.read_working_copy``), so nothing one read finds stays on the practice for the next."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.graph.skipped_folders import scanned_files, skips_folder
from harness.graph.location import Location
from harness.graph.schema_conformance import EXEMPT_FACT
from harness.whiteboard import UnreadableBoard

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    Module,
    OoadClass,
    UnreadableSource,
)
from cdd_guidance.practices.clean_engineering.model.code_class_model import CodeCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES
from cdd_guidance.practices.clean_engineering.reading.folder_facts import folders_of
from cdd_guidance.practices.clean_engineering.measures.read_facts import DESCRIBED_FACT
from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext
from cdd_guidance.practices.source_code import ScriptImports, imported_files

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading
    from cdd_guidance.practices.clean_engineering.model.property import Property
    from cdd_guidance.practices.source_code import ClassReference

# The fact a folder's module or package keeps: whether any of its source is production code.
PRODUCTION_FACT = "holds_production_code"
# The module card a Module is read from, by its path from the source root: the node sits at its folder, and the card
# is the file whose text its facts and its rules come from.
CARD_FACT = "described_in"
# What a folder's production files import, kept on its node by each file: the classes, by the file's path from the source
# root, and the files of the folder itself, by the file's name.
IMPORTED_CLASSES_BY_FILE = "imported_classes_by_file"
SIBLING_IMPORTS = "sibling_imports"
# The fidelities a class is read at, by name: model while none of its operations has a body, code once one has.
MODEL_FIDELITY, CODE_FIDELITY = "model", "code"
_CLASS_NAMES = re.compile(r"\bclass\s+(\w+)")
# A run of the characters a class name is spelled with: a type hint names a class when the class's name is one whole run.
_HINT_WORD = re.compile(r"[A-Za-z0-9_]+")


# Source files are UTF-8; a byte-order mark an editor put first is read as the file's start, not as its first character.
SOURCE_ENCODING = "utf-8-sig"

class CodeRead:
    """One read of the code into the practice's graph: the files it parses, the module each parses into, and the files
    that do not parse, with the reason. Made for each read, so nothing one read finds stays on the practice for the
    next. It holds the folders the read takes and the class nodes it adds."""

    def __init__(self, reading: "GraphReading") -> None:
        self._reading = reading
        self._root = Path(reading.in_graph.source_root)
        report_progress("clean_engineering · folders")
        self._folders = CodeFolders(reading)
        self._files = reading.graph.scope.source_files(self._root, reading.practice.formats.suffixes)
        # The module of each file this read tried, by its resolved path; none for a file that does not parse.
        self._tried: dict[Path, Module | None] = {}
        self._modules: dict[Path, Module] = {}
        self._unreadable: dict[Path, str] = {}

    def read(self) -> None:
        """Parse the files, add the folders, classes, and members they hold, join or add each class a model document
        describes, then link the types and the folders."""
        self._parse()
        self._record_public_sources()
        declared = self._class_names()
        classes = ClassNodes(self._reading, set(declared))
        self._folders.add()
        for file, module in self._modules.items():
            relative = file.relative_to(self._root).as_posix()
            folder = self._folders.take(relative, module)
            for cls in module.classes:
                classes.add(relative, folder, cls)
        DescribedClasses(self._reading, classes).add()
        classes.link_types()
        for file, reason in self._unreadable.items():
            self._folders.keep_unreadable(file.relative_to(self._root).as_posix(), reason)
        self._folders.link()

    def _class_names(self) -> set[str]:
        """The classes the parsed files declare, and those the files an edited-file scope leaves out declare."""
        parsed = {cls.name for module in self._modules.values() for cls in module.classes}
        return parsed | OutsideScope(self._reading, self._files).class_names()

    def _parse(self) -> None:
        for index, file in enumerate(self._files, start=1):
            relative = file.relative_to(self._root).as_posix()
            report_progress(f"clean_engineering · classes · {index}/{len(self._files)} · {relative}")
            module = self._module_of(file)
            if module is not None:
                self._modules[file] = module

    def _module_of(self, file: Path) -> Module | None:
        """The file's module, parsed once in this read; none for a file that does not parse."""
        resolved = file.resolve()
        if resolved not in self._tried:
            self._tried[resolved] = self._parsed(file)
        return self._tried[resolved]

    def _parsed(self, file: Path) -> Module | None:
        """The file's module, read by its language's class model from the practice's formats, with its source facts
        loaded. A file that does not parse is kept with the reason, so the source-parses rule reports it. A saved board
        is a drawing, not source: one that draws no module and no class, such as a Stories story map, is another
        practice's, and one that draws Clean Engineering's modules or classes draws the design the code is read for, so
        neither holds a module and neither is kept."""
        text = self._text_of(file)
        if text is None:
            return None
        try:
            parsed = self._reading.practice.formats.for_file(file).parse(text)
        except UnreadableSource as unreadable:
            self._unreadable[file] = str(unreadable)
            return None
        except UnreadableBoard:
            return None
        if not isinstance(parsed, CodeCleanEngineeringModel):
            return None
        module = parsed.file_module()
        module.source_facts.load(file, self._root)
        return module

    def _text_of(self, file: Path) -> str | None:
        """The file's text, a byte-order mark read as its start and not as text; none for a file the disk cannot give,
        which is kept with the reason."""
        try:
            return file.read_text(encoding=SOURCE_ENCODING)
        except (OSError, UnicodeDecodeError) as error:
            self._unreadable[file] = f"cannot be read: {error}"
            return None

    def _record_public_sources(self) -> None:
        """Give each folder the modules of its own public source files: each one this read parsed, and each one an
        edited-file scope left out, read now. A file that cannot be read counts as a file with no documentation."""
        for folder, paths in self._folders.public_files():
            folder.source_facts.take_public_sources([self._module_of(path) or Module(name=path.name, sequential_order=1) for path in paths])


class OutsideScope:
    """The source files an edited-file scope leaves out, in folders the practice holds nothing read from: their class
    names, which a type hint may still name, and the classes their production files import, each with the module it
    comes from.

    The scope's own files are parsed and their classes named by the parse. Names in the other files come from a text
    match, so reading the files the scope leaves out stays cheap. A refresh holds every other folder as it was read, its
    classes parsed and its imports on its module, so it reads none of them again: a text match would name more than the
    parse did, and a refresh would then link and check what a fresh build does not. A whole load leaves nothing out.
    """

    def __init__(self, reading: "GraphReading", parsed: list[Path]) -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._test_code = reading.test_code
        self._root = Path(reading.in_graph.source_root)
        self._suffixes = reading.practice.formats.suffixes
        self._parsed = set(parsed)
        # The module folder that holds each folder read, by the folder; empty for one in no module.
        self._owners: dict[Path, str] = {}

    def class_names(self) -> set[str]:
        """The class names the files outside the scope declare. The practice's root keeps, by file, the classes each of
        their production files imports and the module that holds the file (``imported_classes_outside``), so the
        deep-module rule sees the callers that make a class public, and the re-exports they pass through, even when the
        scope leaves them out."""
        files = self._files()
        names: set[str] = set()
        importers: dict[str, dict] = {}
        for index, file in enumerate(files, start=1):
            report_progress(f"clean_engineering · class names · {index}/{len(files)} · {file.name}")
            try:
                text = file.read_text(encoding=SOURCE_ENCODING)
            except (OSError, UnicodeDecodeError):
                continue
            names.update(_CLASS_NAMES.findall(text))
            relative = file.relative_to(self._root).as_posix()
            if not self._test_code.is_test_code(relative):
                references = ScriptImports(text).class_references(file, self._root)
                importers[relative] = {"module": self._module_folder_of(file.parent), "classes": sorted(references)}
        self._in_graph.root.set_fact("imported_classes_outside", importers)
        return names

    def _files(self) -> list[Path]:
        if self._graph.scope.edited_files is None:
            return []
        held = {node.source.file for node in folders_of(self._in_graph)}
        return [
            path
            for path in scanned_files(self._root, self._suffixes)
            if path not in self._parsed and path.parent.relative_to(self._root).as_posix() not in held
        ]

    def _module_folder_of(self, folder: Path) -> str:
        """The root-relative path of the nearest folder at or above this one that holds a module card; empty for none."""
        if folder not in self._owners:
            found = folder
            while found != self._root and self._root in found.parents and not ModuleContext(found).exists():
                found = found.parent
            self._owners[folder] = found.relative_to(self._root).as_posix() if found != self._root and self._root in found.parents else ""
        return self._owners[folder]


class DescribedClasses:
    """The classes the practice's model documents describe. One class is one node, whatever formats it is written in.
    A class the code of the module a document describes declares too is the code's node: it takes the document's place
    (``Node.written_at``), the document's facts, and each member the code lacks, so the code's measures and the
    document's description sit on one node. A class no code declares yet is added at its card in its document,
    so the model's rules check the design before its code is written, owned by the folder the document describes (the
    one holding its ``.context``), else the practice's root, and keeps the fact that only a document declares it."""

    def __init__(self, reading: "GraphReading", classes: "ClassNodes") -> None:
        self._documents = reading.model_documents
        self._in_graph = reading.in_graph
        self._test_code = reading.test_code
        self._classes = classes
        self._joins = ClassJoins(reading, classes)

    def add(self) -> None:
        """Add or join each class the documents read now describe, the documents of the folders nearest the code first,
        so a class two documents describe keeps the place of the one nearest its code."""
        folders = {node.source.file: node for node in folders_of(self._in_graph)}
        described = sorted(self._documents.described_now(), key=lambda pair: -_depth(_described_folder(pair[0])))
        named = {(_described_folder(relative), oclass.name) for relative, oclass in described}
        coded = [node for node in self._in_graph.nodes("OoadClass") if not node.has_fact(DESCRIBED_FACT)]
        for relative, oclass in described:
            folder = _described_folder(relative)
            code = self._code_of(folder, oclass.name, coded, named)
            if code is not None:
                self._joins.join(relative, code, oclass)
                continue
            self._classes.add(relative, folders.get(folder, self._in_graph.root), oclass)
            oclass.set_fact(DESCRIBED_FACT, True)
            oclass.set_fact(PRODUCTION_FACT, True)

    def _code_of(self, folder: str, name: str, coded: "list[Node]", named: set[tuple[str, str]]) -> "Node | None":
        """The class the code of folder declares under name, which the document of folder describes: the one class of
        that name in a file under folder, production code before test support such as a spec's fixture of the same
        name, leaving out those a document of a folder nearer their file describes too unless every one is. A document
        names no file and no language, so where two files of the module declare the name, the class it means cannot be
        told and its class stays a node of its own."""
        found = self._declared_under(folder, name, coded)
        meant = [node for node in found if not self._nearer(node.source.file, folder, name, named)] or found
        return meant[0] if len(meant) == 1 else None

    def _declared_under(self, folder: str, name: str, coded: "list[Node]") -> "list[Node]":
        """The classes called name in files under folder: the production ones, else the test support ones."""
        under = [node for node in coded if node.name == name and _under(node.source.file, folder)]
        return [node for node in under if not self._test_code.is_test_code(node.source.file)] or under

    def _nearer(self, file: str, folder: str, name: str, named: set[tuple[str, str]]) -> bool:
        """Whether a document of a folder between folder and file describes name too."""
        parts = Path(file).parent.as_posix().split("/")
        return any(("/".join(parts[:end]), name) in named for end in range(_depth(folder) + 1, len(parts) + 1))


def _described_folder(document: str) -> str:
    """The folder a model document describes, the one holding its ``.context``: ``.`` for the practice's root."""
    return Path(document).parent.parent.as_posix()


def _depth(folder: str) -> int:
    """How many folders deep folder lies under the practice's root: 0 for the root."""
    return 0 if folder in ("", ".") else len(folder.split("/"))


def _under(file: str, folder: str) -> bool:
    """Whether file, from the practice's root, lies under folder; every file lies under the root."""
    return folder in ("", ".") or file.startswith(f"{folder}/")


class ClassNodes:
    """The classes one read adds to the graph, with their properties, operations, and parameters, and the class names a
    type hint may name, so the read links each member to the classes its type names once every class is added."""

    def __init__(self, reading: "GraphReading", class_names: set[str]) -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._index = reading.code_index
        self._class_names = class_names
        # Each relationship a person wrote on a property, as (the class's node, its kind, the class it names).
        self._written: "list[tuple[Node, str, str]]" = []

    def add(self, relative: str, folder: "Node", cls: OoadClass) -> None:
        """Add the class, its properties, and its operations; each is the object the parser built."""
        cls.source_facts.load()
        cls.properties.extend(cls.source_facts.constructor_fields())
        for member in [*cls.public_properties, *cls.operations]:
            member.keep_owner()
        node = self._in_graph.add(cls, f"clean_engineering:OoadClass:{relative}:{cls.name}", Location(relative, cls.line, cls.end_line))
        # The fidelity the class is read at goes by what it holds, in any format: code once an operation has a body,
        # else model. Its operations, properties and parameters answer the class's.
        node.read_at(CODE_FIDELITY if any(operation.has_body for operation in cls.operations) else MODEL_FIDELITY)
        self._graph.edges.link("owns", folder, node)
        self._graph.edges.relate("belongsTo", node, folder)
        self.keep_relationships(node, cls)
        shown = cls.public_properties
        for prop in shown:
            self.add_property(relative, node, prop)
        # A getter its instances do not show, a private one, is read as the operation it is, so what its body calls and
        # raises is read too.
        for operation in cls.operations:
            if not operation.is_property or not any(operation is prop for prop in shown):
                self.add_operation(relative, node, operation)

    def keep_relationships(self, node: "Node", cls: OoadClass) -> None:
        """Keep each relationship a person wrote on a property of cls, which ``link_types`` links from node once every
        class is added."""
        self._written.extend((node, prop.relationship.kind, prop.relationship.target) for prop in cls.properties if prop.stereotype and prop.relationship)

    def link_types(self) -> None:
        """Link each property to the classes its type names, and each operation to the classes it returns, once every
        class is added, so a type in a file read later still links. Every property and operation the practice holds is
        linked, those read now and those held from before, from the type each saves with the graph (``value_type``,
        ``return_type``): a refresh drops the edges to the classes of the files it reads again, and this links the
        members it did not read to the classes it read now."""
        self._class_names |= self._index.class_names()
        for edge in self._in_graph.edge_index.of("properties"):
            self._link_property(edge.parent, edge.child)
        for operation in self._in_graph.nodes("Operation"):
            for other in self._classes_named_in(operation.get_fact("return_type"), operation.source.file):
                self._graph.edges.relate("returns", operation, other)
        for cls, kind, target in self._written:
            related = self._index.file(cls.source.file).class_named(target)
            if related is not None:
                self._graph.edges.relate(kind, cls, related)

    def add_property(self, relative: str, cls: "Node", prop: "Operation | Property") -> "Node":
        """A field the class declares, or a getter: the operation that reads it, which is the property's node. Its type
        is the field's declared type, or the type the getter returns, which ``link_types`` links once every class is
        added. A getter's node spans the getter's whole body, so the calls its body makes and the failures it raises
        are read as an operation's are; a field's spans its line."""
        start, end = prop.source_lines if isinstance(prop, Operation) else (prop.line or 1, prop.line or 1)
        node = self._in_graph.add(prop, f"clean_engineering:Property:{relative}:{prop.name}:{cls.name}", Location(relative, start, end))
        self._graph.edges.group("properties", cls, node)
        return node

    def add_operation(self, relative: str, cls: "Node", operation: "Operation") -> "Node":
        start, end = operation.source_lines
        operation.source_facts.load()
        node = self._in_graph.add(operation, f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}", Location(relative, start, end))
        self._graph.edges.link("owns", cls, node)
        for parameter in operation.parameters:
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            self._graph.edges.relate("hasParameter", node, self._in_graph.add(parameter, param_id, Location(relative, start, start)))
        return node

    def _link_property(self, cls: "Node", prop: "Node") -> None:
        """The class depends on each other class its property's type names, which the property has as its type."""
        hint = prop.get_fact("value_type")
        if not self._names_in(hint):
            return
        self._graph.edges.link("relative", cls, prop)
        for other in self._classes_named_in(hint, cls.source.file):
            if other.name != cls.name:
                self._graph.edges.relate("hasType", prop, other)
                self._graph.edges.relate("dependsOn", cls, other)

    def _classes_named_in(self, hint: str | None, file: str) -> "list[Node]":
        """The class file means by each name the hint names: the one it declares or imports."""
        code_file = self._index.file(file)
        return [found for found in (code_file.class_named(name) for name in self._names_in(hint)) if found is not None]

    def _names_in(self, hint: str | None) -> list[str]:
        """The class names a type hint names, each as a whole type, not as a prefix of a longer name; a collection's
        hint names the class it holds."""
        if not hint:
            return []
        words = set(_HINT_WORD.findall(hint))
        return sorted(
            name
            for name in self._class_names
            if name in words
            or (not _HINT_WORD.fullmatch(name) and re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", hint))
        )


class ClassJoins:
    """The joining of each class a model document describes to the node of the class the code declares, which one read
    of the code makes once: the code's node takes the document's place, the document's facts by the format that
    supplies each, each relationship the document writes on a property, and each member the code does not declare, at
    the document's lines and read at the model fidelity; a member both declare takes the document's place."""

    def __init__(self, reading: "GraphReading", classes: ClassNodes) -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._classes = classes

    def join(self, relative: str, code: "Node", described: OoadClass) -> None:
        """Make the class the document at relative describes one node with code. A node the described class was
        before its code was written is dropped first."""
        described.source_facts.load()
        described.properties.extend(described.source_facts.constructor_fields())
        self._drop_held(relative, described)
        code.written_at(Location(relative, described.line, described.end_line))
        self._take_facts(code, described)
        self._classes.keep_relationships(code, described)
        declared = {edge.child.name: edge.child for kind in ("owns", "properties") for edge in self._graph.edges.from_parent(kind, code)}
        for member in [*described.public_properties, *described.operations]:
            member.keep_owner()
            self._join_member(relative, code, described, member, declared)

    def _join_member(self, relative: str, code: "Node", described: OoadClass, member: "Operation | Property", declared: "dict[str, Node]") -> None:
        """The member both declare takes the document's place; one only the document declares is added under code."""
        held = declared.get(member.name) or self._constructor_named(member.name, described.name, declared)
        if held is not None:
            start, end = member.source_lines if isinstance(member, Operation) else (member.line or 1, member.line or 1)
            held.written_at(Location(relative, start, end))
            return
        if any(member is prop for prop in described.public_properties):
            self._classes.add_property(relative, code, member).read_at(MODEL_FIDELITY)
        elif isinstance(member, Operation):
            self._classes.add_operation(relative, code, member).read_at(MODEL_FIDELITY)

    def _constructor_named(self, name: str, class_name: str, declared: "dict[str, Node]") -> "Node | None":
        """The constructor the code declares, when a document names its class's constructor by the class's name, as a
        model writes it (`+ Ledger(owner: str)`) and code does not (`__init__`, `constructor`); none for any other name."""
        if name != class_name:
            return None
        return next((declared[found] for found in sorted(CONSTRUCTOR_NAMES) if found in declared), None)

    def _take_facts(self, code: "Node", described: OoadClass) -> None:
        """Give code each fact of the described class from the format that supplies it: a list, such as the class's
        stereotypes, holds what each format names, the code's first; any other fact is the code's when its reading
        records it, else the document's."""
        for key, value in described.facts.items():
            held = code.get_fact(key) if code.has_fact(key) else None
            if isinstance(value, list) and isinstance(held, list):
                value = [*held, *(item for item in value if item not in held)]
            elif code.has_fact(key):
                continue
            code.keep_fact(key, value)

    def _drop_held(self, relative: str, described: OoadClass) -> None:
        """Drop the nodes the class the document at relative describes was held as, with their edges, while no code
        declared it: a refresh that reads the code new since keeps the document's nodes of the read before, and the
        class is one node now."""
        held = self._in_graph.node(f"clean_engineering:OoadClass:{relative}:{described.name}")
        if held is None:
            return
        owned = {id(edge.child) for kind in ("owns", "properties") for edge in self._graph.edges.from_parent(kind, held)}
        parameters = {id(edge.child) for node in self._in_graph.nodes() if id(node) in owned for edge in self._graph.edges.from_parent("hasParameter", node)}
        dropped = self._in_graph.drop({id(held), *owned, *parameters})
        self._in_graph.edge_index.drop(lambda edge: id(edge.parent) in dropped or id(edge.child) in dropped)


class CodeFolders:
    """The folders one read of the code takes, by each one's path from the source root: the folder's Module, the node it
    is added as, and what its production files import. A module owns a module card (``.context/module-context.md``);
    any other folder with source is a package. With an edited-file scope, only the folders holding those files."""

    def __init__(self, reading: "GraphReading") -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._test_code = reading.test_code
        self._root = Path(self._in_graph.source_root)
        self._suffixes = reading.practice.formats.suffixes
        self._modules: dict[str, Module] = self._found(self._graph.scope.folders)
        self._nodes: "dict[str, Node]" = {}
        self._imports: dict[str, list[str]] = {relative: [] for relative in self._modules}

    def public_files(self) -> list[tuple[Module, list[Path]]]:
        """Each folder's Module with its own public source files."""
        found = []
        for relative, folder in self._modules.items():
            directory = self._root / relative
            paths = (path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in self._suffixes)
            found.append((folder, sorted(path for path in paths if self._is_public_source(path.name))))
        return found

    def _is_public_source(self, file_name: str) -> bool:
        """True for a file of a folder other modules may read: production code whose name does not start with `_`."""
        return not file_name.startswith("_") and not self._test_code.is_test_code(file_name)

    def add(self) -> None:
        """Add each folder to the graph as its Module's node. A folder the graph holds already, as a refresh of one of
        its files finds it, keeps its node, which takes what the folder says now."""
        for relative, module in self._modules.items():
            node = self._in_graph.add(module, f"clean_engineering:{module.type}:{relative}", Location(relative, 1, 1))
            if node is not module:
                self._read_again(node, relative, module)
            self._nodes[relative] = node

    def _read_again(self, node: "Node", relative: str, module: Module) -> None:
        """Give node, the folder's node a read before added, the facts the folder's Module read now holds, and keep
        what its files import only for the files still in it, so it holds what a node read anew holds: a file added
        counts among its public files, and a file deleted or moved away leaves no import behind. A fact the read
        works out again on every node, such as which relationships test code is exempt from, starts afresh."""
        for key, fact in module.facts.items():
            node.keep_fact(key, fact)
        node.forget_fact(EXEMPT_FACT)
        folder = self._root / relative
        in_folder = lambda name: (folder / name).is_file()
        self._keep_files_still_there(node, IMPORTED_CLASSES_BY_FILE, lambda file: (self._root / file).is_file())
        self._keep_files_still_there(node, SIBLING_IMPORTS, in_folder, lambda imported: [name for name in imported if in_folder(name)])

    def _keep_files_still_there(self, node: "Node", key: str, still_there, kept_of=lambda held: held) -> None:
        """Keep the fact at key only for the files still there, each with what it holds that is still there; a sibling a
        file imported and that was deleted or moved away is no longer imported, as a read anew finds it."""
        kept = {file: kept_of(held) for file, held in (node.get_fact(key) if node.has_fact(key) else {}).items() if still_there(file)}
        if kept:
            node.set_fact(key, kept)
        else:
            node.forget_fact(key)

    def take(self, relative: str, module: Module) -> "Node":
        """The folder node that holds the file at relative, which keeps what the file imports when it is production
        code; the practice's root for a file in no folder read. A spec's imports are not its module's dependencies: a
        spec of a lower module may import the one above it."""
        owner = self._nearest(str(Path(relative).parent).replace("\\", "/"), self._modules)
        if not owner:
            return self._in_graph.root
        if not self._test_code.is_test_code(relative):
            self._imports[owner].extend(module.dependencies)
            self._record_imported_classes(self._nodes[owner], relative, module.imported_classes)
            self._record_sibling_imports(self._nodes[owner], relative, module.dependencies)
        return self._nodes[owner]

    def keep_unreadable(self, relative: str, reason: str) -> None:
        """A file that did not parse, kept on the module that holds it, so validate reports it instead of skipping it.
        A file in no module is kept on the folder that holds it; only a file in no folder read is kept on the
        practice's root, which no rule checks."""
        folder = str(Path(relative).parent).replace("\\", "/")
        cards = {path: module for path, module in self._modules.items() if module.type == "Module"}
        owner = self._nodes.get(self._nearest(folder, cards)) or self._nodes.get(self._nearest(folder, self._modules)) or self._in_graph.root
        kept = (owner.get_fact("unreadable_sources") or []) if owner.has_fact("unreadable_sources") else []
        owner.set_fact("unreadable_sources", list(dict.fromkeys([*kept, f"{relative}: {reason}"])))

    def link(self) -> None:
        """Each folder is owned by the folder that encloses it, and depends on each folder its files import from."""
        held = {node.source.file: node for node in folders_of(self._in_graph)}
        held.update(self._nodes)
        for relative in sorted(self._modules, key=lambda item: (item.count("/"), item)):
            folder = self._nodes[relative]
            parent = self._enclosing(relative) or self._in_graph.root
            for imported in self._imported(relative, held):
                self._graph.edges.relate("dependsOn", folder, imported)
            self._graph.edges.link("owns", parent, folder)
            if self._modules[relative].type == "Package":
                self._graph.edges.relate("belongsTo", folder, parent)

    def _record_imported_classes(self, folder: "Node", relative: str, references: "list[ClassReference]") -> None:
        """The classes a production file imports, re-exports, or qualifies, each with the module it names it from, kept
        on its folder by the file's path, so a refresh that reads the file again replaces what it named before and
        keeps what the folder's other files name."""
        kept = folder.get_fact(IMPORTED_CLASSES_BY_FILE) if folder.has_fact(IMPORTED_CLASSES_BY_FILE) else {}
        folder.set_fact(IMPORTED_CLASSES_BY_FILE, {**kept, relative: sorted(references)})

    def _record_sibling_imports(self, folder: "Node", relative: str, targets: list[str]) -> None:
        """The files of its own folder a production file imports, kept on the folder by file name, so the one-way-deps
        rule sees a cycle between the files of one folder; a refresh keeps the other files' imports."""
        path = Path(relative)
        siblings = {found.name for found in (self._sibling_imported(path, target) for target in targets) if found is not None}
        kept = folder.get_fact(SIBLING_IMPORTS) if folder.has_fact(SIBLING_IMPORTS) else {}
        folder.set_fact(SIBLING_IMPORTS, {**kept, path.name: sorted(siblings)})

    def _sibling_imported(self, path: Path, target: str) -> Path | None:
        """The file of path's own folder an import of target names; none for a file of another folder."""
        candidates = (Path(item) for item in imported_files(target))
        own = path.parent.as_posix()
        return next((item for item in candidates if item.parent.as_posix() == own and item != path and (self._root / item).is_file()), None)

    def _enclosing(self, relative: str) -> "Node | None":
        parent = str(Path(relative).parent).replace("\\", "/")
        owner = self._nearest(parent, self._modules) if parent != "." else ""
        return self._nodes[owner] if owner else None

    def _imported(self, relative: str, held: "dict[str, Node]") -> "list[Node]":
        """The graph folder each of the folder's imports lands in (longest match); imports of the folder itself drop out."""
        found: "dict[str, Node]" = {}
        for target in self._imports[relative]:
            parts = target.split("/")
            while parts and "/".join(parts) not in held:
                parts.pop()
            folder = "/".join(parts)
            if folder and folder != relative:
                found[folder] = held[folder]
        return [found[folder] for folder in sorted(found)]

    def _nearest(self, path: str, among: dict[str, Module]) -> str:
        """The path of the nearest folder of among at or above path; empty for none."""
        current = path
        while current and current != ".":
            if current in among:
                return current
            parent = str(Path(current).parent).replace("\\", "/")
            if parent == current:
                break
            current = "" if parent == "." else parent
        return ""

    def _found(self, scope: list[Path] | None) -> dict[str, Module]:
        """Each folder read, by its path from the root: the folders of the scope, or every folder under the root."""
        if scope is not None:
            found = {folder.relative_to(self._root).as_posix(): self._folder_module(folder, os.listdir(folder)) for folder in scope}
            return {relative: module for relative, module in found.items() if module is not None}
        folders: dict[str, Module] = {}
        for dirpath, dirnames, filenames in os.walk(self._root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            folder = Path(dirpath)
            module = self._folder_module(folder, filenames) if folder != self._root else None
            if module is not None:
                folders[folder.relative_to(self._root).as_posix()] = module
        return folders

    def _folder_module(self, folder: Path, filenames: list[str]) -> Module | None:
        """The folder's Module, made once with its folder, which holds its card: typed ``Module`` when it holds a module
        card and ``Package`` when it holds only source; none for a folder with neither. It records whether any of its
        source is production code: a folder of specs and story tests alone is test code, held to no relationship the
        schema requires."""
        relative = folder.relative_to(self._root).as_posix() if folder != self._root else ""
        sources = [name for name in filenames if Path(name).suffix.lower() in self._suffixes]
        has_code = bool(sources)
        if not has_code and not (folder / ".context").is_dir():
            return None
        module = Module(name=folder.name, sequential_order=1)
        module.source_facts.load_folder(folder)
        module.set_fact(PRODUCTION_FACT, any(not self._test_code.is_test_code(f"{relative}/{name}".lstrip("/")) for name in sources))
        if module.has_module_context:
            module.type = "Module"
            module.set_fact(CARD_FACT, f"{relative}/.context/module-context.md".lstrip("/"))
        elif has_code:
            module.type = "Package"
        else:
            return None
        return module
