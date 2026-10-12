"""Load a working copy into the explorer graph from the practice models.

Clean engineering and DDD come from the TypeScript class parser. Stories come
from the story model. A selected pattern overlay adds the nodes that overlay names.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.graph import Graph
from harness.graph.rules import attach_rules

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
        if clean is not None:
            _record_story_edges(graph, classes)
    if "bdd" in graph.practices:
        _offer(graph.practice("bdd"), ["Spec", "Description", "Context", "Observation"])
    if "ux" in graph.practices:
        _offer(graph.practice("ux"), ["UxMap", "Screen"])
    if _overlay_selected(graph, "lern_domain_driven"):
        _record_lern(graph, source, classes)
    for practice in graph.practices.values():
        if practice.loaded != ["nodes", "edges", "rules"]:
            practice.loaded = ["nodes", "edges", "rules"]


def _offer(practice, types: list[str]) -> None:
    for name in types:
        practice.node_types.add(name)
    practice.loaded = ["nodes", "edges", "rules"]


def _overlay_selected(graph: Graph, pattern: str) -> bool:
    return any(pattern in item.replace("\\", "/").split("/") for item in graph.overlays)


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
    attach_rules(practice)
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
        span = _method_span(text, operation.name, getattr(operation, "line", None) or 1)
        op_id = f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}"
        nodes.append([op_id, operation.name, "Operation", "clean_engineering", relative, span[0], span[1]])
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
    """Class name plus the <<stereotype>> tags on the comment above the declaration."""
    match = re.search(rf"(?:export\s+)?(?:abstract\s+)?class\s+{re.escape(name)}\b", text)
    if match is None:
        return name
    prefix = text[max(0, match.start() - 240) : match.start()]
    comment = re.search(r"/\*\*([\s\S]*?)\*/\s*$", prefix)
    if comment is None:
        return name
    tags = re.findall(r"<<[^>]+>>", comment.group(1))
    if not tags:
        return name
    return f"{name} {' '.join(tags)}"


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
    match = re.search(rf"\b{re.escape(name)}\s*\([^)]*\)\s*(?::\s*[^{{]+)?\s*\{{", text)
    if match is None:
        return fallback, fallback
    start = text[: match.start()].count("\n") + 1
    depth = 0
    opened = False
    for index in range(match.end() - 1, len(text)):
        if text[index] == "{":
            depth += 1
            opened = True
        elif text[index] == "}":
            depth -= 1
            if opened and depth == 0:
                return start, text[: index].count("\n") + 1
    return start, start


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


def _record_story_edges(graph: Graph, classes: list[dict]) -> None:
    stories = graph.practice("stories")
    clean = graph.practice("clean_engineering")
    operations = [node for node in clean.by_id.values() if node.type == "Operation"]
    properties = [node for node in clean.by_id.values() if node.type == "Property"]
    classes_by_name = {node.name: node for node in clean.by_id.values() if node.type == "OoadClass"}
    modules = {node.name: node for node in clean.by_id.values() if node.type == "Module"}
    steps = [node for node in stories.by_id.values() if node.type == "Step"]
    examples = [node for node in stories.by_id.values() if node.type == "Example"]
    epics = [node for node in stories.by_id.values() if node.type in {"Epic", "SubEpic"}]
    for step in steps:
        body = _step_body(graph._folder, step)
        for operation in operations:
            if re.search(rf"\.{re.escape(operation.name)}\s*\(", body):
                _edge(stories, "invokes", 12, "relationship", step, operation)
                _edge(clean, "invokes", 12, "relationship", operation, step)
                _edge(clean, "invokedBy", 9, "relationship", operation, step)
                module_name = Path(operation.source.file).parent.name
                module = modules.get(module_name)
                epic = _epic_for(step, epics)
                if module is not None and epic is not None:
                    _edge(clean, "usedBy", 14, "relationship", module, epic)
                    _edge(stories, "uses", 9, "relationship", epic, module)
        for example in examples:
            if re.search(rf"\b{re.escape(example.name)}\b", body) and step.name.lower().startswith("then"):
                _edge(stories, "observes", 8, "relationship", step, example)
    for example in examples:
        text = _example_source(graph._folder, example.name)
        for name, class_node in classes_by_name.items():
            if re.search(rf"\b{re.escape(name)}\b", text):
                _edge(stories, "demonstrates", 4, "grouped", example, class_node)
                _edge(clean, "demonstrates", 4, "grouped", class_node, example)
                _edge(clean, "demonstratedThrough", 8, "relationship", class_node, example)
        for prop in properties:
            if re.search(rf"\.{re.escape(prop.name)}\b", text):
                _edge(stories, "retrievedUsing", 11, "relationship", example, prop)
                _edge(clean, "retrievedUsing", 11, "relationship", prop, example)


def _edge(practice, kind: str, order: int, display: str, parent, child) -> None:
    practice.record({"kind": kind, "order": order, "display": display}, parent, child)


def _step_body(root: Path | None, step) -> str:
    if root is None or not step.source.file:
        return ""
    path = root / step.source.file
    if not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = max(0, step.source.start_line - 1)
    chunk = lines[start : start + 40]
    return "\n".join(chunk)


def _example_source(root: Path | None, name: str) -> str:
    if root is None:
        return ""
    for file in root.rglob("*.ts"):
        text = file.read_text(encoding="utf-8")
        if re.search(rf"function\s+{re.escape(name)}\b", text):
            return text
    return ""


def _epic_for(step, epics: list):
    file = step.source.file
    for epic in epics:
        if epic.source.file and file.startswith(str(Path(epic.source.file).parent).replace("\\", "/")):
            return epic
    return epics[0] if epics else None


def _record_lern(graph: Graph, root: Path, classes: list[dict]) -> None:
    """LERN overlay nodes. File shape selects the overlay type."""
    ddd = graph.practice("ddd") if "ddd" in graph.practices else None
    stories = graph.practice("stories") if "stories" in graph.practices else None
    if ddd is None or stories is None:
        return
    roots = {cls["name"]: cls for cls in classes if cls["name"] in {item["name"] for item in classes}}
    entity_ids = {node.name: node for node in ddd.by_id.values() if node.type == "EntityRoot"}
    for file in sorted(root.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(root).as_posix()
        if file.name.endswith("-node.ts"):
            _lern_type(ddd, relative, "DomainNode", entity_ids, "hosts")
        elif file.name.endswith("-client.tsx"):
            _lern_type(ddd, relative, "DomainClient", entity_ids, "interacts")
        elif file.name.endswith(".story.shared.ts"):
            _lern_story(stories, relative, "StoryShared")
        elif file.name.endswith(".story.server.spec.ts"):
            _lern_story(stories, relative, "ServerSpec")
        elif file.name.endswith(".story.domain.spec.ts"):
            _lern_story(stories, relative, "DomainSpec")
        elif "playwright" in file.name and file.suffix == ".ts":
            _lern_story(stories, relative, "PlaywrightSpec")


def _lern_type(practice, relative: str, semantic: str, entities: dict, kind: str) -> None:
    name = Path(relative).stem
    node_id = f"ddd:{semantic}:{relative}"
    practice.apply_nodes([[node_id, name, semantic, "ddd", relative, 1, 1]])
    folder = Path(relative).parent.name
    for entity in entities.values():
        if folder and folder.replace("-", "").lower() in entity.source.file.replace("-", "").lower():
            practice.record({"kind": kind, "order": 5, "display": "relationship"}, practice.by_id[node_id], entity)
            return


def _lern_story(practice, relative: str, semantic: str) -> None:
    name = Path(relative).name
    node_id = f"stories:{semantic}:{relative}"
    practice.apply_nodes([[node_id, name, semantic, "stories", relative, 1, 1]])
