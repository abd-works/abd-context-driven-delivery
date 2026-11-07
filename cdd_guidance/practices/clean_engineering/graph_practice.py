"""How Clean Engineering takes part in the graph: it reads each source file with its language's class model and adds
the folders, classes, properties, operations, and parameters it parsed to its practice graph as nodes, and keeps the
members its model documents describe on the practice's root."""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.bound_node import schema_sync_paused
from harness.graph.graph import Graph, Node, PracticeGraph, Source
from harness.graph.graph_practice import GraphPractice, GraphPractices, rules_in
from harness.graph.skipped_folders import scanned_files, skips_folder

_PACKAGE = "cdd_guidance.practices.clean_engineering"
CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py"}
_GETTER = re.compile(r"\bget\s+(\w+)\s*\(")
_CLASS_NAMES = re.compile(r"\bclass\s+(\w+)")
_FIELD_INIT = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|declare|override)\s+)*(\w+)\s*:\s*([^=;\n]+?)(?:\s*=\s*[^;\n]*)?\s*;",
    re.M,
)
_STATIC_LINE = re.compile(r"^\s*(?:(?:public|private|protected|readonly|declare|override)\s+)*static\b")
# Construction and accessor heads are how a class is built or read, not operations a rule measures.
_NOT_OPERATIONS = frozenset({"constructor", "get", "set"})


class CleanEngineeringGraph(GraphPractice):
    """Clean Engineering's nodes, its rules, and the draw.io rules it checks on a diagram's nodes."""

    def own_rules(self) -> dict:
        return {**rules_in(f"{self.package}.rules"), **self.language_rules("drawio")}

    def language_rules(self, language: str) -> dict:
        return rules_in(f"{self.package}.model.drawio.rules") if language == "drawio" else {}

    def read(self, practice: PracticeGraph) -> None:
        with schema_sync_paused():
            _CodeReading(practice).read()
            _ModelReading(practice).read()


