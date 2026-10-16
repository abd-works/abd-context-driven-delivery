"""Load a working copy into the explorer graph from the practice models.

Each practice loads through its root model when it has one. A pattern overlay
has no root model: each schema type loads through the model it extends.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.graph import EdgeType, Graph
from harness.graph.rules import attach_rules
from harness.graph.schema_catalog import SchemaType, overlay_schema, path_matches, practice_schema

_GETTER = re.compile(r"\bget\s+(\w+)\s*\(")
_FOREIGN = re.compile(r"//\s*foreign\s+(\w+)")
_CLASS_NAMES = re.compile(r"\bclass\s+(\w+)")
_FIELD_INIT = re.compile(
    r"^\s*(?:(?:public|private|protected|readonly|declare|override)\s+)*(\w+)\s*:\s*([^=;\n]+?)(?:\s*=\s*[^;\n]*)?\s*;",
    re.M,
)
_STATIC_LINE = re.compile(r"^\s*(?:(?:public|private|protected|readonly|declare|override)\s+)*static\b")
_HEADING = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)
_CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py"}
_SKIP_DIRS = {".codeql", ".git", ".context", "node_modules", "__pycache__", ".sessions"}


def fill_working_copy(graph: Graph) -> None:
    source = graph._folder
    if source is None:
        return
    clean = graph.practice("clean_engineering") if "clean_engineering" in graph.practices else None
    classes = _record_clean(clean, source) if clean is not None else []
    if "ddd" in graph.practices:
        _record_ddd(graph.practice("ddd"), source, classes)
    if "stories" in graph.practices:
        _record_stories(graph.practice("stories"), source)
    _publish_unmodeled(graph)
    _load_overlay(graph, source)
    for practice in graph.practices.values():
        practice.root_node.populate()
    from harness.graph.schema_edges import sync_schema_edges

    sync_schema_edges(graph)
    for practice in graph.practices.values():
        practice.rebuild_tree()
        attach_rules(practice)
        practice.loaded = ["nodes", "edges", "rules"]


_MODELED = {"clean_engineering", "ddd", "stories"}


def _publish_unmodeled(graph: Graph) -> None:
    """A practice with no root model still offers every type its schema names."""
    for name in graph.practices:
        if name in _MODELED:
            continue
        _publish(graph, practice_schema(name, []))


def _record_clean(practice, root: Path) -> list[dict]:
    from practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel

    roles = _code_folders(root)
    parsed: list[dict] = []
    nodes = []
    edges = []
    root_id = practice.root_node.node_id
    class_names = _class_names(root)
    ids = {rel: f"clean_engineering:{kind}:{rel}" for rel, kind in roles.items()}
    for rel in sorted(roles, key=lambda item: (item.count("/"), item)):
        kind = roles[rel]
        parent = _enclosing_id(rel, roles, ids, root_id)
        nodes.append([ids[rel], Path(rel).name, kind, "clean_engineering", rel, 1, 1])
        edges.append([parent, ids[rel], "owns", 2, "direct"])
        if kind == "Package":
            edges.append([ids[rel], parent, "belongsTo", 5, "relationship"])
    src = root / "src"
    if src.is_dir():
        for file in sorted(src.rglob("*")):
            if file.suffix.lower() not in {".ts", ".tsx"} or not file.is_file() or _ignored(file.relative_to(root)):
                continue
            text = file.read_text(encoding="utf-8")
            relative = file.relative_to(root).as_posix()
            owner = _nearest(str(Path(relative).parent).replace("\\", "/"), roles)
            owner_id = ids.get(owner, root_id)
            model = TypeScriptCleanEngineeringModel.parse(text)
            for module in model.modules:
                for cls in module.classes:
                    parsed.append(_class_fact(practice, text, relative, owner_id, cls, class_names, nodes, edges))
    practice.apply_nodes(nodes)
    practice.apply_edges(edges)
    practice.loaded = ["nodes", "edges", "rules"]
    return parsed


def _code_folders(root: Path) -> dict[str, str]:
    """A module owns `.context/module-context.md`. Any other folder with source is a package."""
    roles: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in _SKIP_DIRS and not name.startswith(".")]
        folder = Path(dirpath)
        rel = folder.relative_to(root)
        if rel == Path("."):
            continue
        key = rel.as_posix()
        if (folder / ".context" / "module-context.md").is_file():
            roles[key] = "Module"
        elif any(Path(name).suffix.lower() in _CODE_SUFFIXES for name in filenames):
            roles[key] = "Package"
    return roles


def _ignored(rel: Path) -> bool:
    return any(part in _SKIP_DIRS or part.startswith(".") for part in rel.parts)


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


def _enclosing_id(path: str, roles: dict[str, str], ids: dict[str, str], root_id: str) -> str:
    parent = str(Path(path).parent).replace("\\", "/")
    owner = _nearest(parent, roles) if parent != "." else ""
    return ids[owner] if owner else root_id


def _bounded_contexts(root: Path) -> list[tuple[str, str, str]]:
    """Each folder that contains `.context/bounded-context.md` is a bounded context."""
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in _SKIP_DIRS and not name.startswith(".")]
        marker = Path(dirpath) / ".context" / "bounded-context.md"
        if not marker.is_file():
            continue
        folder = Path(dirpath)
        rel = "." if folder == root else folder.relative_to(root).as_posix()
        text = marker.read_text(encoding="utf-8")
        heading = _HEADING.search(text)
        name = heading.group(1).strip() if heading else folder.name
        found.append((rel, name, marker.relative_to(root).as_posix()))
    return sorted(found)


def _context_for(folder: str, contexts: list[str]) -> str:
    best = ""
    for candidate in contexts:
        if candidate == "." or folder == candidate or folder.startswith(candidate + "/"):
            if candidate == "." or len(candidate) > len(best):
                best = candidate
    return best


def _class_fact(practice, text: str, relative: str, module_id: str, cls, class_names: set[str], nodes: list, edges: list) -> dict:
    class_id = f"clean_engineering:OoadClass:{relative}:{cls.name}"
    start, end = _class_extent(text, cls.name, getattr(cls, "line", None) or 1)
    nodes.append([class_id, cls.name, "OoadClass", "clean_engineering", relative, start, end])
    edges.append([module_id, class_id, "owns", 2, "direct"])
    edges.append([class_id, module_id, "belongsTo", 5, "relationship"])
    properties = _properties_of(cls, text)
    for prop in properties:
        prop_id = f"clean_engineering:Property:{relative}:{prop['name']}:{cls.name}"
        nodes.append([prop_id, prop["name"], "Property", "clean_engineering", relative, prop["line"], prop["line"]])
        edges.append([class_id, prop_id, "properties", 3, "grouped"])
        if _names_class(prop["hint"], class_names):
            edges.append([class_id, prop_id, "relative", 1, "direct"])
            for other in class_names:
                if other != cls.name and other in prop["hint"]:
                    other_id = _class_id_named(nodes, other)
                    if other_id:
                        edges.append([prop_id, other_id, "hasType", 7, "relationship"])
                        edges.append([class_id, other_id, "dependsOn", 13, "relationship"])
    for operation in cls.operations:
        if operation.name in {"constructor", "get", "set"} or getattr(operation, "is_property", False):
            continue
        if str(operation.name).startswith("_"):
            continue
        from practices.clean_engineering.model.operation import operation_source_span

        span = _method_span(text, operation.name, getattr(operation, "line", None) or 1)
        model_span = operation_source_span(operation)
        if model_span is not None:
            start, end = model_span
        else:
            start = getattr(operation, "line", None) or span[0]
            line_count = getattr(operation, "line_count", None)
            end = start + line_count - 1 if line_count and line_count > 0 else span[1]
        op_id = f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}"
        nodes.append([op_id, operation.name, "Operation", "clean_engineering", relative, start, end])
        edges.append([class_id, op_id, "owns", 2, "direct"])
        for parameter in operation.parameters:
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            nodes.append([param_id, parameter.name, "Parameter", "clean_engineering", relative, span[0], span[0]])
            edges.append([op_id, param_id, "hasParameter", 6, "relationship"])
        if _names_class(getattr(operation, "return_type", "") or "", class_names):
            for other in class_names:
                if other in (operation.return_type or ""):
                    other_id = _class_id_named(nodes, other)
                    if other_id:
                        edges.append([op_id, other_id, "returns", 10, "relationship"])
    return {"name": cls.name, "id": class_id, "file": relative, "operations": list(cls.operations), "text": text}


def _properties_of(cls, text: str) -> list[dict]:
    body, body_line = _class_span(text, cls.name)
    found = []
    seen = set()
    for prop in cls.properties:
        if str(prop.name).startswith("_") or prop.name in seen:
            continue
        seen.add(prop.name)
        found.append({"name": prop.name, "hint": getattr(prop, "type_hint", "") or "", "line": getattr(prop, "line", None) or 1})
    for operation in cls.operations:
        if not getattr(operation, "is_property", False) or operation.name in seen or str(operation.name).startswith("_"):
            continue
        seen.add(operation.name)
        found.append({
            "name": operation.name,
            "hint": operation.name[:1].upper() + operation.name[1:],
            "line": getattr(operation, "line", None) or 1,
        })
    for match in _GETTER.finditer(body):
        name = match.group(1)
        if name in seen or name.startswith("_"):
            continue
        seen.add(name)
        line = body_line + body[: match.start()].count("\n")
        found.append({"name": name, "hint": name[:1].upper() + name[1:], "line": line})
    for match in _FIELD_INIT.finditer(body):
        name = match.group(1)
        line_start = body.rfind("\n", 0, match.start()) + 1
        if name in seen or name.startswith("_") or _STATIC_LINE.match(body[line_start:]):
            continue
        seen.add(name)
        line = body_line + body[: match.start()].count("\n")
        found.append({"name": name, "hint": match.group(2).strip(), "line": line})
    found.sort(key=lambda prop: (prop["line"], prop["name"]))
    return found


def _class_extent(text: str, name: str, fallback: int) -> tuple[int, int]:
    """Declaration line through the class's closing brace."""
    match = re.search(rf"\bclass\s+{re.escape(name)}\b[^{{]*\{{", text)
    if match is None:
        return fallback, fallback
    start = text[: match.start()].count("\n") + 1
    body, _body_line = _class_span(text, name)
    end = start + body.count("\n")
    return start, max(start, end)


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


