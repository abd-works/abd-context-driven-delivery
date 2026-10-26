"""Load a working copy into the explorer graph from the practice models.

Clean engineering and DDD come from the TypeScript class parser. Stories come
from the story model. A selected pattern overlay adds the nodes that overlay names.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from harness.graph.bound_node import schema_sync_paused
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
_VIEW_EXPORT = re.compile(r"export\s+function\s+(\w+View)\s*\(")
_CONTEXT_ARROW = re.compile(r"^[\s\-*>]*(.+?)\s*→\s*(.+?)\s*$")
_VIEW_SKIP_SUFFIXES = ("-form", "-fields", "-banner", "-messages", "-footer", "-loaded", "-client")
_CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py"}
_SKIP_DIRS = {".codeql", ".git", ".context", "node_modules", "__pycache__", ".sessions", "retired"}


def _report(graph: Graph, message: str) -> None:
    graph.report_progress(message)


def _typescript_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return [
        file
        for file in folder.rglob("*")
        if file.is_file() and file.suffix.lower() in {".ts", ".tsx"}
    ]


def fill_working_copy(graph: Graph) -> None:
    source = graph._folder
    if source is None:
        return
    clean = graph.practice("clean_engineering") if "clean_engineering" in graph.practices else None
    with schema_sync_paused():
        classes = _record_clean(clean, source) if clean is not None else []
        if "ddd" in graph.practices:
            _record_ddd(graph.practice("ddd"), source, classes)
    if "stories" in graph.practices:
        _record_stories(graph.practice("stories"), source)
        if clean is not None:
            _record_story_edges(graph, classes)
    if "bdd" in graph.practices:
        _report(graph, "bdd · node types")
        _offer(graph.practice("bdd"), ["Spec", "Description", "Context", "Observation"])
        with schema_sync_paused():
            _record_bdd(graph.practice("bdd"), source)
    if "ux" in graph.practices:
        _report(graph, "ux · node types")
        _offer(graph.practice("ux"), ["UxMap", "Screen"])
    if _overlay_selected(graph, "lern_domain_driven"):
        _record_lern(graph, source, classes)
    _register_overlay_schema_catalog(graph)
    for practice in graph.practices.values():
        attach_rules(practice)
        practice.loaded = ["nodes", "edges", "rules"]


def _offer(practice, types: list[str]) -> None:
    for name in types:
        practice.node_types.add(name)
    practice.loaded = ["nodes", "edges", "rules"]


def _overlay_selected(graph: Graph, pattern: str) -> bool:
    return any(pattern in item.replace("\\", "/").split("/") for item in graph.overlays)


def _register_overlay_schema_catalog(graph: Graph) -> None:
    """Expose overlay schema node and connector types in the filter lists before rules run."""
    from harness.graph.graph import EdgeType
    from harness.graph.schema_edges import overlay_edge_display, relationship_kinds_for_patterns
    from harness.graph.schema_rules import active_overlay_patterns, schema_semantic_types_for_practice

    active = active_overlay_patterns(tuple(graph.overlays))
    if not active:
        return
    edge_kinds = relationship_kinds_for_patterns(active)
    for name, practice in graph.practices.items():
        for node_type in schema_semantic_types_for_practice(name, active):
            practice.node_types.add(node_type)
        for kind in edge_kinds.get(name, ()):
            if kind not in practice.edge_types:
                practice.edge_types[kind] = EdgeType(kind, 5, overlay_edge_display(kind))


_FOLDER_FACTS = (
    "has_module_context",
    "has_bounded_context",
    "modules_heading",
    "model_blocks",
    "is_a_in_context",
    "child_parent_in_context",
    "public_source_internal",
    "public_source_files",
)
_CLASS_FACTS = (
    "bases",
    "method_count",
    "operation_shapes",
    "property_names",
    "constructs",
    "composes_peers",
    "peer_names",
    "module_helpers",
    "prose_comment",
    "prototype_swap",
    "bold_interaction_lines",
    "bold_invariant_lines",
)
_OPERATION_FACTS = (
    "line_count",
    "max_control_flow_depth",
    "has_bare_catch",
    "swallows_exceptions",
    "unnamed_literal_numbers",
    "is_static",
    "is_classmethod",
    "is_property",
    "body_fingerprint",
    "callees",
    "peer_private_access",
    "private_reach",
    "io_and_domain",
    "io_and_domain_callees",
    "raises_on_empty",
    "exception_without_message",
    "generic_exception_message",
    "mutates_without_record",
    "prose_comment",
    "bold_interaction_lines",
    "bold_invariant_lines",
)
_PARAMETER_FACTS = ("type_hint", "operation_name", "property_setter")


def _record_clean(practice, root: Path) -> list[dict]:
    _report(practice.graph, "clean_engineering · folders")
    roles = _code_folders(root)
    parsed: list[dict] = []
    nodes = []
    edges = []
    root_id = practice.root_node.node_id
    files = _code_files(root)
    class_names = _class_names(files, practice.graph)
    ids = {rel: f"clean_engineering:{kind}:{rel}" for rel, kind in roles.items()}
    folders = {rel: _folder_module(root / rel) for rel in roles}
    for index, file in enumerate(files, start=1):
        relative = file.relative_to(root).as_posix()
        _report(practice.graph, f"clean_engineering · classes · {index}/{len(files)} · {relative}")
        owner = _nearest(str(Path(relative).parent).replace("\\", "/"), roles)
        module, text = _parsed_module(file, root)
        if module is None:
            continue
        if owner:
            folders[owner].dependencies.extend(module.dependencies)
        for cls in module.classes:
            parsed.append(_class_fact(practice, text, relative, ids.get(owner, root_id), cls, class_names, nodes, edges))
    for rel in sorted(roles, key=lambda item: (item.count("/"), item)):
        kind = roles[rel]
        parent = _enclosing_id(rel, roles, ids, root_id)
        folders[rel].dependencies = sorted(_imported_folders(folders[rel].dependencies, ids, rel))
        folder_row = [ids[rel], Path(rel).name, kind, "clean_engineering", rel, 1, 1]
        nodes.append(_fact_row(folder_row, _facts_of(folders[rel], _FOLDER_FACTS + ("dependencies",))))
        edges.append([parent, ids[rel], "owns", 2, "direct"])
        if kind == "Package":
            edges.append([ids[rel], parent, "belongsTo", 5, "relationship"])
    practice.apply_nodes(nodes)
    practice.apply_edges(edges)
    practice.loaded = ["nodes", "edges", "rules"]
    return parsed


def _code_files(root: Path) -> list[Path]:
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in _SKIP_DIRS and not name.startswith(".")]
        found.extend(Path(dirpath) / name for name in filenames if Path(name).suffix.lower() in _CODE_SUFFIXES)
    return sorted(found)


def _folder_module(folder: Path):
    from cdd_guidance.practices.clean_engineering.model.base_class_model import Module

    module = Module(name=folder.name, sequential_order=1)
    module.load_folder_facts(folder)
    return module


def _parsed_module(file: Path, root: Path):
    """The language model's module for one source file, with its source facts loaded, and the file text.

    A file without classes still gets its language's module so its imports are recorded.
    """
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


def _imported_folders(targets: list[str], ids: dict[str, str], own: str) -> set[str]:
    """Graph folder each import lands in (longest match); imports of the folder itself drop out."""
    found: set[str] = set()
    for target in targets:
        parts = target.split("/")
        while parts and "/".join(parts) not in ids:
            parts.pop()
        folder = "/".join(parts)
        if folder and folder != own:
            found.add(ids[folder])
    return found


_SPEC_FACTS = ("patches_infrastructure", "signature_marker", "top_level_describes", "code_like_describe_lines", "private_probe")
_BEHAVIOR_FACTS = ("expect_count", "has_implementation", "private_probe")
_BEHAVIOR_EDGES = {"Description": ("descriptions", 1), "Context": ("contexts", 2), "Observation": ("observations", 3)}


def _record_bdd(practice, root: Path) -> None:
    """Each spec file's language model reads its describe tree; every node loads its own facts."""
    from cdd_guidance.practices.bdd.model.spec_source import is_spec_file

    nodes: list = []
    edges: list = []
    specs = [file for file in _code_files(root) if is_spec_file(file)]
    for index, file in enumerate(specs, start=1):
        relative = file.relative_to(root).as_posix()
        _report(practice.graph, f"bdd · specs · {index}/{len(specs)} · {relative}")
        _record_spec(practice, file, relative, nodes, edges)
    practice.apply_nodes(nodes)
    practice.apply_edges(edges)
    practice.loaded = ["nodes", "edges", "rules"]