class _CodeReading:
    """One read of a working copy's code into the Clean Engineering practice graph."""

    def __init__(self, practice: PracticeGraph) -> None:
        self.practice = practice
        self.graph: Graph = practice.graph
        self.root = Path(practice.source_root)
        self.class_names: set[str] = set()

    def read(self) -> None:
        self.graph.report_progress("clean_engineering · folders")
        roles = _code_folders(self.root, self.graph.scope_folders())
        files = self.graph.source_files(self.root, CODE_SUFFIXES)
        modules = self._parsed_modules(files)
        self.class_names = {cls.name for module, _text in modules.values() for cls in module.classes}
        self.class_names |= self._class_names(self._unparsed_declaring_files(files))
        folders = {rel: self._folder_node(rel, kind) for rel, kind in roles.items()}
        for file, (module, text) in modules.items():
            relative = file.relative_to(self.root).as_posix()
            owner = _nearest(str(Path(relative).parent).replace("\\", "/"), roles)
            if owner:
                folders[owner].dependencies.extend(module.dependencies)
            for cls in module.classes:
                self._class(text, relative, folders.get(owner) or self.practice.root_node, cls)
        self._link_folders(roles, folders)

    def _folder_node(self, rel: str, kind: str):
        from cdd_guidance.practices.clean_engineering.model.base_class_model import Module

        module = Module(name=Path(rel).name, sequential_order=1)
        module.load_folder_facts(self.root / rel)
        module.type = kind
        return self.practice.add(module, f"clean_engineering:{kind}:{rel}", rel, 1, 1)

    def _link_folders(self, roles: dict[str, str], folders: dict) -> None:
        ids = {rel: folder.node_id for rel, folder in folders.items()}
        for rel in sorted(roles, key=lambda item: (item.count("/"), item)):
            parent = _enclosing(rel, roles, folders) or self.practice.root_node
            folder = folders[rel]
            folder.dependencies = sorted(_imported_folders(folder.dependencies, ids, rel))
            self.practice.link("owns", parent, folder)
            if roles[rel] == "Package":
                self.practice.link("belongsTo", folder, parent, "relationship")

    def _parsed_modules(self, files: list[Path]) -> dict[Path, tuple]:
        """Each source file's parsed module and text, for the files that parse."""
        modules: dict[Path, tuple] = {}
        for index, file in enumerate(files, start=1):
            self.graph.report_progress(f"clean_engineering · classes · {index}/{len(files)} · {file.relative_to(self.root).as_posix()}")
            module, text = _parsed_module(file, self.root)
            if module is not None:
                modules[file] = (module, text)
        return modules

    def _unparsed_declaring_files(self, files: list[Path]) -> list[Path]:
        """The source files outside an edited-file scope, whose class names a type hint may still name.

        The scope's own files are parsed and their classes named by the parse. Names in the other files come from a
        text match, so reading the files the scope leaves out stays cheap.
        """
        if self.graph.edited_files() is None:
            return []
        parsed = set(files)
        return [path for path in scanned_files(self.root, CODE_SUFFIXES) if path not in parsed]

    def _class_names(self, files: list[Path]) -> set[str]:
        names = set()
        for index, file in enumerate(files, start=1):
            self.graph.report_progress(f"clean_engineering · class names · {index}/{len(files)} · {file.name}")
            try:
                names.update(_CLASS_NAMES.findall(file.read_text(encoding="utf-8")))
            except (OSError, UnicodeDecodeError):
                continue
        return names

    def _class(self, text: str, relative: str, folder: Node, cls) -> None:
        """Add the class, its properties, and its operations; each is the object the parser built."""
        if cls.line and cls.end_line:
            start, end = cls.line, cls.end_line
        else:
            start, end = _class_extent(text, cls.name, getattr(cls, "line", None) or 1)
        lines = text.splitlines()
        cls.load_source_facts("\n".join(lines[start - 1 : end]))
        node = self.practice.add(cls, f"clean_engineering:OoadClass:{relative}:{cls.name}", relative, start, end)
        node.set_fact("folder", folder.node_id)
        self.practice.link("owns", folder, node)
        self.practice.link("belongsTo", node, folder, "relationship")
        for prop in _properties_of(cls, text):
            self._property(relative, node, prop)
        for operation in cls.own_operations():
            if operation.name not in _NOT_OPERATIONS and not getattr(operation, "is_property", False):
                self._operation(lines, relative, node, operation)

    def _property(self, relative: str, cls: Node, prop: dict) -> None:
        prop_id = f"clean_engineering:Property:{relative}:{prop['name']}:{cls.name}"
        parsed = prop["parsed"]
        node = (
            self.practice.add(parsed, prop_id, relative, prop["line"], prop["line"])
            if parsed is not None
            else self.practice.add_named("Property", prop_id, prop["name"], Source(relative, prop["line"], prop["line"], self.practice.source_root))
        )
        # A property found only by a getter or field has no parsed object to name its class, so the node does.
        node.set_fact("owner", cls.name)
        self.practice.link("properties", cls, node, "grouped")
        if not _names_class(prop["hint"], self.class_names):
            return
        self.practice.link("relative", cls, node)
        for other in self.class_names:
            other_node = self._class_named(other) if other != cls.name and other in prop["hint"] else None
            if other_node is not None:
                self.practice.link("hasType", node, other_node, "relationship")
                self.practice.link("dependsOn", cls, other_node, "relationship")

    def _operation(self, lines: list[str], relative: str, cls: Node, operation) -> None:
        from cdd_guidance.practices.clean_engineering.model.operation import operation_source_span

        start, end = operation_source_span(operation) or _scanned_span("\n".join(lines), operation)
        operation.load_span_facts("\n".join(lines[start - 1 : end]))
        node = self.practice.add(operation, f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}", relative, start, end)
        node.set_fact("parameters", [[p.name, (p.type_hint or "").strip()] for p in operation.parameters])
        self.practice.link("owns", cls, node)
        for parameter in operation.parameters:
            parameter.load_operation_facts(operation)
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            self.practice.link("hasParameter", node, self.practice.add(parameter, param_id, relative, start, start), "relationship")
        returned = getattr(operation, "return_type", "") or ""
        if _names_class(returned, self.class_names):
            for other in self.class_names:
                other_node = self._class_named(other) if other in returned else None
                if other_node is not None:
                    self.practice.link("returns", node, other_node, "relationship")

    def _class_named(self, name: str) -> Node | None:
        return next((node for node in self.practice.nodes.get("OoadClass", []) if node.name == name), None)