def _stereotyped_name(text: str, name: str) -> str:
    from practices.ddd.model.stereotypes import class_declaration_decorated_name

    return class_declaration_decorated_name(text, name)


def _class_names(root: Path) -> set[str]:
    names = set()
    src = root / "src"
    if not src.is_dir():
        return names
    for file in src.rglob("*"):
        if file.suffix.lower() in {".ts", ".tsx"} and file.is_file():
            names.update(_CLASS_NAMES.findall(file.read_text(encoding="utf-8")))
    return names


def _names_class(hint: str, class_names: set[str]) -> bool:
    """A hint names a class when that class is a whole type, not a prefix of a longer name."""
    if not hint or "[" in hint:
        return False
    return any(re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])", hint) for name in class_names)


def _class_id_named(nodes: list, name: str) -> str:
    for row in nodes:
        if row[2] == "OoadClass" and row[1] == name:
            return row[0]
    return ""


def _method_span(text: str, name: str, fallback: int) -> tuple[int, int]:
    from practices.clean_engineering.model.c_family_parse import CFamilyParse

    return CFamilyParse.method_span_in_text(text, name, fallback)


def _record_ddd(practice, root: Path, classes: list[dict]) -> None:
    from practices.ddd.model.stereotypes import inferred_tactical_kind

    names = {cls["name"] for cls in classes}
    members: dict[str, list[dict]] = {}
    for cls in classes:
        folder = str(Path(cls["file"]).parent).replace("\\", "/")
        kind = inferred_tactical_kind(_stereotyped_name(cls["text"], cls["name"]), names)
        if kind is None:
            continue
        members.setdefault(folder, []).append({**cls, "kind": kind})
    nodes = []
    edges = []
    contexts = _bounded_contexts(root) or [(".", "bounded context", ".")]
    context_ids = {}
    for rel, name, markdown in contexts:
        context_id = f"ddd:BoundedContext:{rel}:{name}"
        context_ids[rel] = context_id
        end = 1
        if markdown != ".":
            text = (root / markdown).read_text(encoding="utf-8")
            end = max(1, text.count("\n") if text.endswith("\n") else text.count("\n") + 1)
        nodes.append([context_id, name, "BoundedContext", "ddd", markdown, 1, end])
        parent_rel = _context_for(str(Path(rel).parent).replace("\\", "/"), [item[0] for item in contexts]) if rel != "." else ""
        if rel != "." and parent_rel == rel:
            parent_rel = ""
        parent_id = context_ids.get(parent_rel) or practice.root_node.node_id
        edges.append([parent_id, context_id, "owns", 2, "direct"])
        if parent_rel:
            edges.append([context_id, parent_id, "belongsTo", 3, "relationship"])
    by_id = {}
    for folder in sorted(members):
        context_id = context_ids[_context_for(folder, list(context_ids))]
        aggregate_id = f"ddd:Aggregate:{folder}"
        nodes.append([aggregate_id, Path(folder).name, "Aggregate", "ddd", folder, 1, 1])
        edges.append([context_id, aggregate_id, "owns", 2, "direct"])
        edges.append([aggregate_id, context_id, "belongsTo", 3, "relationship"])
        for member in members[folder]:
            member_id = f"ddd:{member['kind']}:{member['file']}:{member['name']}"
            nodes.append([member_id, member["name"], member["kind"], "ddd", member["file"], 1, 1])
            by_id[member["name"]] = member_id
            if member["kind"] == "EntityRoot":
                edges.append([aggregate_id, member_id, "root", 1, "direct"])
            else:
                edges.append([aggregate_id, member_id, "owns", 2, "direct"])
            edges.append([member_id, aggregate_id, "belongsTo", 3, "relationship"])
            if member["kind"] == "Repository" and member["name"].endswith("Repository"):
                root_name = member["name"][: -len("Repository")]
                root_id = by_id.get(root_name)
                if root_id:
                    edges.append([member_id, root_id, "accesses", 4, "relationship"])
        for member in members[folder]:
            if member["kind"] != "EntityRoot":
                continue
            for other in _FOREIGN.findall(member["text"]):
                other_id = by_id.get(other)
                if other_id and other != member["name"]:
                    edges.append([by_id[member["name"]], other_id, "associates", 5, "relationship"])
    practice.apply_nodes(nodes)
    practice.apply_edges(edges)
    practice.loaded = ["nodes", "edges", "rules"]


