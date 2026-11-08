"""How Clean Engineering takes part in the graph: it reads each source file with the class model of its language, from
its own formats, and adds the folders, classes, properties, operations, and parameters it parsed to its graph as nodes;
and it keeps the class models its model documents describe, so a realization can follow an interaction the model gives
a member."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.graph import Graph, Node
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import scanned_files, skips_folder

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    UnreadableSource,
    class_names_imported_by,
)
from cdd_guidance.practices.clean_engineering.model.module_context_files import ModuleContext
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.model.production_code import is_test_code

_CLASS_NAMES = re.compile(r"\bclass\s+(\w+)")
# The file an import names, after the path its import reads as: a Python module or package, or a script file.
_IMPORTED_FILE_ENDINGS = (".py", "/__init__.py", "", ".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js")


class GraphReading:
    """Clean Engineering's operations over the graph it is read in: reading the code, then the model documents."""

    graph: Graph
    # The format the practice's model documents are written in, which reads each into the class model it describes.
    model_document_format: type[CleanEngineeringModel]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # The class model each model document read describes, by the document's path from the source root.
        self._model_documents: dict[str, CleanEngineeringModel] = {}
        # Whether the model documents have been read for the graph this practice is in.
        self._documents_read = False
        # The operations and properties of the code read, by name; made the first time a reader asks after a read.
        self._members_by_name: dict[str, list[Node]] | None = None

    def read_working_copy(self) -> None:
        """Read each source file with its language's class model, adding the folders, classes, properties, operations,
        and parameters it parsed as nodes, and keep the class model each model document describes."""
        self._members_by_name = None
        with schema_sync_paused():
            self._read_code()
            self._read_model_documents()

    def described_member(self, owner: str, name: str) -> Operation | Property | None:
        """The operation or property a Clean Engineering model document describes as owner.name; none when none does.
        A graph read back from a saved file reads the documents under its source root the first time it is asked."""
        if not self._documents_read:
            self._read_model_documents()
        for model in self._model_documents.values():
            found = model.described_member(owner, name)
            if found is not None:
                return found
        return None

    def members_named(self, name: str) -> list[Node]:
        """The operations and properties of the code read into the graph that are called name, each class's operation
        before its property: one index of the graph's members, made once after each read, which every practice that
        links to the code asks."""
        if self._members_by_name is None:
            self._members_by_name = {}
            for member in [*self.in_graph.nodes("Operation"), *self.in_graph.nodes("Property")]:
                self._members_by_name.setdefault(member.name, []).append(member)
        return self._members_by_name.get(name, [])

    ## the code

    @property
    def _source_root(self) -> Path:
        return Path(self.in_graph.source_root)

    def _read_code(self) -> None:
        self.graph.report_progress("clean_engineering · folders")
        folders = self._code_folders(self.graph.scope_folders())
        files = self.graph.source_files(self._source_root, self.readable_suffixes)
        modules = self._parsed_modules(files)
        self._record_public_sources(folders, modules)
        self._class_names = {cls.name for module in modules.values() for cls in module.classes}
        self._class_names |= self._read_unparsed(self._unparsed_declaring_files(files))
        nodes = {rel: self.in_graph.add(module, f"clean_engineering:{module.type}:{rel}", rel, 1, 1) for rel, module in folders.items()}
        imports: dict[str, list[str]] = {rel: [] for rel in folders}
        for file, module in modules.items():
            relative = file.relative_to(self._source_root).as_posix()
            owner = _nearest(str(Path(relative).parent).replace("\\", "/"), folders)
            # A spec's imports are not its module's dependencies: a spec of a lower module may import the one above it.
            if owner and not is_test_code(relative):
                imports[owner].extend(module.dependencies)
                nodes[owner].merge_fact("imported_names", module.imported_names)
                self._record_sibling_imports(nodes[owner], relative, module.dependencies)
            for cls in module.classes:
                self._class(relative, nodes.get(owner) or self.in_graph.root, cls)
        self._record_unreadable(folders, nodes)
        self._link_folders(folders, nodes, imports)

    def _parsed_modules(self, files: list[Path]) -> dict:
        """Each source file's module, read by its language's class model, with its source facts loaded. A file that does
        not parse is kept in ``_unreadable`` with the reason, so the source-parses rule reports it."""
        self._unreadable: dict[Path, str] = {}
        modules: dict = {}
        for index, file in enumerate(files, start=1):
            self.graph.report_progress(f"clean_engineering · classes · {index}/{len(files)} · {file.relative_to(self._source_root).as_posix()}")
            try:
                modules[file] = self._parsed_module(file)
            except (OSError, UnicodeDecodeError) as error:
                self._unreadable[file] = f"cannot be read: {error}"
            except UnreadableSource as unreadable:
                self._unreadable[file] = str(unreadable)
        return modules

    def _parsed_module(self, file: Path) -> Module:
        """The file's module, read by its language's class model from the practice's formats, with its source facts
        loaded. Raises UnreadableSource for a file its language cannot read."""
        module = self.format_for(file).parse(file.read_text(encoding="utf-8")).file_module()
        module.load_source_facts(file, self._source_root)
        return module

    def _record_public_sources(self, folders: dict, modules: dict) -> None:
        """Give each folder the modules of its own public source files: each one this load parsed, and each one an
        edited-file scope left out, read now. A file that cannot be read counts as a file with no documentation."""
        parsed = {file.resolve(): module for file, module in modules.items()}
        unreadable = {file.resolve() for file in self._unreadable}
        for rel, folder in folders.items():
            directory = self._source_root / rel
            public = sorted(
                path
                for path in directory.iterdir()
                if path.is_file() and path.suffix.lower() in self.readable_suffixes and folder.holds_public_source(path.name)
            )
            folder.take_public_sources([parsed.get(path.resolve()) or self._module_read_now(path, unreadable) for path in public])

    def _module_read_now(self, file: Path, unreadable: set[Path]) -> Module:
        """The module of a file this load did not parse; an empty one for a file that cannot be read."""
        if file.resolve() not in unreadable:
            try:
                return self._parsed_module(file)
            except (OSError, UnicodeDecodeError, UnreadableSource):
                pass
        return Module(name=file.name, sequential_order=1)

    def _unparsed_declaring_files(self, files: list[Path]) -> list[Path]:
        """The source files outside an edited-file scope, whose class names a type hint may still name.

        The scope's own files are parsed and their classes named by the parse. Names in the other files come from a
        text match, so reading the files the scope leaves out stays cheap.
        """
        if self.graph.edited_files() is None:
            return []
        parsed = set(files)
        return [path for path in scanned_files(self._source_root, self.readable_suffixes) if path not in parsed]

    def _read_unparsed(self, files: list[Path]) -> set[str]:
        """The class names the files outside the scope declare. The practice's root keeps the class names each of their
        production files imports, by the module that holds the file, so the deep-module rule sees the callers that make
        a class public even when the scope leaves them out."""
        names: set[str] = set()
        importers: dict[str, set[str]] = {}
        owners: dict[Path, str] = {}
        for index, file in enumerate(files, start=1):
            self.graph.report_progress(f"clean_engineering · class names · {index}/{len(files)} · {file.name}")
            try:
                text = file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            names.update(_CLASS_NAMES.findall(text))
            if is_test_code(file.relative_to(self._source_root).as_posix()):
                continue
            if file.parent not in owners:
                owners[file.parent] = self._module_folder_of(file.parent)
            for name in class_names_imported_by(text):
                importers.setdefault(name, set()).add(owners[file.parent])
        self.in_graph.root.set_fact("imported_names_outside", {name: sorted(held) for name, held in importers.items()})
        return names

    def _module_folder_of(self, folder: Path) -> str:
        """The root-relative path of the nearest folder at or above this one that holds a module card; empty for none."""
        root = self._source_root
        while folder != root and root in folder.parents:
            if ModuleContext(folder).exists():
                return folder.relative_to(root).as_posix()
            folder = folder.parent
        return ""

    def _record_sibling_imports(self, folder: Node, relative: str, targets: list[str]) -> None:
        """The files of its own folder a production file imports, kept on the folder by file name, so the one-way-deps
        rule sees a cycle between the files of one folder; a refresh keeps the other files' imports."""
        path = Path(relative)
        own = path.parent.as_posix()
        siblings = set()
        for target in targets:
            # TypeScript names the compiled `./x.js` for its source `x.ts`.
            bases = [target, target.removesuffix(".js")] if target.endswith(".js") else [target]
            candidates = (Path(f"{base}{ending}") for base in bases for ending in _IMPORTED_FILE_ENDINGS)
            found = next(
                (item for item in candidates if item.parent.as_posix() == own and item != path and (self._source_root / item).is_file()),
                None,
            )
            if found is not None:
                siblings.add(found.name)
        kept = folder.get_fact("sibling_imports") if folder.has_fact("sibling_imports") else {}
        folder.set_fact("sibling_imports", {**kept, path.name: sorted(siblings)})

    def _record_unreadable(self, folders: dict, nodes: dict) -> None:
        """Each file that did not parse, on the module that holds it, so validate reports it instead of skipping it.
        A file in no module is kept on the practice's root, which no rule checks."""
        modules = {rel: module for rel, module in folders.items() if module.type == "Module"}
        for file, reason in self._unreadable.items():
            relative = file.relative_to(self._source_root).as_posix()
            owner = nodes.get(_nearest(str(Path(relative).parent).replace("\\", "/"), modules)) or self.in_graph.root
            kept = owner.get_fact("unreadable_sources") or []
            owner.set_fact("unreadable_sources", list(dict.fromkeys([*kept, f"{relative}: {reason}"])))

    def _link_folders(self, folders: dict, nodes: dict, imports: dict[str, list[str]]) -> None:
        """Each folder is owned by the folder that encloses it, and depends on each folder its files import from."""
        held = {node.source.file: node for kind in ("Module", "Package") for node in self.in_graph.nodes(kind)}
        held.update(nodes)
        for rel in sorted(folders, key=lambda item: (item.count("/"), item)):
            parent = _enclosing(rel, folders, nodes) or self.in_graph.root
            folder = nodes[rel]
            for imported in _imported_folders(imports[rel], held, rel):
                self.graph.link("dependsOn", folder, imported, "relationship")
            self.graph.link("owns", parent, folder)
            if folders[rel].type == "Package":
                self.graph.link("belongsTo", folder, parent, "relationship")

    def _class(self, relative: str, folder: Node, cls) -> None:
        """Add the class, its properties, and its operations; each is the object the parser built."""
        cls.load_source_facts()
        node = self.in_graph.add(cls, f"clean_engineering:OoadClass:{relative}:{cls.name}", relative, cls.line, cls.end_line)
        self.graph.link("owns", folder, node)
        self.graph.link("belongsTo", node, folder, "relationship")
        for prop in cls.public_properties:
            self._property(relative, node, prop)
        for operation in cls.operations:
            if not operation.is_property:
                self._operation(relative, node, operation)

    def _property(self, relative: str, cls: Node, prop: Operation | Property) -> None:
        """A field the class declares, or a getter: the operation that reads it, which is the property's node. Its type
        is the field's declared type, or the type the getter returns."""
        prop_id = f"clean_engineering:Property:{relative}:{prop.name}:{cls.name}"
        line = prop.line or 1
        hint = prop.value_type or ""
        node = self.in_graph.add(prop, prop_id, relative, line, line)
        self.graph.link("properties", cls, node, "grouped")
        named = _classes_named_in(hint, self._class_names)
        if not named:
            return
        self.graph.link("relative", cls, node)
        for other in named:
            other_node = self._class_named(other) if other != cls.name else None
            if other_node is not None:
                self.graph.link("hasType", node, other_node, "relationship")
                self.graph.link("dependsOn", cls, other_node, "relationship")

    def _operation(self, relative: str, cls: Node, operation) -> None:
        start, end = operation.source_lines
        operation.load_span_facts()
        node = self.in_graph.add(operation, f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}", relative, start, end)
        self.graph.link("owns", cls, node)
        for parameter in operation.parameters:
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            self.graph.link("hasParameter", node, self.in_graph.add(parameter, param_id, relative, start, start), "relationship")
        for other in _classes_named_in(operation.return_type or "", self._class_names):
            other_node = self._class_named(other)
            if other_node is not None:
                self.graph.link("returns", node, other_node, "relationship")

    def _code_folders(self, scope: list[Path] | None) -> dict:
        """A module owns a module card (``.context/module-context.md``). Any other folder with source is a package.
        Each is the folder's Module, made once with its folder, which holds its card. With a scope, only those folders
        are read."""
        root = self._source_root
        if scope is not None:
            found = {folder.relative_to(root).as_posix(): self._folder_module(folder, os.listdir(folder)) for folder in scope}
            return {rel: module for rel, module in found.items() if module is not None}
        folders: dict = {}
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            folder = Path(dirpath)
            rel = folder.relative_to(root)
            module = self._folder_module(folder, filenames) if rel != Path(".") else None
            if module is not None:
                folders[rel.as_posix()] = module
        return folders

    def _folder_module(self, folder: Path, filenames: list[str]) -> Module | None:
        """The folder's Module, typed ``Module`` when it holds a module card and ``Package`` when it holds only source;
        none for a folder with neither."""
        has_code = any(Path(name).suffix.lower() in self.readable_suffixes for name in filenames)
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

    def _class_named(self, name: str) -> Node | None:
        return next((node for node in self.in_graph.nodes("OoadClass") if node.name == name), None)

    ## the model documents

    def _read_model_documents(self) -> None:
        """The Clean Engineering model documents for the folders in scope, ``{folder}/.context/*-model.md``, each kept
        as the class model it describes, so a realization can follow an interaction into a class the load left out
        without a second copy of the class among the code's nodes. A refresh reads only some documents, so the models
        the others describe stay; a whole load reads them all again."""
        if self.graph.edited_files() is None or not self._documents_read:
            self._model_documents = {}
        self._documents_read = True
        for file in self._model_files():
            relative = file.relative_to(self._source_root).as_posix()
            self.graph.report_progress(f"clean_engineering · model · {relative}")
            self._model_documents[relative] = self.model_document_format().parse(file.read_text(encoding="utf-8"))

    def _model_files(self) -> list[Path]:
        """Each scoped folder's and each of its parents' ``.context/*-model.md``, up to the root. ``.context`` is a
        skipped folder, so the code scan never reaches them."""
        edited = self.graph.edited_files()
        folders = self._every_folder() if edited is None else self._folders_holding(edited)
        named = {path for path in (edited or []) if path.name.endswith("-model.md")}
        return sorted({model for folder in folders for model in (folder / ".context").glob("*-model.md")} | named)

    def _every_folder(self) -> set[Path]:
        folders = set()
        for dirpath, dirnames, _files in os.walk(self._source_root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            folders.add(Path(dirpath))
        return folders

    def _folders_holding(self, edited: list[Path]) -> set[Path]:
        root = self._source_root
        folders = set()
        for path in edited:
            folder = path if path.is_dir() else path.parent
            while folder == root or root in folder.parents:
                folders.add(folder)
                if folder == root:
                    break
                folder = folder.parent
        return folders


def parameters_of(operation: Node) -> list[Node]:
    """The parameters an operation takes, in the order it declares them: the nodes its hasParameter edges lead to, which
    a graph read back from its saved file keeps too."""
    return [edge.child for edge in operation.graph.edges_from("hasParameter", operation)]


def _nearest(path: str, folders: dict) -> str:
    current = path
    while current and current != ".":
        if current in folders:
            return current
        parent = str(Path(current).parent).replace("\\", "/")
        if parent == current:
            break
        current = "" if parent == "." else parent
    return ""


def _enclosing(path: str, folders: dict, nodes: dict):
    parent = str(Path(path).parent).replace("\\", "/")
    owner = _nearest(parent, folders) if parent != "." else ""
    return nodes[owner] if owner else None


def _imported_folders(targets: list[str], held: dict, own: str) -> list:
    """The graph folder each import lands in (longest match); imports of the folder itself drop out."""
    found: dict = {}
    for target in targets:
        parts = target.split("/")
        while parts and "/".join(parts) not in held:
            parts.pop()
        folder = "/".join(parts)
        if folder and folder != own:
            found[folder] = held[folder]
    return [found[folder] for folder in sorted(found)]


def _classes_named_in(hint: str, class_names: set[str]) -> list[str]:
    """The classes a type hint names, each as a whole type, not as a prefix of a longer name; a generic container's hint
    names none."""
    if not hint or "[" in hint:
        return []
    return sorted(name for name in class_names if re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", hint))