class _ModelReading:
    """The Clean Engineering model documents for the folders in scope, ``{folder}/.context/*-model.md``. The practice's
    root holds every member they describe, by ``Class.member``, so a realization can follow an interaction into a class
    the load left out without a second copy of the class among the code's nodes."""

    def __init__(self, practice: PracticeGraph) -> None:
        self.practice = practice
        self.graph: Graph = practice.graph
        self.root = Path(practice.source_root)

    def read(self) -> None:
        from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
        from cdd_guidance.practices.clean_engineering.model.model_descriptions import ModelDescriptions

        descriptions = ModelDescriptions()
        for file in self._model_files():
            relative = file.relative_to(self.root).as_posix()
            self.graph.report_progress(f"clean_engineering · model · {relative}")
            descriptions.read(MarkdownCleanEngineeringModel(name="", sequential_order=1).parse(file.read_text(encoding="utf-8")), relative)
        if not descriptions.is_empty:
            self.practice.root_node.set_fact("model_members", descriptions.model_members)

    def _model_files(self) -> list[Path]:
        """Each scoped folder's and each of its parents' ``.context/*-model.md``, up to the root. ``.context`` is a
        skipped folder, so the code scan never reaches them."""
        edited = self.graph.edited_files()
        folders = self._every_folder() if edited is None else self._folders_holding(edited)
        named = {path for path in (edited or []) if path.name.endswith("-model.md")}
        return sorted({model for folder in folders for model in (folder / ".context").glob("*-model.md")} | named)

    def _every_folder(self) -> set[Path]:
        folders = set()
        for dirpath, dirnames, _files in os.walk(self.root):
            dirnames[:] = [name for name in dirnames if not skips_folder(name)]
            folders.add(Path(dirpath))
        return folders

    def _folders_holding(self, edited: list[Path]) -> set[Path]:
        folders = set()
        for path in edited:
            folder = path if path.is_dir() else path.parent
            while folder == self.root or self.root in folder.parents:
                folders.add(folder)
                if folder == self.root:
                    break
                folder = folder.parent
        return folders


def _parsed_module(file: Path, root: Path):
    """The language model's module for one source file, with its source facts loaded, and the file text. A file
    without classes still gets its language's module so its imports are recorded."""
    from cdd_guidance.practices.clean_engineering.model.base_class_model import Module

    try:
        text = file.read_text(encoding="utf-8")
        model = _language_model(file).parse(text)
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
        return None, ""
    module = model.modules[0] if model.modules else model.load_module(Module(name="", sequential_order=1))
    module.load_source_facts(text, file, root)
    return module, text


def _language_model(file: Path):
    from cdd_guidance.practices.clean_engineering.model.javascript.javascript_class_model import JavaScriptCleanEngineeringModel
    from cdd_guidance.practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
    from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel

    suffix = file.suffix.lower()
    if suffix == ".py":
        return PythonCleanEngineeringModel()
    if suffix in {".js", ".jsx"}:
        return JavaScriptCleanEngineeringModel()
    return TypeScriptCleanEngineeringModel


def _code_folders(root: Path, scope: list[Path] | None = None) -> dict[str, str]:
    """A module owns a module card (``.context/module-context.md``). Any other folder with source is a package. With a
    scope, only those folders are read, not the whole tree."""
    if scope is not None:
        roles = {folder.relative_to(root).as_posix(): _folder_role(folder, os.listdir(folder)) for folder in scope}
        return {key: role for key, role in roles.items() if role}
    roles: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if not skips_folder(name)]
        folder = Path(dirpath)
        rel = folder.relative_to(root)
        role = _folder_role(folder, filenames) if rel != Path(".") else ""
        if role:
            roles[rel.as_posix()] = role
    return roles


def _folder_role(folder: Path, filenames: list[str]) -> str:
    from cdd_guidance.practices.clean_engineering.model.module_context_files import module_card

    if module_card(folder).is_file():
        return "Module"
    if any(Path(name).suffix.lower() in CODE_SUFFIXES for name in filenames):
        return "Package"
    return ""


