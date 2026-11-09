"""One read of the code into Clean Engineering's graph: the files it parses, the folders it takes, and the class nodes
it adds and links. The practice makes one for each read (``GraphReading.read_working_copy``), so nothing one read finds
stays on the practice for the next."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.graph.skipped_folders import scanned_files, skips_folder

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    Module,
    UnreadableSource,
    class_names_imported_by,
)
from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext
from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.model.graph_reading import GraphReading
    from cdd_guidance.practices.clean_engineering.model.operation import Operation
    from cdd_guidance.practices.clean_engineering.model.property import Property

_CLASS_NAMES = re.compile(r"\bclass\s+(\w+)")
# A run of the characters a class name is spelled with: a type hint names a class when the class's name is one whole run.
_HINT_WORD = re.compile(r"[A-Za-z0-9_]+")
# The file an import names, after the path its import reads as: a Python module or package, or a script file.
_IMPORTED_FILE_ENDINGS = (".py", "/__init__.py", "", ".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js")


class CodeRead:
    """One read of the code into the practice's graph: the files it parses, the module each parses into, and the files
    that do not parse, with the reason. Made for each read, so nothing one read finds stays on the practice for the
    next. It holds the folders the read takes and the class nodes it adds."""

    def __init__(self, practice: "GraphReading") -> None:
        self._practice = practice
        self._root = Path(practice.in_graph.source_root)
        practice.graph.report_progress("clean_engineering · folders")
        self._folders = CodeFolders(practice)
        self._files = practice.graph.scope.source_files(self._root, practice.readable_suffixes)
        # The module of each file this read tried, by its resolved path; none for a file that does not parse.
        self._tried: dict[Path, Module | None] = {}
        self._modules: dict[Path, Module] = {}
        self._unreadable: dict[Path, str] = {}

    def read(self) -> None:
        """Parse the files, add the folders, classes, and members they hold, then link the types and the folders."""
        self._parse()
        self._record_public_sources()
        classes = ClassNodes(self._practice, self._class_names())
        self._folders.add()
        for file, module in self._modules.items():
            relative = file.relative_to(self._root).as_posix()
            folder = self._folders.take(relative, module)
            for cls in module.classes:
                classes.add(relative, folder, cls)
        classes.link_types()
        for file, reason in self._unreadable.items():
            self._folders.keep_unreadable(file.relative_to(self._root).as_posix(), reason)
        self._folders.link()

    def _class_names(self) -> set[str]:
        """The classes the parsed files declare, and those the files an edited-file scope leaves out declare."""
        parsed = {cls.name for module in self._modules.values() for cls in module.classes}
        return parsed | OutsideScope(self._practice, self._files).class_names()

    def _parse(self) -> None:
        for index, file in enumerate(self._files, start=1):
            relative = file.relative_to(self._root).as_posix()
            self._practice.graph.report_progress(f"clean_engineering · classes · {index}/{len(self._files)} · {relative}")
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
        loaded. A file that does not parse is kept with the reason, so the source-parses rule reports it."""
        try:
            module = self._practice.format_for(file).parse(file.read_text(encoding="utf-8")).file_module()
        except (OSError, UnicodeDecodeError) as error:
            self._unreadable[file] = f"cannot be read: {error}"
            return None
        except UnreadableSource as unreadable:
            self._unreadable[file] = str(unreadable)
            return None
        module.load_source_facts(file, self._root)
        return module

    def _record_public_sources(self) -> None:
        """Give each folder the modules of its own public source files: each one this read parsed, and each one an
        edited-file scope left out, read now. A file that cannot be read counts as a file with no documentation."""
        for folder, paths in self._folders.public_files():
            folder.take_public_sources([self._module_of(path) or Module(name=path.name, sequential_order=1) for path in paths])


