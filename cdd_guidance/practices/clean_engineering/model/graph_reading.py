"""How Clean Engineering takes part in the graph: it reads each source file with the class model of its language, from
its own formats, and adds the folders, classes, properties, operations, and parameters it parsed to its graph as nodes;
and it keeps the members its model documents describe on the practice's root."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.graph import Graph, Node, Source
from harness.graph.model_node import schema_sync_paused
from harness.graph.skipped_folders import scanned_files, skips_folder

CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py"}
_CLASS_NAMES = re.compile(r"\bclass\s+(\w+)")
# What the operation rules measure on a body; a getter's Property node records them for its getter.
_GETTER_MEASURES = ("line_count", "max_control_flow_depth", "has_bare_catch", "swallows_exceptions")


class GraphReading:
    """Clean Engineering's operations over the graph it is read in: reading the code, then the model documents."""

    graph: Graph

    def read_working_copy(self) -> None:
        """Read each source file with its language's class model, adding the folders, classes, properties, operations,
        and parameters it parsed as nodes, and keep the members the model documents describe on the practice's root."""
        with schema_sync_paused():
            self._read_code()
            self._read_model_documents()

    ## the code

    @property
    def _source_root(self) -> Path:
        return Path(self.graph.source_root_of(self))

    def _read_code(self) -> None:
        self.graph.report_progress("clean_engineering · folders")
        folders = _code_folders(self._source_root, self.graph.scope_folders())
        files = self.graph.source_files(self._source_root, CODE_SUFFIXES)
        modules = self._parsed_modules(files)
        self._class_names = {cls.name for module in modules.values() for cls in module.classes}
        self._class_names |= self._class_names_in(self._unparsed_declaring_files(files))
        nodes = {rel: self.graph.add(self, module, f"clean_engineering:{module.type}:{rel}", rel, 1, 1) for rel, module in folders.items()}
        imports: dict[str, list[str]] = {rel: [] for rel in folders}
        for file, module in modules.items():
            relative = file.relative_to(self._source_root).as_posix()
            owner = _nearest(str(Path(relative).parent).replace("\\", "/"), folders)
            if owner:
                imports[owner].extend(module.dependencies)
                self._record_imported_names(nodes[owner], relative, module)
            for cls in module.classes:
                self._class(relative, nodes.get(owner) or self.graph.root_of(self), cls)
        self._record_unreadable(folders, nodes)
        self._link_folders(folders, nodes, imports)

    def _parsed_modules(self, files: list[Path]) -> dict:
        """Each source file's module, read by its language's class model, with its source facts loaded. A file that does
        not parse is kept in ``_unreadable`` with the reason, so the source-parses rule reports it."""
        from cdd_guidance.practices.clean_engineering.model.base_class_model import UnreadableSource

        self._unreadable: dict[Path, str] = {}
        modules: dict = {}
        for index, file in enumerate(files, start=1):
            self.graph.report_progress(f"clean_engineering · classes · {index}/{len(files)} · {file.relative_to(self._source_root).as_posix()}")
            try:
                text = file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as error:
                self._unreadable[file] = f"cannot be read: {error}"
                continue
            try:
                module = self.code_model_for(file).parse(text).file_module()
            except UnreadableSource as unreadable:
                self._unreadable[file] = str(unreadable)
                continue
            module.load_source_facts(file, self._source_root)
            modules[file] = module
        return modules

    def _unparsed_declaring_files(self, files: list[Path]) -> list[Path]:
        """The source files outside an edited-file scope, whose class names a type hint may still name.

        The scope's own files are parsed and their classes named by the parse. Names in the other files come from a
        text match, so reading the files the scope leaves out stays cheap.
        """
        if self.graph.edited_files() is None:
            return []
        parsed = set(files)
        return [path for path in scanned_files(self._source_root, CODE_SUFFIXES) if path not in parsed]

    def _class_names_in(self, files: list[Path]) -> set[str]:
        names = set()
        for index, file in enumerate(files, start=1):
            self.graph.report_progress(f"clean_engineering · class names · {index}/{len(files)} · {file.name}")
            try:
                names.update(_CLASS_NAMES.findall(file.read_text(encoding="utf-8")))
            except (OSError, UnicodeDecodeError):
                continue
        return names

    def _record_imported_names(self, folder: Node, relative: str, module) -> None:
        """The class names a production file imports, kept on its folder for the deep-module rule; a refresh keeps the
        names the folder's other files import."""
        from cdd_guidance.practices.clean_engineering.model.rules_shared.typed_and_comments import is_test_code

        if not is_test_code(relative):
            _merge_fact(folder, "imported_names", module.imported_names)

    def _record_unreadable(self, folders: dict, nodes: dict) -> None:
        """Each file that did not parse, on the module that holds it, so validate reports it instead of skipping it.
        A file in no module is kept on the practice's root, which no rule checks."""
        modules = {rel: module for rel, module in folders.items() if module.type == "Module"}
        for file, reason in self._unreadable.items():
            relative = file.relative_to(self._source_root).as_posix()
            owner = nodes.get(_nearest(str(Path(relative).parent).replace("\\", "/"), modules)) or self.graph.root_of(self)
            kept = owner.get_fact("unreadable_sources") or []
            owner.set_fact("unreadable_sources", list(dict.fromkeys([*kept, f"{relative}: {reason}"])))

    def _link_folders(self, folders: dict, nodes: dict, imports: dict[str, list[str]]) -> None:
        """Each folder is owned by the folder that encloses it, and depends on each folder its files import from."""
        held = {node.source.file: node for kind in ("Module", "Package") for node in self.graph.nodes_of(self, kind)}
        held.update(nodes)
        for rel in sorted(folders, key=lambda item: (item.count("/"), item)):
            parent = _enclosing(rel, folders, nodes) or self.graph.root_of(self)
            folder = nodes[rel]
            for imported in _imported_folders(imports[rel], held, rel):
                self.graph.link("dependsOn", folder, imported, "relationship")
            self.graph.link("owns", parent, folder)
            if folders[rel].type == "Package":
                self.graph.link("belongsTo", folder, parent, "relationship")

    def _class(self, relative: str, folder: Node, cls) -> None:
        """Add the class, its properties, and its operations; each is the object the parser built."""
        cls.load_source_facts()
        node = self.graph.add(self, cls, f"clean_engineering:OoadClass:{relative}:{cls.name}", relative, cls.line, cls.end_line)
        node.set_fact("folder", folder.node_id)
        self.graph.link("owns", folder, node)
        self.graph.link("belongsTo", node, folder, "relationship")
        for prop in _properties_of(cls):
            self._property(relative, node, prop)
        for operation in cls.operations:
            if not operation.is_property:
                self._operation(relative, node, operation)

    def _property(self, relative: str, cls: Node, prop) -> None:
        """A field the class declares, or a getter, which is a property read through an operation."""
        prop_id = f"clean_engineering:Property:{relative}:{prop.name}:{cls.name}"
        line = prop.line or 1
        if prop.type == "Property":
            node = self.graph.add(self, prop, prop_id, relative, line, line)
            hint = prop.type_hint or ""
        else:
            node = self.graph.add_named(self, "Property", prop_id, prop.name, Source(relative, line, line, str(self._source_root)))
            hint = prop.name[:1].upper() + prop.name[1:]
            for fact in _GETTER_MEASURES:
                node.set_fact(fact, getattr(prop, fact, None))
        # A property found only by a getter has no parsed object to name its class, so the node does.
        node.set_fact("owner", cls.name)
        self.graph.link("properties", cls, node, "grouped")
        if not _names_class(hint, self._class_names):
            return
        self.graph.link("relative", cls, node)
        for other in self._class_names:
            other_node = self._class_named(other) if other != cls.name and other in hint else None
            if other_node is not None:
                self.graph.link("hasType", node, other_node, "relationship")
                self.graph.link("dependsOn", cls, other_node, "relationship")

    def _operation(self, relative: str, cls: Node, operation) -> None:
        start, end = operation.source_lines
        operation.load_span_facts()
        node = self.graph.add(self, operation, f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}", relative, start, end)
        node.set_fact("parameters", [[p.name, (p.type_hint or "").strip()] for p in operation.parameters])
        self.graph.link("owns", cls, node)
        for parameter in operation.parameters:
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            self.graph.link("hasParameter", node, self.graph.add(self, parameter, param_id, relative, start, start), "relationship")
        returned = operation.return_type or ""
        if _names_class(returned, self._class_names):
            for other in self._class_names:
                other_node = self._class_named(other) if other in returned else None
                if other_node is not None:
                    self.graph.link("returns", node, other_node, "relationship")

    def _class_named(self, name: str) -> Node | None:
        return next((node for node in self.graph.nodes_of(self, "OoadClass") if node.name == name), None)

    ## the model documents

    def _read_model_documents(self) -> None:
        """The Clean Engineering model documents for the folders in scope, ``{folder}/.context/*-model.md``. The
        practice's root holds every member they describe, by ``Class.member``, so a realization can follow an
        interaction into a class the load left out without a second copy of the class among the code's nodes."""
        described: dict = {}
        for file in self._model_files():
            relative = file.relative_to(self._source_root).as_posix()
            self.graph.report_progress(f"clean_engineering · model · {relative}")
            described.update(self.model_in("markdown", file.read_text(encoding="utf-8")).described_members(relative))
        if described:
            # A refresh reads only some model documents, so the members the others describe stay.
            root = self.graph.root_of(self)
            root.set_fact("model_members", {**(root.get_fact("model_members") or {}), **described})

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