def _record_stories(practice, source: Path) -> None:
    from practices.stories.model.graph_story_model import GraphStoryModel
    from practices.stories.model.story_model import StoryModel
    from practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

    files: dict[str, str] = {}
    if source.is_dir():
        for path in source.rglob("*"):
            if path.suffix.lower() not in {".ts", ".tsx"} or not path.is_file():
                continue
            files[path.relative_to(source).as_posix()] = path.read_text(encoding="utf-8")
    model = TypeScriptStoryModel("tests").load(files)
    if not model.epics:
        model = StoryModel.load(source)
    GraphStoryModel(model).record(practice)


def _load_overlay(graph: Graph, root: Path) -> None:
    """Overlay types load through the base their schema ``is:`` names."""
    types = overlay_schema(graph.overlays)
    if not types:
        return
    _publish(graph, types)
    for schema_type in types:
        _load_schema_type(graph, root, schema_type, types)
    _link_schema_fields(graph, types)


def _publish(graph: Graph, types: tuple[SchemaType, ...] | list[SchemaType]) -> None:
    for schema_type in types:
        practice = graph.practices.get(schema_type.practice)
        if practice is None:
            continue
        practice.node_types.add(schema_type.semantic)
        for kind, _targets in schema_type.fields:
            if kind not in practice.edge_types:
                practice.edge_types[kind] = EdgeType(kind, 5, "relationship")