def _record_spec(practice, file: Path, relative: str, nodes: list, edges: list) -> None:
    from cdd_guidance.practices.bdd.model.bdd_model import PythonBddModel, TypeScriptBddModel

    try:
        text = file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    spec = (PythonBddModel() if file.suffix == ".py" else TypeScriptBddModel()).parse_code(text)
    spec.load_source_facts(text)
    lines = text.splitlines()
    spec_id = f"bdd:Spec:{relative}"
    nodes.append(_fact_row([spec_id, file.stem, "Spec", "bdd", relative, 1, max(1, len(lines))], _facts_of(spec, _SPEC_FACTS)))
    edges.append([practice.root_node.node_id, spec_id, "owns", 2, "direct"])
    ids = {id(spec): spec_id}
    for node in spec.behavior_nodes():
        node.load_span_facts("\n".join(lines[node.line - 1 : node.end_line]))
        node_id = f"bdd:{node.type}:{relative}:{node.line}:{node.name}"
        ids[id(node)] = node_id
        row = [node_id, node.name, node.type, "bdd", relative, node.line, node.end_line]
        nodes.append(_fact_row(row, _facts_of(node, _BEHAVIOR_FACTS)))
        kind, order = _BEHAVIOR_EDGES[node.type]
        edges.append([ids.get(id(node.parent), spec_id), node_id, kind, order, "direct"])