class OutsideScope:
    """The source files an edited-file scope leaves out, in folders the practice holds nothing read from: their class
    names, which a type hint may still name, and the class names their production files import.

    The scope's own files are parsed and their classes named by the parse. Names in the other files come from a text
    match, so reading the files the scope leaves out stays cheap. A refresh holds every other folder as it was read, its
    classes parsed and its imports on its module, so it reads none of them again: a text match would name more than the
    parse did, and a refresh would then link and check what a fresh build does not. A whole load leaves nothing out.
    """

    def __init__(self, practice: "GraphReading", parsed: list[Path]) -> None:
        self._graph = practice.graph
        self._in_graph = practice.in_graph
        self._root = Path(practice.in_graph.source_root)
        self._suffixes = practice.readable_suffixes
        self._parsed = set(parsed)
        # The module folder that holds each folder read, by the folder; empty for one in no module.
        self._owners: dict[Path, str] = {}

    def class_names(self) -> set[str]:
        """The class names the files outside the scope declare. The practice's root keeps the class names each of their
        production files imports, by the module that holds the file, so the deep-module rule sees the callers that make
        a class public even when the scope leaves them out."""
        files = self._files()
        names: set[str] = set()
        importers: dict[str, set[str]] = {}
        for index, file in enumerate(files, start=1):
            self._graph.report_progress(f"clean_engineering · class names · {index}/{len(files)} · {file.name}")
            try:
                text = file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            names.update(_CLASS_NAMES.findall(text))
            if not is_test_code(file.relative_to(self._root).as_posix()):
                owner = self._module_folder_of(file.parent)
                for name in class_names_imported_by(text):
                    importers.setdefault(name, set()).add(owner)
        self._in_graph.root.set_fact("imported_names_outside", {name: sorted(held) for name, held in importers.items()})
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