def _load_schema_type(graph: Graph, root: Path, schema_type: SchemaType, types: tuple[SchemaType, ...]) -> None:
    practice = graph.practices.get(schema_type.practice)
    if practice is None:
        return
    for file in _schema_files(root, schema_type, types):
        relative = file.relative_to(root).as_posix()
        node_id = f"{schema_type.practice}:{schema_type.semantic}:{relative}"
        if node_id in practice.by_id:
            continue
        text = file.read_text(encoding="utf-8")
        end = max(1, text.count("\n") + (0 if text.endswith("\n") else 1))
        name = _loaded_name(schema_type, file, text)
        practice.apply_nodes([[node_id, name, schema_type.semantic, schema_type.practice, relative, 1, end]])


def _loaded_name(schema_type: SchemaType, file: Path, text: str) -> str:
    """The base model names the node when it can read the file. The schema type stays."""
    if file.suffix.lower() not in {".ts", ".tsx"} or not schema_type.is_ref:
        return file.stem
    from practices.clean_engineering.model.typescript.typescript_class_model import TypeScriptCleanEngineeringModel

    model = TypeScriptCleanEngineeringModel.parse(text)
    for module in model.modules:
        for cls in module.classes:
            return cls.name
    return file.stem


def _schema_files(root: Path, schema_type: SchemaType, types: tuple[SchemaType, ...]) -> list[Path]:
    found = []
    for file in sorted(root.rglob("*")):
        if not file.is_file() or _ignored(file.relative_to(root)):
            continue
        if not path_matches(schema_type.path, file.relative_to(root)):
            continue
        if _best_schema_type(file.relative_to(root), types) is not schema_type:
            continue
        found.append(file)
    return found