_TACTICAL_FACTS = (
    "peer_private_operations",
    "public_derive_operations",
    "delegating_operations",
    "identity_free_loads",
    "tactical_stereotype",
)


def _tactical_facts(member: dict) -> dict:
    """The DDD building block for a class member loads its own tactical facts."""
    from cdd_guidance.practices.ddd.model.nodes import DomainService, Entity, Factory, Repository, Specification, ValueObject

    block_types = {
        "EntityRoot": Entity,
        "Entity": Entity,
        "ValueObject": ValueObject,
        "Repository": Repository,
        "DomainService": DomainService,
        "Factory": Factory,
        "Specification": Specification,
    }
    block_type = block_types.get(member["kind"])
    if block_type is None:
        return {}
    block = block_type(name=member["name"], sequential_order=1)
    if member["kind"] == "EntityRoot":
        block.is_root = True
    block.load_tactical_facts(member["model"], member["text"])
    return _facts_of(block, _TACTICAL_FACTS)


def _facts_of(owner, names: tuple[str, ...], extra: dict | None = None) -> dict:
    """The facts a model object loaded on itself, plus what only the recorder knows."""
    facts = {name: getattr(owner, name) for name in names if hasattr(owner, name)}
    facts.update(extra or {})
    return facts


def _fact_row(row: list, facts: dict) -> list:
    from harness.graph.node_data import encode_node_data

    payload = encode_node_data(facts)
    return row + ["", payload] if payload else row


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


def _bounded_context_id(folder: str, context_ids: dict[str, str], root_id: str) -> str:
    """Longest matching bounded context for a source folder, else root or default context."""
    rel = _context_for(folder, list(context_ids))
    return context_ids.get(rel) or context_ids.get(".") or root_id


