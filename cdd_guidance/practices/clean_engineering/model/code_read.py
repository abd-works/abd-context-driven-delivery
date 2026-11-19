"""One read of the code into Clean Engineering's graph: the files it parses, the folders it takes, and the class nodes
it adds and links, with each class a model document describes that no code declares. The practice makes one for each
read (``GraphReading.read_working_copy``), so nothing one read finds stays on the practice for the next."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.graph.skipped_folders import scanned_files, skips_folder
from harness.graph.location import Location
from harness.whiteboard.whiteboard import UnreadableBoard

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    Module,
    OoadClass,
    UnreadableSource,
)
from cdd_guidance.practices.clean_engineering.model.code_class_model import CodeCleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext
from cdd_guidance.practices.clean_engineering.model.script_imports import ScriptImports, imported_files
from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.model.graph_reading import GraphReading
    from cdd_guidance.practices.clean_engineering.model.operation import Operation
    from cdd_guidance.practices.clean_engineering.model.property import Property
    from cdd_guidance.practices.clean_engineering.model.script_imports import ClassReference

# The fact a folder's module or package keeps: whether any of its source is production code.
PRODUCTION_FACT = "holds_production_code"
# The fact a class keeps when a model document describes it and no code declares it: the design, read from the
# document, standing in for code not written yet.
DESCRIBED_FACT = "described_by_model_document"
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
        """Parse the files, add the folders, classes, and members they hold, and each class a model document describes
        that no code declares, then link the types and the folders."""
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
        DescribedClasses(self._reading, classes).add(declared)
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
            if not is_test_code(relative):
                references = ScriptImports(text).class_references(file, self._root)
                importers[relative] = {"module": self._module_folder_of(file.parent), "classes": sorted(references)}
        self._in_graph.root.set_fact("imported_classes_outside", importers)
        return names

    def _files(self) -> list[Path]:
        if self._graph.scope.edited_files is None:
            return []
        held = {node.source.file for kind in ("Module", "Package") for node in self._in_graph.nodes(kind)}
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
    """The classes the practice's model documents describe that no code declares, added as the code's classes are, so
    the model's rules check the design before its code is written. Each sits at its card in its document, owned by the
    folder the document describes (the one holding its ``.context``), else the practice's root, and keeps the fact that
    a document, not code, declares it. A class code declares keeps the code's node alone."""

    def __init__(self, reading: "GraphReading", classes: "ClassNodes") -> None:
        self._documents = reading.model_documents
        self._in_graph = reading.in_graph
        self._classes = classes

    def add(self, declared: set[str]) -> None:
        """Add each class the documents read now describe whose name no code class has, the first document's when two
        describe it; declared holds the classes this read's code declares, and the classes held from before that code
        declares count too."""
        taken = declared | {node.name for node in self._in_graph.nodes("OoadClass") if not node.has_fact(DESCRIBED_FACT)}
        folders = {node.source.file: node for kind in ("Module", "Package") for node in self._in_graph.nodes(kind)}
        for relative, oclass in self._documents.described_now():
            if oclass.name in taken:
                continue
            taken.add(oclass.name)
            described = Path(relative).parent.parent.as_posix()
            self._classes.add(relative, folders.get(described, self._in_graph.root), oclass)
            oclass.set_fact(DESCRIBED_FACT, True)
            oclass.set_fact(PRODUCTION_FACT, True)