class ClassNodes:
    """The classes one read adds to the graph, with their properties, operations, and parameters, and the class names a
    type hint may name, so the read links each member to the classes its type names once every class is added."""

    def __init__(self, practice: "GraphReading", class_names: set[str]) -> None:
        self._graph = practice.graph
        self._in_graph = practice.in_graph
        self._index = practice.code_index
        self._class_names = class_names

    def add(self, relative: str, folder: "Node", cls) -> None:
        """Add the class, its properties, and its operations; each is the object the parser built."""
        cls.load_source_facts()
        for member in [*cls.public_properties, *cls.operations]:
            member.keep_owner()
        node = self._in_graph.add(cls, f"clean_engineering:OoadClass:{relative}:{cls.name}", relative, cls.line, cls.end_line)
        self._graph.link("owns", folder, node)
        self._graph.link("belongsTo", node, folder, "relationship")
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
        for edge in self._in_graph.edges("properties"):
            self._link_property(edge.parent, edge.child)
        for operation in self._in_graph.nodes("Operation"):
            for other in self._classes_named_in(operation.get_fact("return_type")):
                self._graph.link("returns", operation, other, "relationship")

    def _property(self, relative: str, cls: "Node", prop: "Operation | Property") -> None:
        """A field the class declares, or a getter: the operation that reads it, which is the property's node. Its type
        is the field's declared type, or the type the getter returns, which ``link_types`` links once every class is
        added."""
        line = prop.line or 1
        node = self._in_graph.add(prop, f"clean_engineering:Property:{relative}:{prop.name}:{cls.name}", relative, line, line)
        self._graph.link("properties", cls, node, "grouped")

    def _operation(self, relative: str, cls: "Node", operation) -> None:
        start, end = operation.source_lines
        operation.load_span_facts()
        node = self._in_graph.add(operation, f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}", relative, start, end)
        self._graph.link("owns", cls, node)
        for parameter in operation.parameters:
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            self._graph.link("hasParameter", node, self._in_graph.add(parameter, param_id, relative, start, start), "relationship")

    def _link_property(self, cls: "Node", prop: "Node") -> None:
        """The class depends on each other class its property's type names, which the property has as its type."""
        hint = prop.get_fact("value_type")
        if not self._names_in(hint):
            return
        self._graph.link("relative", cls, prop)
        for other in self._classes_named_in(hint):
            if other.name != cls.name:
                self._graph.link("hasType", prop, other, "relationship")
                self._graph.link("dependsOn", cls, other, "relationship")

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

    def __init__(self, practice: "GraphReading") -> None:
        self._graph = practice.graph
        self._in_graph = practice.in_graph
        self._root = Path(self._in_graph.source_root)
        self._suffixes = practice.readable_suffixes
        self._modules: dict[str, Module] = self._found(self._graph.scope.folders)
        self._nodes: "dict[str, Node]" = {}
        self._imports: dict[str, list[str]] = {relative: [] for relative in self._modules}

    def public_files(self) -> list[tuple[Module, list[Path]]]:
        """Each folder's Module with its own public source files."""
        found = []
        for relative, folder in self._modules.items():
            directory = self._root / relative
            paths = (path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in self._suffixes)
            found.append((folder, sorted(path for path in paths if folder.holds_public_source(path.name))))
        return found

    def add(self) -> None:
        """Add each folder to the graph as its Module's node."""
        for relative, module in self._modules.items():
            self._nodes[relative] = self._in_graph.add(module, f"clean_engineering:{module.type}:{relative}", relative, 1, 1)

    def take(self, relative: str, module: Module) -> "Node":
        """The folder node that holds the file at relative, which keeps what the file imports when it is production
        code; the practice's root for a file in no folder read. A spec's imports are not its module's dependencies: a
        spec of a lower module may import the one above it."""
        owner = self._nearest(str(Path(relative).parent).replace("\\", "/"), self._modules)
        if not owner:
            return self._in_graph.root
        if not is_test_code(relative):
            self._imports[owner].extend(module.dependencies)
            self._nodes[owner].merge_fact("imported_names", module.imported_names)
            self._record_sibling_imports(self._nodes[owner], relative, module.dependencies)
        return self._nodes[owner]

    def keep_unreadable(self, relative: str, reason: str) -> None:
        """A file that did not parse, kept on the module that holds it, so validate reports it instead of skipping it.
        A file in no module is kept on the practice's root, which no rule checks."""
        cards = {path: module for path, module in self._modules.items() if module.type == "Module"}
        owner = self._nodes.get(self._nearest(str(Path(relative).parent).replace("\\", "/"), cards)) or self._in_graph.root
        kept = owner.get_fact("unreadable_sources") or []
        owner.set_fact("unreadable_sources", list(dict.fromkeys([*kept, f"{relative}: {reason}"])))

    def link(self) -> None:
        """Each folder is owned by the folder that encloses it, and depends on each folder its files import from."""
        held = {node.source.file: node for kind in ("Module", "Package") for node in self._in_graph.nodes(kind)}
        held.update(self._nodes)
        for relative in sorted(self._modules, key=lambda item: (item.count("/"), item)):
            folder = self._nodes[relative]
            parent = self._enclosing(relative) or self._in_graph.root
            for imported in self._imported(relative, held):
                self._graph.link("dependsOn", folder, imported, "relationship")
            self._graph.link("owns", parent, folder)
            if self._modules[relative].type == "Package":
                self._graph.link("belongsTo", folder, parent, "relationship")

    def _record_sibling_imports(self, folder: "Node", relative: str, targets: list[str]) -> None:
        """The files of its own folder a production file imports, kept on the folder by file name, so the one-way-deps
        rule sees a cycle between the files of one folder; a refresh keeps the other files' imports."""
        path = Path(relative)
        siblings = {found.name for found in (self._sibling_imported(path, target) for target in targets) if found is not None}
        kept = folder.get_fact("sibling_imports") if folder.has_fact("sibling_imports") else {}
        folder.set_fact("sibling_imports", {**kept, path.name: sorted(siblings)})

    def _sibling_imported(self, path: Path, target: str) -> Path | None:
        """The file of path's own folder an import of target names; none for a file of another folder."""
        # TypeScript names the compiled `./x.js` for its source `x.ts`.
        bases = [target, target.removesuffix(".js")] if target.endswith(".js") else [target]
        candidates = (Path(f"{base}{ending}") for base in bases for ending in _IMPORTED_FILE_ENDINGS)
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

    @staticmethod
    def _nearest(path: str, among: dict[str, Module]) -> str:
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
        card and ``Package`` when it holds only source; none for a folder with neither."""
        has_code = any(Path(name).suffix.lower() in self._suffixes for name in filenames)
        if not has_code and not (folder / ".context").is_dir():
            return None
        module = Module(name=folder.name, sequential_order=1)
        module.load_folder_facts(folder)
        if module.has_module_context:
            module.type = "Module"
        elif has_code:
            module.type = "Package"
        else:
            return None
        return module