def _nearest(path: str, roles: dict[str, str]) -> str:
    current = path
    while current and current != ".":
        if current in roles:
            return current
        parent = str(Path(current).parent).replace("\\", "/")
        if parent == current:
            break
        current = "" if parent == "." else parent
    return ""


def _enclosing(path: str, roles: dict[str, str], folders: dict):
    parent = str(Path(path).parent).replace("\\", "/")
    owner = _nearest(parent, roles) if parent != "." else ""
    return folders[owner] if owner else None


def _imported_folders(targets: list[str], ids: dict[str, str], own: str) -> set[str]:
    """The graph folder each import lands in (longest match); imports of the folder itself drop out."""
    found: set[str] = set()
    for target in targets:
        parts = target.split("/")
        while parts and "/".join(parts) not in ids:
            parts.pop()
        folder = "/".join(parts)
        if folder and folder != own:
            found.add(ids[folder])
    return found


def _properties_of(cls, text: str) -> list[dict]:
    """The class's properties: the parsed ones, its getters, and the fields its body declares, each once, in line order."""
    body, body_line = _class_span(text, cls.name)
    found = []
    seen = set()
    for prop in cls.properties:
        if str(prop.name).startswith("_") or prop.name in seen:
            continue
        seen.add(prop.name)
        found.append({"name": prop.name, "hint": getattr(prop, "type_hint", "") or "", "line": getattr(prop, "line", None) or 1, "parsed": prop})
    for operation in cls.operations:
        if not getattr(operation, "is_property", False) or operation.name in seen or str(operation.name).startswith("_"):
            continue
        seen.add(operation.name)
        found.append({"name": operation.name, "hint": operation.name[:1].upper() + operation.name[1:], "line": getattr(operation, "line", None) or 1, "parsed": None})
    for match in _GETTER.finditer(body):
        name = match.group(1)
        if name in seen or name.startswith("_"):
            continue
        seen.add(name)
        found.append({"name": name, "hint": name[:1].upper() + name[1:], "line": body_line + body[: match.start()].count("\n"), "parsed": None})
    for match in _FIELD_INIT.finditer(body):
        name = match.group(1)
        line_start = body.rfind("\n", 0, match.start()) + 1
        if name in seen or name.startswith("_") or _STATIC_LINE.match(body[line_start:]):
            continue
        seen.add(name)
        found.append({"name": name, "hint": match.group(2).strip(), "line": body_line + body[: match.start()].count("\n"), "parsed": None})
    found.sort(key=lambda prop: (prop["line"], prop["name"]))
    return found


def _class_extent(text: str, name: str, fallback: int) -> tuple[int, int]:
    """Declaration line through the class's closing brace."""
    match = re.search(rf"\bclass\s+{re.escape(name)}\b[^{{]*\{{", text)
    if match is None:
        return fallback, fallback
    start = text[: match.start()].count("\n") + 1
    body, _body_line = _class_span(text, name)
    return start, max(start, start + body.count("\n"))


def _class_span(text: str, name: str) -> tuple[str, int]:
    match = re.search(rf"\bclass\s+{re.escape(name)}\b[^{{]*\{{", text)
    if match is None:
        return text, 1
    start = match.end() - 1
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index], text[:start].count("\n") + 1
    return text[start:], text[:start].count("\n") + 1


def _names_class(hint: str, class_names: set[str]) -> bool:
    """A hint names a class when that class is a whole type, not a prefix of a longer name."""
    if not hint or "[" in hint:
        return False
    return any(re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", hint) for name in class_names)


def _scanned_span(text: str, operation) -> tuple[int, int]:
    """An operation's lines when its parser gave no span: from its line, or the text's method head, through its close."""
    from cdd_guidance.practices.clean_engineering.model.c_family_parse import CFamilyParse

    span = CFamilyParse.method_span_in_text(text, operation.name, getattr(operation, "line", None) or 1)
    start = getattr(operation, "line", None) or span[0]
    line_count = getattr(operation, "line_count", None)
    return start, start + line_count - 1 if line_count and line_count > 0 else span[1]


GraphPractices.register(CleanEngineeringGraph("clean_engineering", _PACKAGE))