class ClassNodes:
    """The classes one read adds to the graph, with their properties, operations, and parameters, and the class names a
    type hint may name, so the read links each member to the classes its type names once every class is added."""

    def __init__(self, reading: "GraphReading", class_names: set[str]) -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
        self._index = reading.code_index
        self._class_names = class_names

    def add(self, relative: str, folder: "Node", cls: OoadClass) -> None:
        """Add the class, its properties, and its operations; each is the object the parser built."""
        cls.source_facts.load()
        for member in [*cls.public_properties, *cls.operations]:
            member.keep_owner()
        node = self._in_graph.add(cls, f"clean_engineering:OoadClass:{relative}:{cls.name}", Location(relative, cls.line, cls.end_line))
        self._graph.edges.link("owns", folder, node)
        self._graph.edges.relate("belongsTo", node, folder)
        for prop in cls.public_properties:
            self._property(relative, node, prop)
        for operation in cls.operations:
            if not operation.is_property:
                self._operation(relative, node, operation)

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
            for other in self._classes_named_in(operation.get_fact("return_type")):
                self._graph.edges.relate("returns", operation, other)

    def _property(self, relative: str, cls: "Node", prop: "Operation | Property") -> None:
        """A field the class declares, or a getter: the operation that reads it, which is the property's node. Its type
        is the field's declared type, or the type the getter returns, which ``link_types`` links once every class is
        added."""
        line = prop.line or 1
        node = self._in_graph.add(prop, f"clean_engineering:Property:{relative}:{prop.name}:{cls.name}", Location(relative, line, line))
        self._graph.edges.group("properties", cls, node)

    def _operation(self, relative: str, cls: "Node", operation: "Operation") -> None:
        start, end = operation.source_lines
        operation.source_facts.load()
        node = self._in_graph.add(operation, f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}", Location(relative, start, end))
        self._graph.edges.link("owns", cls, node)
        for parameter in operation.parameters:
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            self._graph.edges.relate("hasParameter", node, self._in_graph.add(parameter, param_id, Location(relative, start, start)))

    def _link_property(self, cls: "Node", prop: "Node") -> None:
        """The class depends on each other class its property's type names, which the property has as its type."""
        hint = prop.get_fact("value_type")
        if not self._names_in(hint):
            return
        self._graph.edges.link("relative", cls, prop)
        for other in self._classes_named_in(hint):
            if other.name != cls.name:
                self._graph.edges.relate("hasType", prop, other)
                self._graph.edges.relate("dependsOn", cls, other)

    def _classes_named_in(self, hint: str | None) -> "list[Node]":
        """The first class the graph holds under each name the hint names."""
        return [found[0] for found in (self._index.classes_named(name) for name in self._names_in(hint)) if found]

    def _names_in(self, hint: str | None) -> list[str]:
        """The class names a type hint names, each as a whole type, not as a prefix of a longer name; a generic
        container's hint names none."""
        if not hint or "[" in hint:
            return []
        words = set(_HINT_WORD.findall(hint))
        return sorted(
            name
            for name in self._class_names
            if name in words
            or (not _HINT_WORD.fullmatch(name) and re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", hint))
        )


class CodeFolders:
    """The folders one read of the code takes, by each one's path from the source root: the folder's Module, the node it
    is added as, and what its production files import. A module owns a module card (``.context/module-context.md``);
    any other folder with source is a package. With an edited-file scope, only the folders holding those files."""

    def __init__(self, reading: "GraphReading") -> None:
        self._graph = reading.graph
        self._in_graph = reading.in_graph
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
        return not file_name.startswith("_") and not is_test_code(file_name)

    def add(self) -> None:
        """Add each folder to the graph as its Module's node."""
        for relative, module in self._modules.items():
            self._nodes[relative] = self._in_graph.add(module, f"clean_engineering:{module.type}:{relative}", Location(relative, 1, 1))

    def take(self, relative: str, module: Module) -> "Node":
        """The folder node that holds the file at relative, which keeps what the file imports when it is production
        code; the practice's root for a file in no folder read. A spec's imports are not its module's dependencies: a
        spec of a lower module may import the one above it."""
        owner = self._nearest(str(Path(relative).parent).replace("\\", "/"), self._modules)
        if not owner:
            return self._in_graph.root
        if not is_test_code(relative):
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
        held = {node.source.file: node for kind in ("Module", "Package") for node in self._in_graph.nodes(kind)}
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
        kept = folder.get_fact("imported_classes_by_file") if folder.has_fact("imported_classes_by_file") else {}
        folder.set_fact("imported_classes_by_file", {**kept, relative: sorted(references)})

    def _record_sibling_imports(self, folder: "Node", relative: str, targets: list[str]) -> None:
        """The files of its own folder a production file imports, kept on the folder by file name, so the one-way-deps
        rule sees a cycle between the files of one folder; a refresh keeps the other files' imports."""
        path = Path(relative)
        siblings = {found.name for found in (self._sibling_imported(path, target) for target in targets) if found is not None}
        kept = folder.get_fact("sibling_imports") if folder.has_fact("sibling_imports") else {}
        folder.set_fact("sibling_imports", {**kept, path.name: sorted(siblings)})

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
        module.set_fact(PRODUCTION_FACT, any(not is_test_code(f"{relative}/{name}".lstrip("/")) for name in sources))
        if module.has_module_context:
            module.type = "Module"
        elif has_code:
            module.type = "Package"
        else:
            return None
        return module