def _best_schema_type(relative: Path, types: tuple[SchemaType, ...]) -> SchemaType | None:
    matches = [item for item in types if path_matches(item.path, relative)]
    if not matches:
        return None
    return max(matches, key=lambda item: _path_rank(item, relative.stem))


def _path_rank(schema_type: SchemaType, stem: str) -> tuple[bool, int]:
    folded = stem.lower().replace("-", "")
    token = schema_type.key[:1].lower() + schema_type.key[1:]
    short = token.removesuffix("Root") if token.endswith("Root") else token
    named = short.lower() in folded
    literal = len(re.sub(r"\{[^}]+\}", "", schema_type.path))
    return (named, literal)


def _link_schema_fields(graph: Graph, types: tuple[SchemaType, ...]) -> None:
    nodes = _nodes_by_semantic(graph)
    for schema_type in types:
        practice = graph.practices.get(schema_type.practice)
        if practice is None:
            continue
        for kind, targets in schema_type.fields:
            _link_kind(practice, nodes, schema_type.semantic, kind, targets)


def _nodes_by_semantic(graph: Graph) -> dict[str, list]:
    found: dict[str, list] = {}
    for practice in graph.practices.values():
        for node in practice.by_id.values():
            found.setdefault(node.type, []).append(node)
    return found


def _link_kind(practice, nodes: dict[str, list], owner_type: str, kind: str, targets: tuple[str, ...]) -> None:
    from harness.graph.schema_rules import semantic_type

    owners = nodes.get(owner_type, [])
    targets_nodes = []
    for target in targets:
        targets_nodes.extend(nodes.get(semantic_type(target), []))
    for owner in owners:
        for target in targets_nodes:
            if owner is target or not _same_folder(owner, target):
                continue
            practice.record({"kind": kind, "order": 5, "display": "relationship"}, owner, target)


def _same_folder(left, right) -> bool:
    first = _folder(left)
    second = _folder(right)
    if not first or first == "." or not second or second == ".":
        return False
    return first == second or first.startswith(second + "/") or second.startswith(first + "/")


def _folder(node) -> str:
    path = Path(node.source.file)
    if path.suffix:
        return path.parent.as_posix()
    return path.as_posix().strip("/")