def _merge_fact(node: Node, key: str, values: list) -> None:
    """Add values to a list fact the node keeps: on its parsed object's own field, or among the facts a node read back
    from a saved graph keeps."""
    kept = node.get_fact(key) or []
    merged = sorted(set(kept) | set(values))
    if key in getattr(node, "graph_facts", ()):
        setattr(node, key, merged)
    else:
        node.set_fact(key, merged)


def _code_folders(root: Path, scope: list[Path] | None = None) -> dict:
    """A module owns a module card (``.context/module-context.md``). Any other folder with source is a package. Each is
    the folder's Module, made once with its folder, which holds its card. With a scope, only those folders are read."""
    if scope is not None:
        found = {folder.relative_to(root).as_posix(): _folder_module(folder, os.listdir(folder)) for folder in scope}
        return {rel: module for rel, module in found.items() if module is not None}
    folders: dict = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not skips_folder(name)]
        folder = Path(dirpath)
        rel = folder.relative_to(root)
        module = _folder_module(folder, filenames) if rel != Path(".") else None
        if module is not None:
            folders[rel.as_posix()] = module
    return folders


def _folder_module(folder: Path, filenames: list[str]):
    """The folder's Module, typed ``Module`` when it holds a module card and ``Package`` when it holds only source; none
    for a folder with neither."""
    from cdd_guidance.practices.clean_engineering.model.base_class_model import Module

    has_code = any(Path(name).suffix.lower() in CODE_SUFFIXES for name in filenames)
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


def _properties_of(cls) -> list:
    """The class's properties: the fields its parser read, then its getters, each once, in line order. A static field
    belongs to the class, not to its instances, and a name starting with `_` is private."""
    found = []
    seen = set()
    for prop in cls.properties:
        if str(prop.name).startswith("_") or prop.name in seen or prop.is_static:
            continue
        seen.add(prop.name)
        found.append(prop)
    for operation in cls.operations:
        if not operation.is_property or operation.name in seen or str(operation.name).startswith("_"):
            continue
        seen.add(operation.name)
        found.append(operation)
    return sorted(found, key=lambda member: (member.line or 1, member.name))


def _names_class(hint: str, class_names: set[str]) -> bool:
    """A hint names a class when that class is a whole type, not a prefix of a longer name."""
    if not hint or "[" in hint:
        return False
    return any(re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", hint) for name in class_names)