def _class_fact(practice, text: str, relative: str, module_id: str, cls, class_names: set[str], nodes: list, edges: list) -> dict:
    class_id = f"clean_engineering:OoadClass:{relative}:{cls.name}"
    if cls.line and cls.end_line:
        class_start, class_end = cls.line, cls.end_line
    else:
        class_start, class_end = _class_extent(text, cls.name, getattr(cls, "line", None) or 1)
    lines = text.splitlines()
    cls.load_source_facts("\n".join(lines[class_start - 1 : class_end]))
    class_facts = _facts_of(cls, _CLASS_FACTS, {"folder": module_id})
    class_row = [class_id, cls.name, "OoadClass", "clean_engineering", relative, class_start, class_end]
    nodes.append(_fact_row(class_row, class_facts))
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
    for operation in cls.own_operations():
        if operation.name in {"constructor", "get", "set"} or getattr(operation, "is_property", False):
            continue
        if str(operation.name).startswith("_"):
            continue
        from cdd_guidance.practices.clean_engineering.model.operation import operation_source_span

        span = _method_span(text, operation.name, getattr(operation, "line", None) or 1)
        model_span = operation_source_span(operation)
        if model_span is not None:
            start, end = model_span
        else:
            start = getattr(operation, "line", None) or span[0]
            line_count = getattr(operation, "line_count", None)
            end = start + line_count - 1 if line_count and line_count > 0 else span[1]
        op_id = f"clean_engineering:Operation:{relative}:{operation.name}:{cls.name}"
        operation.load_span_facts("\n".join(lines[start - 1 : end]))
        signature = {"owner": cls.name, "parameters": [[p.name, (p.type_hint or "").strip()] for p in operation.parameters]}
        op_row = [op_id, operation.name, "Operation", "clean_engineering", relative, start, end]
        nodes.append(_fact_row(op_row, _facts_of(operation, _OPERATION_FACTS, signature)))
        edges.append([class_id, op_id, "owns", 2, "direct"])
        for parameter in operation.parameters:
            param_id = f"clean_engineering:Parameter:{relative}:{parameter.name}:{cls.name}.{operation.name}"
            parameter.load_operation_facts(operation)
            nodes.append(_fact_row([param_id, parameter.name, "Parameter", "clean_engineering", relative, span[0], span[0]], _facts_of(parameter, _PARAMETER_FACTS)))
            edges.append([op_id, param_id, "hasParameter", 6, "relationship"])
        if _names_class(getattr(operation, "return_type", "") or "", class_names):
            for other in class_names:
                if other in (operation.return_type or ""):
                    other_id = _class_id_named(nodes, other)
                    if other_id:
                        edges.append([op_id, other_id, "returns", 10, "relationship"])
    return {
        "name": cls.name,
        "id": class_id,
        "file": relative,
        "operations": list(cls.operations),
        "text": text,
        "model": cls,
        "facts": class_facts,
        "extent": (class_start, class_end),
    }


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
    from cdd_guidance.practices.ddd.model.stereotypes import class_declaration_decorated_name

    return class_declaration_decorated_name(text, name)


def _class_names(files: list[Path], graph: Graph | None = None) -> set[str]:
    names = set()
    for index, file in enumerate(files, start=1):
        if graph is not None:
            _report(graph, f"clean_engineering · class names · {index}/{len(files)} · {file.name}")
        try:
            names.update(_CLASS_NAMES.findall(file.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError):
            continue
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
    from cdd_guidance.practices.clean_engineering.model.c_family_parse import CFamilyParse

    return CFamilyParse.method_span_in_text(text, name, fallback)


def _record_ddd(practice, root: Path, classes: list[dict]) -> None:
    from cdd_guidance.practices.ddd.model.stereotypes import inferred_tactical_kind

    _report(practice.graph, "ddd · bounded contexts")
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
        folder_facts = _facts_of(_folder_module(root / rel), _FOLDER_FACTS)
        nodes.append(_fact_row([context_id, name, "BoundedContext", "ddd", markdown, 1, end], folder_facts))
        parent_rel = _context_for(str(Path(rel).parent).replace("\\", "/"), [item[0] for item in contexts]) if rel != "." else ""
        if rel != "." and parent_rel == rel:
            parent_rel = ""
        parent_id = context_ids.get(parent_rel) or practice.root_node.node_id
        edges.append([parent_id, context_id, "owns", 2, "direct"])
        if parent_rel:
            edges.append([context_id, parent_id, "belongsTo", 3, "relationship"])
    by_id = {}
    ddd_root_id = practice.root_node.node_id
    for folder in sorted(members):
        context_id = _bounded_context_id(folder, context_ids, ddd_root_id)
        aggregate_id = f"ddd:Aggregate:{folder}"
        aggregate_facts = _facts_of(_folder_module(root / folder), _FOLDER_FACTS)
        nodes.append(_fact_row([aggregate_id, Path(folder).name, "Aggregate", "ddd", folder, 1, 1], aggregate_facts))
        edges.append([context_id, aggregate_id, "owns", 2, "direct"])
        edges.append([aggregate_id, context_id, "belongsTo", 3, "relationship"])
        for member in members[folder]:
            member_id = f"ddd:{member['kind']}:{member['file']}:{member['name']}"
            start, end = member["extent"]
            member_row = [member_id, member["name"], member["kind"], "ddd", member["file"], start, end]
            nodes.append(_fact_row(member_row, {**member["facts"], **_tactical_facts(member)}))
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
    from cdd_guidance.practices.stories.model.graph_story_model import GraphStoryModel
    from cdd_guidance.practices.stories.model.story_model import StoryModel
    from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel

    files: dict[str, str] = {}
    sources = _typescript_files(source)
    total = len(sources)
    graph = practice.graph

    def report(phase: str, detail: str) -> None:
        _report(graph, f"stories · {phase} · {detail}")

    for index, path in enumerate(sources, start=1):
        relative = path.relative_to(source).as_posix()
        _report(graph, f"stories · {index}/{total} · {relative}")
        files[relative] = path.read_text(encoding="utf-8")
    _report(graph, "stories · parse")
    model = TypeScriptStoryModel("tests").load(files, on_file=lambda detail: report("parse", detail))
    if not model.epics:
        _report(graph, "stories · markdown")
        model = StoryModel.load(source, on_file=lambda detail: report("markdown", detail))
    _report(graph, "stories · record")
    GraphStoryModel(model).record(practice, on_node=lambda detail: report("record", detail))


def _gwt_phase(step) -> str:
    if step.type in {"Given", "When", "Then"}:
        return step.type.lower()
    name = (step.name or "").strip().casefold()
    for prefix in ("given", "when", "then"):
        if name.startswith(prefix + " "):
            return prefix
    return ""


def _record_story_edges(graph: Graph, classes: list[dict]) -> None:
    stories = graph.practice("stories")
    clean = graph.practice("clean_engineering")
    operations = [node for node in clean.by_id.values() if node.type == "Operation"]
    properties = [node for node in clean.by_id.values() if node.type == "Property"]
    classes_by_name = {node.name: node for node in clean.by_id.values() if node.type == "OoadClass"}
    modules = {node.name: node for node in clean.by_id.values() if node.type == "Module"}
    steps = [node for node in stories.by_id.values() if node.type in {"Step", "Given", "When", "Then"}]
    examples = [node for node in stories.by_id.values() if node.type == "Example"]
    epics = [node for node in stories.by_id.values() if node.type in {"Epic", "SubEpic"}]
    total_steps = len(steps)
    for index, step in enumerate(steps, start=1):
        _report(graph, f"stories · steps · {index}/{total_steps} · {step.name}")
        body = _step_body(graph._folder, step)
        callees = list(getattr(step, "data", {}).get("callees") or [])
        for operation in operations:
            if operation.name in callees or re.search(rf"\.{re.escape(operation.name)}\s*\(", body):
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
            if not re.search(rf"\b{re.escape(example.name)}\b", body):
                continue
            phase = _gwt_phase(step)
            if phase in {"given", "when", "then"}:
                _edge(stories, "observes", 8, "relationship", step, example)
    total_examples = len(examples)
    for index, example in enumerate(examples, start=1):
        _report(graph, f"stories · examples · {index}/{total_examples} · {example.name}")
        text = _example_source(graph._folder, example.name, graph)
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


def _example_source(root: Path | None, name: str, graph: Graph | None = None) -> str:
    if root is None:
        return ""
    files = [file for file in root.rglob("*.ts") if file.is_file()]
    total = len(files)
    for index, file in enumerate(files, start=1):
        if graph is not None:
            relative = file.relative_to(root).as_posix()
            _report(graph, f"stories · example {name} · {index}/{total} · {relative}")
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
    """LERN overlay: schema tier nodes from repo files, wired with schema relationship kinds, carrying tier facts."""
    from cdd_guidance.patterns.lern_domain_driven.tier_facts import story_shared_facts, test_setup_text

    ddd = graph.practice("ddd") if "ddd" in graph.practices else None
    stories = graph.practice("stories") if "stories" in graph.practices else None
    if ddd is None or stories is None:
        return
    _record_lern_context_mappings(graph, root, ddd)
    aggregates = {
        node.source.file.replace("\\", "/"): node
        for node in ddd.by_id.values()
        if node.type == "Aggregate"
    }
    entity_roots = [node for node in ddd.by_id.values() if node.type == "EntityRoot"]
    repositories = [node for node in ddd.by_id.values() if node.type == "Repository"]

    setup_text = test_setup_text(root)
    for folder, aggregate in sorted(aggregates.items()):
        slug = Path(folder).name
        artifacts: dict[str, object] = {}
        for filename, semantic in (
            (f"{slug}-node.ts", "NodeRoot"),
            (f"{slug}-client.tsx", "ClientRoot"),
            (f"{slug}-routes.ts", "Route"),
            (f"{slug}.json", "JsonStore"),
        ):
            relative = f"{folder}/{filename}"
            if not (root / relative).is_file():
                continue
            artifacts[semantic] = _lern_ddd_file_node(ddd, relative, semantic)
            _lern_schema_edge(ddd, "owns", aggregate, artifacts[semantic])

        folder_entity_roots = [node for node in entity_roots if _aggregate_folder(node.source.file) == folder]
        folder_repositories = [node for node in repositories if _aggregate_folder(node.source.file) == folder]

        node_root = artifacts.get("NodeRoot")
        client_root = artifacts.get("ClientRoot")
        route = artifacts.get("Route")
        json_store = artifacts.get("JsonStore")
        _set_tier_facts(root, folder, aggregate, node_root, route, folder_repositories, setup_text)

        for entity in folder_entity_roots:
            if node_root is not None:
                _lern_schema_edge(ddd, "nodeRoot", entity, node_root)
                _lern_schema_edge(ddd, "hosts", entity, node_root)
            if client_root is not None:
                _lern_schema_edge(ddd, "interacts", entity, client_root)

        if client_root is not None and route is not None:
            _lern_schema_edge(ddd, "calls", client_root, route)
        if route is not None and node_root is not None:
            _lern_schema_edge(ddd, "nodeRoot", route, node_root)

        for repo in folder_repositories:
            if json_store is not None:
                _lern_schema_edge(ddd, "writes", repo, json_store)
            if node_root is not None:
                _lern_schema_edge(ddd, "nodeRepository", node_root, repo)

        views = _lern_views_in_aggregate(root, folder, slug, ddd, aggregate, artifacts, folder_repositories)
        if node_root is not None:
            for view in views:
                _lern_schema_edge(ddd, "views", node_root, view)

    for file in sorted(root.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(root).as_posix()
        if file.name.endswith(".story.shared.ts"):
            _lern_story_file(stories, relative, "StoryShared")
            shared = stories.by_id.get(f"stories:StoryShared:{relative}")
            for key, value in story_shared_facts(file.read_text(encoding="utf-8")).items():
                shared.set_fact(key, value)
        elif file.name.endswith(".story.server.spec.ts"):
            _lern_story_file(stories, relative, "ServerSpec")
        elif file.name.endswith(".story.domain.spec.ts"):
            _lern_story_file(stories, relative, "DomainSpec")
        elif "playwright" in file.name and file.suffix == ".ts":
            _lern_story_file(stories, relative, "PlaywrightSpec")


def _set_tier_facts(root: Path, folder: str, aggregate, node_root, route, repositories, setup_text: str) -> None:
    """Read each LERN tier file once and record what its rules need on the node it became."""
    from cdd_guidance.patterns.lern_domain_driven.tier_facts import node_root_facts, route_facts, unreset_instances, web_path_literals

    aggregate.set_fact("web_path_literals", web_path_literals(root, folder))
    tiers = ((node_root, lambda text: node_root_facts(text, setup_text)), (route, route_facts))
    for tier_node, facts_of in tiers:
        if tier_node is None:
            continue
        for key, value in facts_of((root / tier_node.source.file).read_text(encoding="utf-8")).items():
            tier_node.set_fact(key, value)
    for repository in repositories:
        text = (root / repository.source.file).read_text(encoding="utf-8")
        repository.set_fact("unreset_instances", unreset_instances(text, [repository.name], setup_text))


def _file_line_span(root: Path, relative: str) -> tuple[int, int]:
    path = root / relative
    if not path.is_file():
        return 1, 1
    text = path.read_text(encoding="utf-8")
    if not text:
        return 1, 1
    end = text.count("\n") + (0 if text.endswith("\n") else 1)
    return 1, max(1, end)


def _aggregate_folder(file_path: str) -> str:
    return str(Path(file_path).parent).replace("\\", "/")


def _is_lern_view_file(filename: str, slug: str) -> bool:
    if filename == f"{slug}-client.tsx" or not filename.endswith(".tsx"):
        return False
    return not any(filename.endswith(f"{suffix}.tsx") for suffix in _VIEW_SKIP_SUFFIXES)


def _lern_views_in_aggregate(root: Path, folder: str, slug: str, ddd, aggregate, artifacts, repositories) -> list:
    views = []
    folder_path = root / folder
    if not folder_path.is_dir():
        return views
    client_root = artifacts.get("ClientRoot")
    node_root = artifacts.get("NodeRoot")
    repo = repositories[0] if repositories else None
    for file in sorted(folder_path.glob("*.tsx")):
        if not _is_lern_view_file(file.name, slug):
            continue
        text = file.read_text(encoding="utf-8")
        match = _VIEW_EXPORT.search(text)
        if match is None:
            continue
        relative = file.relative_to(root).as_posix()
        view = _lern_ddd_file_node(ddd, relative, "View", display_name=match.group(1))
        views.append(view)
        _lern_schema_edge(ddd, "view", aggregate, view)
        if client_root is not None:
            _lern_schema_edge(ddd, "clientRoot", view, client_root)
        if repo is not None:
            _lern_schema_edge(ddd, "nodeRepository", view, repo)
    return views


def _record_lern_context_mappings(graph: Graph, root: Path, ddd) -> None:
    bounded_contexts = [node for node in ddd.by_id.values() if node.type == "BoundedContext"]
    aggregates = [node for node in ddd.by_id.values() if node.type == "Aggregate"]

    def resolve_aggregate(label: str):
        label = label.strip()
        for node in aggregates:
            if node.name == label or label.endswith(f"· {node.name}") or label.endswith(f"·{node.name}"):
                return node
        tail = label.split("·")[-1].strip() if "·" in label else label
        for node in aggregates:
            if node.name == tail:
                return node
        return None

    for bc_node in bounded_contexts:
        markdown = bc_node.source.file
        if not markdown or markdown == ".":
            continue
        path = root / markdown
        if not path.is_file():
            continue
        for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = _CONTEXT_ARROW.match(line.strip())
            if match is None:
                continue
            left, right = match.group(1).strip(), match.group(2).strip()
            map_id = f"ddd:ContextMapping:{markdown}:{index}"
            if map_id in ddd.by_id:
                continue
            label = f"{left} → {right}"
            ddd.apply_nodes([[map_id, label, "ContextMapping", "ddd", markdown, index, index]])
            mapping = ddd.by_id[map_id]
            _lern_schema_edge(ddd, "mappedTo", bc_node, mapping)
            local = resolve_aggregate(left)
            remote = resolve_aggregate(right)
            if local is not None:
                _lern_schema_edge(ddd, "local", mapping, local)
            if remote is not None:
                _lern_schema_edge(ddd, "remote", mapping, remote)


def _lern_schema_edge(practice, kind: str, parent, child) -> None:
    from harness.graph.schema_edges import overlay_edge_display

    order = 2 if overlay_edge_display(kind) == "direct" else 5
    _edge(practice, kind, order, overlay_edge_display(kind), parent, child)


def _lern_ddd_file_node(practice, relative: str, semantic: str, display_name: str | None = None):
    name = display_name or Path(relative).stem
    node_id = f"ddd:{semantic}:{relative}"
    if node_id in practice.by_id:
        return practice.by_id[node_id]
    source_root = Path(practice.source_root) if practice.source_root else None
    start, end = _file_line_span(source_root, relative) if source_root is not None else (1, 1)
    practice.apply_nodes([[node_id, name, semantic, "ddd", relative, start, end]])
    return practice.by_id[node_id]


def _parent_story_scope(stories, relative: str):
    rel = relative.replace("\\", "/")
    candidates: list[tuple[int, object]] = []
    for node in stories.by_id.values():
        if node.type not in {"Epic", "SubEpic"}:
            continue
        epic_dir = _aggregate_folder(node.source.file) if node.source.file else ""
        if epic_dir and (rel == epic_dir or rel.startswith(f"{epic_dir}/")):
            candidates.append((len(epic_dir), node))
    if candidates:
        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]
    parent_name = Path(rel).parent.name.replace("_", "-")
    for node in stories.by_id.values():
        if node.type in {"Epic", "SubEpic"} and node.name.replace("_", "-") == parent_name:
            return node
    return None


def _lern_story_file(practice, relative: str, semantic: str) -> None:
    name = Path(relative).name
    node_id = f"stories:{semantic}:{relative}"
    source_root = Path(practice.source_root) if practice.source_root else None
    start, end = _file_line_span(source_root, relative) if source_root is not None else (1, 1)
    practice.apply_nodes([[node_id, name, semantic, "stories", relative, start, end]])
    node = practice.by_id.get(node_id)
    parent = _parent_story_scope(practice, relative)
    if node is not None and parent is not None:
        _lern_schema_edge(practice, "owns", parent, node)
