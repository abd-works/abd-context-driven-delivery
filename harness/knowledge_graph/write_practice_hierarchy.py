"""Load a PracticeGraph and write the practice hierarchy report."""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from collections import defaultdict
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_HARNESS = (_REPO / "harness").resolve()
sys.path[:] = [
    item
    for item in sys.path
    if not item or Path(item).resolve() != _HARNESS
]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
import mcp.types  # SDK; harness/mcp must not shadow this
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from harness.knowledge_graph.model.practice_graph import PracticeGraph, RuleSlugs
from harness.knowledge_graph.model.graph_node import Kind
from harness.knowledge_graph.model.codeql import (
    CodeQL,
    attach_query_server,
    detach_query_server,
)
from harness.knowledge_graph.model.graph_rules import closest_fidelity
from harness.mcp.codeql_query_daemon import QueryServerClient
from harness.knowledge_graph.model.dot_graph import (
    _hierarchy_line,
    _hierarchy_violations,
    graph_name_matches,
    prune_to_violations,
    walk_hierarchy,
)
from practices.clean_engineering.model.codeql.codeql_model import Module

_DEFAULT_PRACTICES = ("clean_engineering", "bdd", "stories", "ddd")


def _append_line(lines: list[str], depth: int, node, graph: PracticeGraph) -> None:
    try:
        line = _hierarchy_line(depth, node)
        mark = _hierarchy_violations(node)
        lines.append(f"{line}  {mark}" if mark else line)
    except Exception as error:
        name = getattr(node, "name", "") or type(node).__name__
        graph.record_partial_failure(f"hierarchy {name}", error)
        lines.append(f"{'  ' * depth}ERROR: {name}: {error}")


def _render_kg(
    graph: PracticeGraph,
    graphs: list[str] | None = None,
    violations_only: bool = False,
) -> str:
    root = graph.ce_model
    if root is None:
        raise RuntimeError("no Clean Engineering model on the graph")
    lines: list[str] = []
    modules = [
        module
        for _, module in root.outgoing()
        if isinstance(module, Module) and graph_name_matches(module.name, graphs)
    ]
    walked: list[tuple[int, object]] = [(0, root)]
    for module in modules:
        walked.extend((depth + 1, node) for depth, node in walk_hierarchy(module))
    if violations_only:
        walked = prune_to_violations(walked)
    for depth, node in walked:
        _append_line(lines, depth, node, graph)
    return "\n".join(lines) + ("\n" if lines else "")


def _slugs_for(graph: PracticeGraph, practices: tuple[str, ...]) -> RuleSlugs:
    wanted = set(practices)
    return RuleSlugs(
        [
            rule.slug
            for rule in graph.rule_registry
            if rule.practice in wanted and rule.graph_evaluated
        ]
    )


_CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py"}
_STORY_CODE = re.compile(
    r".+_story\.(test|spec)\.[jt]sx?$|.+\.examples\.[jt]sx?$|.+\.e2e\.[jt]sx?$"
)
_MODULE_CONTEXT_NAMES = ("module-context.md", "architecture-context.md")


def _load_ce_folders(graph: PracticeGraph, workspace: Path) -> None:
    """Modules are repo folders with module context, a child that has it, or non-story code."""
    folders = _ce_folders(workspace)
    if not folders:
        return
    modules: dict[str, Module] = {}
    for index, rel in enumerate(sorted(folders), start=1):
        module = Module(rel.split("/")[-1], index)
        module.folder = rel
        context = folders[rel]
        if context is not None:
            from practices.stories.model.source_location import SourceLocation

            module.source = SourceLocation(
                str(context.relative_to(workspace)).replace("\\", "/"),
                1,
            )
        graph.register(module)
        modules[rel] = module
    for rel, module in modules.items():
        parent_rel = "/".join(rel.split("/")[:-1])
        while parent_rel and parent_rel not in modules:
            parent_rel = "/".join(parent_rel.split("/")[:-1])
        parent = modules.get(parent_rel)
        if parent is None:
            continue
        parent.modules.append(module)
        parent.relate(Kind.OWNS, module)


def _ce_folders(workspace: Path) -> dict[str, Path | None]:
    found: dict[str, Path | None] = {}
    domain = workspace / "domain"
    src = workspace / "src"
    if domain.is_dir():
        start, start_rel = domain, "domain"
    elif src.is_dir():
        start, start_rel = src, "src"
    else:
        start, start_rel = workspace, ""

    def visit(folder: Path, rel: str) -> bool:
        try:
            children = list(folder.iterdir())
        except OSError:
            return False
        context = _module_context(folder) if rel else None
        code = _has_non_story_code(children) if rel else False
        child_kept = False
        for child in children:
            if not child.is_dir() or _skip_ce_dir(child.name, rel):
                continue
            child_rel = f"{rel}/{child.name}" if rel else child.name
            if visit(child, child_rel):
                child_kept = True
        if rel and (context is not None or code or child_kept):
            found[rel] = context
            return True
        return child_kept

    visit(start, start_rel)
    return found


def _skip_ce_dir(name: str, parent_rel: str) -> bool:
    if name in _SKIP_PACKAGES or name.startswith("."):
        return True
    rel = f"{parent_rel}/{name}" if parent_rel else name
    if rel == "stories" or rel.startswith("stories/"):
        return True
    if rel == "tests" or rel.startswith("tests/"):
        return True
    if rel == "apps" or rel.startswith("apps/"):
        return True
    if rel == "packages" or rel.startswith("packages/"):
        return True
    if name == "routes":
        return True
    return False


def _module_context(folder: Path) -> Path | None:
    for name in _MODULE_CONTEXT_NAMES:
        direct = folder / name
        if direct.is_file():
            return direct
        nested = folder / ".context" / name
        if nested.is_file():
            return nested
    return None


def _has_non_story_code(children: list[Path]) -> bool:
    for child in children:
        if not child.is_file() or child.suffix.lower() not in _CODE_SUFFIXES:
            continue
        if _STORY_CODE.match(child.name):
            continue
        return True
    return False


_SKIP_PACKAGES = {
    "node_modules",
    ".git",
    "dist",
    "__pycache__",
    ".venv",
    "venv",
    "coverage",
    ".codeql",
    ".context",
    ".cursor",
    ".vscode",
    ".github",
    "htmlcov",
    "examples",
}


def _node_folder(node: dict) -> str:
    folder = (node.get("properties") or {}).get("folder") or ""
    path = str(folder).replace("\\", "/")
    if path:
        return path
    name = node.get("name") or ""
    if node.get("semantic_type") == "Module" and "." in name:
        return name.replace(".", "/")
    return ""


def _package_node(path: str) -> dict:
    label = path.split("/")[-1] or path or "workspace"
    return {
        "node_id": f"pkg:{path or 'workspace'}",
        "name": label,
        "practice": "",
        "fidelity": None,
        "semantic_type": "Package",
        "properties": {"folder": path},
        "applicable_rules": [],
        "violations": [],
        "source": None,
    }


def _top_level_folders(root: Path) -> list[str]:
    if not root.is_dir():
        return []
    names: list[str] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name in _SKIP_PACKAGES or child.name.startswith("."):
            continue
        if child.name in {"tests", "apps", "stories"}:
            continue
        names.append(child.name)
    return names


def _ensure_packages(
    nodes: list[dict],
    relationships: list[dict],
    root: Path,
) -> None:
    by_path: dict[str, str] = {}
    for node in nodes:
        semantic = node.get("semantic_type")
        if semantic not in ("Module", "Package"):
            continue
        path = _node_folder(node)
        if not path:
            continue
        props = node.setdefault("properties", {})
        props["folder"] = path
        by_path[path] = node["node_id"]
    needed = set(_top_level_folders(root))
    for path in list(by_path):
        if not path.strip():
            continue
        parts = [part for part in path.split("/") if part]
        for index in range(1, len(parts)):
            needed.add("/".join(parts[:index]))
        if parts:
            needed.add(parts[0])
    for path in sorted(item for item in needed if item.strip()):
        if path in by_path:
            continue
        package = _package_node(path)
        nodes.append(package)
        by_path[path] = package["node_id"]
    seen = {(edge["from_id"], edge["to_id"]) for edge in relationships}
    for path, node_id in by_path.items():
        if "/" not in path:
            continue
        parent_path = path.rsplit("/", 1)[0]
        parent_id = by_path.get(parent_path)
        if not parent_id:
            continue
        key = (parent_id, node_id)
        if key in seen:
            continue
        seen.add(key)
        relationships.append(
            {"kind": "owns", "from_id": parent_id, "to_id": node_id}
        )


def _nest_contained_modules(nodes: list[dict], relationships: list[dict]) -> None:
    _ensure_packages(nodes, relationships, Path())
    modules = [
        node
        for node in nodes
        if node.get("semantic_type") == "Module"
    ]
    paths: list[tuple[str, str]] = []
    for node in modules:
        folder = (node.get("properties") or {}).get("folder") or ""
        name = node.get("name") or ""
        path = folder.replace("\\", "/")
        if not path and name.count(".") >= 1:
            path = name.replace(".", "/")
        if path:
            paths.append((node["node_id"], path))
    seen = {(edge["from_id"], edge["to_id"]) for edge in relationships}
    for child_id, child_path in paths:
        nearest: tuple[str, str] | None = None
        for parent_id, parent_path in paths:
            if parent_path == child_path:
                continue
            if not child_path.startswith(parent_path + "/"):
                continue
            if nearest is None or len(parent_path) > len(nearest[1]):
                nearest = (parent_id, parent_path)
        if nearest is None:
            continue
        key = (nearest[0], child_id)
        if key in seen:
            continue
        seen.add(key)
        relationships.append(
            {"kind": "owns", "from_id": nearest[0], "to_id": child_id}
        )


def _step_title(name: str, semantic: str, keyword: str) -> str:
    if semantic != "Step" or not keyword:
        return name
    prefix = f"{keyword} "
    if name.lower().startswith(prefix.lower()):
        return name
    return f"{keyword} {name}"


_STORY_FILE_KINDS = {"Story", "Scenario", "Background", "Epic"}


def _source_dto(node, folder: Path) -> dict | None:
    src = getattr(node, "source", None)
    file = str(getattr(src, "file", "") or "").replace("\\", "/")
    if not file:
        return None
    start = int(getattr(src, "line", 0) or 0)
    end = int(getattr(src, "end_line", 0) or start)
    text = str(getattr(src, "text", "") or "")
    from practices.clean_engineering.model.codeql.codeql_model import SourceLocation, SourceSpan

    semantic = node.semantic_type()
    if semantic in _STORY_FILE_KINDS:
        path = folder / file
        if path.is_file():
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            return {
                "file": file,
                "start_line": 1,
                "end_line": len(lines) or 1,
                "text": "\n".join(lines),
            }
    if start > 0:
        location = SourceSpan(folder).read(
            SourceLocation(file=file, line=start, end_line=end, text=text)
        )
        start, end, text = location.line, location.end_line, location.text
    return {
        "file": file,
        "start_line": start,
        "end_line": end or start,
        "text": text,
    }


def explorer_dto(graph: PracticeGraph, folder: Path) -> dict:
    grouped: dict[str, dict[str, list]] = defaultdict(
        lambda: {"nodes": [], "relationships": []}
    )
    practices: dict[str, str] = {}
    rule_rows: dict[tuple[str, str], list] = {}
    for node in graph.nodes.values():
        practice = getattr(node, "practice", "") or "node"
        practices[node.node_id] = practice
        semantic = node.semantic_type()
        key = (practice, semantic)
        if key not in rule_rows:
            rule_rows[key] = list(
                graph.rule_registry.rules_for_node(
                    practice=practice,
                    semantic_type=semantic,
                )
            )
        matched = rule_rows[key]
        rule_tags: dict[str, str] = {}
        rule_catalog: list[dict[str, str]] = []
        for rule in matched:
            tag = getattr(rule, "tag", "base") or "base"
            rule_tags[rule.slug] = tag
            rule_catalog.append({"slug": rule.slug, "tag": tag})
        hits = graph.violations_for(node)
        properties = {"folder": getattr(node, "folder", "") or ""}
        stereotype = str(getattr(node, "stereotype", "") or "")
        if stereotype:
            properties["stereotype"] = stereotype
        grouped[practice]["nodes"].append(
            {
                "node_id": node.node_id,
                "name": _step_title(
                    getattr(node, "name", None) or semantic or node.node_id,
                    semantic,
                    str(getattr(node, "keyword", "") or ""),
                ),
                "practice": practice,
                "fidelity": closest_fidelity(practice, semantic),
                "semantic_type": semantic,
                "sequential_order": int(getattr(node, "sequential_order", 0) or 0),
                "keyword": str(getattr(node, "keyword", "") or ""),
                "properties": properties,
                "applicable_rules": [rule.slug for rule in matched],
                "rule_tags": rule_tags,
                "rule_catalog": rule_catalog,
                "violations": [
                    {
                        "rule_slug": hit.rule_slug,
                        "message": hit.message,
                        "practice": hit.practice,
                        "fidelity": hit.fidelity,
                        "tag": getattr(hit, "tag", "base") or "base",
                    }
                    for hit in hits
                ],
                "source": _source_dto(node, folder),
            }
        )
    for edge in graph.relationships:
        practice = (
            practices.get(edge.from_id)
            or practices.get(edge.to_id)
            or "node"
        )
        grouped[practice]["relationships"].append(
            {
                "kind": edge.kind,
                "from_id": edge.from_id,
                "to_id": edge.to_id,
                "cardinality": getattr(edge, "cardinality", "") or "",
                "sequential_order": int(getattr(edge, "sequential_order", 0) or 0),
                "immediate": bool(getattr(edge, "immediate", True)),
            }
        )
    all_nodes = [
        node for payload in grouped.values() for node in payload["nodes"]
    ]
    overlay = list(all_nodes)
    package_rels: list[dict] = []
    _ensure_packages(overlay, package_rels, folder)
    package_nodes = [
        node for node in overlay if node.get("semantic_type") == "Package"
    ]
    graphs = [
        {
            "id": f"practice:{name}",
            "name": name,
            "nodes": payload["nodes"],
            "relationships": payload["relationships"],
        }
        for name, payload in sorted(grouped.items())
    ]
    if package_nodes:
        graphs.insert(
            0,
            {
                "id": "practice:workspace",
                "name": "workspace",
                "nodes": package_nodes,
                "relationships": package_rels,
            },
        )
    return {
        "id": str(uuid.uuid4()),
        "folder": str(folder),
        "practice_graphs": graphs,
    }


def main(
    populate: bool = True,
    graphs: list[str] | None = None,
    violations_only: bool = False,
    root: Path | None = None,
    ddd: bool = False,
    as_json: bool = False,
    practices: tuple[str, ...] | None = None,
    rules: bool = False,
) -> None:
    workspace = Path(root) if root is not None else _REPO
    names = ",".join(graphs) if graphs else "all"
    selected = practices if practices else _DEFAULT_PRACTICES
    if ddd and "ddd" not in selected:
        selected = selected + ("ddd",)
    log = sys.stderr if as_json else sys.stdout
    print(
        f"loading {workspace} populate={populate} graphs={names} "
        f"practices={','.join(selected)} violations_only={violations_only}",
        file=log,
        flush=True,
    )
    graph = PracticeGraph(workspace)
    _load_practice_trees(graph, workspace, log)
    ctx = graph.working_context()
    hierarchy_path = ctx / "knowledge-graph-ce-hierarchy.txt"
    timings_path = ctx / "knowledge-graph-ce-rule-timings.txt"
    zero_hits_path = ctx / "knowledge-graph-zero-hit-rules.txt"
    server = None
    if rules:
        try:
            server = QueryServerClient().ensure_query_server(workspace)
            attach_query_server(server)
            print(
                f"query-server daemon pid={server.pid} port={server.port}",
                file=log,
                flush=True,
            )
        except Exception as error:
            print(
                f"query-server daemon did not start ({error}); using database run-queries",
                file=log,
                flush=True,
            )
            server = None
    try:
        codeql = CodeQL(workspace)
        codeql.populate(graph, populate=populate)
        _load_story_queries(graph, workspace, log)
        if rules:
            slugs = _slugs_for(graph, selected)
            graph.evaluate_rules(slugs)
        if as_json:
            print(
                f"loaded {len(graph.nodes)} nodes, {len(graph.relationships)} edges",
                file=log,
                flush=True,
            )
            payload = explorer_dto(graph, workspace)
            export_path = ctx / "explorer-graph.json"
            export_path.write_text(json.dumps(payload), encoding="utf-8")
            print(f"wrote {export_path}", file=log, flush=True)
            print(json.dumps(payload), flush=True)
            return
        if not rules:
            print(
                f"loaded {len(graph.nodes)} nodes, {len(graph.relationships)} edges",
                file=log,
                flush=True,
            )
            payload = explorer_dto(graph, workspace)
            export_path = ctx / "explorer-graph.json"
            export_path.write_text(json.dumps(payload), encoding="utf-8")
            print(f"wrote {export_path}", file=log, flush=True)
            return
        print(
            f"full run: {len(slugs.names)} graph rules "
            f"({', '.join(selected)})",
            file=log,
            flush=True,
        )
        zeros = graph.zero_hit_slugs()
        zeros.write(zero_hits_path)
        print(
            f"stored {len(zeros.names)} zero-hit rules in {zero_hits_path}",
            file=log,
            flush=True,
        )
        print(
            f"loaded {len(graph.nodes)} nodes, {len(graph.relationships)} edges",
            file=log,
            flush=True,
        )
        timings = sorted(graph.rule_timings, key=lambda item: item.seconds, reverse=True)
        lines = [
            f"{item.seconds:7.2f}s  hits={item.hits:4d}  {item.slug}"
            + (
                f"  {item.error}"
                if item.error == "skipped"
                else f"  ERROR {item.error}"
                if item.error
                else ""
            )
            for item in timings
        ]
        total = sum(item.seconds for item in timings)
        body = "\n".join(lines) + f"\n\n{len(timings)} rules, {total:.2f}s total\n"
        timings_path.write_text(body, encoding="utf-8")
        print(body, file=log, flush=True)
        print(f"wrote {timings_path}", file=log, flush=True)
        export_path = ctx / "explorer-graph.json"
        payload = explorer_dto(graph, workspace)
        export_path.write_text(json.dumps(payload), encoding="utf-8")
        print(f"wrote {export_path}", file=log, flush=True)
        text = _render_kg(graph, graphs=graphs, violations_only=violations_only)
        hierarchy_path.write_text(text, encoding="utf-8")
        print(
            f"wrote {hierarchy_path} ({len(text)} chars, {text.count(chr(10))} lines)",
            file=log,
            flush=True,
        )
        failures = list(graph.partial_failures)
        print(f"partial failures: {len(failures)}", file=log, flush=True)
        for item in failures:
            print(f"  {item}", file=log, flush=True)
    finally:
        if server is not None:
            detach_query_server(server)


def _load_practice_trees(graph: PracticeGraph, workspace: Path, log) -> None:
    """Load stories, DDD, and BDD trees. CodeQL fact queries only build the code index."""
    from harness.knowledge_graph.model.loader import GraphLoader
    from practices.stories.model.story_model import StoryModel as DiskStoryModel

    loader = GraphLoader.from_graph(graph)
    try:
        _load_ce_folders(graph, workspace)
        print(
            f"clean engineering folders: {sum(1 for node in graph.nodes.values() if node.semantic_type() == 'Module')}",
            file=log,
            flush=True,
        )
    except Exception as error:
        print(f"clean engineering folders did not load ({error})", file=log, flush=True)
    try:
        loader._load_bdd_descriptions()
    except Exception as error:
        print(f"bdd tree did not load ({error})", file=log, flush=True)
    try:
        loader._load_ddd_structure_from_map()
        print(
            f"ddd contexts: {sum(1 for node in graph.nodes.values() if node.semantic_type() == 'BoundedContext')}",
            file=log,
            flush=True,
        )
    except Exception as error:
        print(f"ddd tree did not load ({error})", file=log, flush=True)
    try:
        loader.graph.story_map = loader._load_story_map(DiskStoryModel.load(workspace))
        loader._index_story_epics()
        print(
            f"stories map: {len(loader.graph.story_map.epics)} epics",
            file=log,
            flush=True,
        )
    except Exception as error:
        print(f"stories map did not load ({error})", file=log, flush=True)
    if loader.graph.story_map and loader.graph.story_map.epics:
        return


def _load_story_queries(graph: PracticeGraph, workspace: Path, log) -> None:
    """Story queries run after the class index exists, so invokes and observes can bind."""
    if graph.story_map and graph.story_map.epics:
        return
    from practices.stories.model.codeql.codeql_model import StoryModel

    try:
        StoryModel().load_on(graph, workspace)
        print(
            f"stories tree: {sum(1 for node in graph.nodes.values() if node.semantic_type() == 'Story')} stories, "
            f"{sum(1 for edge in graph.relationships if getattr(edge, 'kind', None) == 'invokes')} invokes",
            file=log,
            flush=True,
        )
    except Exception as error:
        print(f"stories tree did not load ({error})", file=log, flush=True)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rules",
        dest="rules",
        action="store_true",
        help="Evaluate graph rules against the CodeQL database and write them into the JSON graph.",
    )
    parser.add_argument(
        "--no-populate",
        dest="populate",
        action="store_false",
        help="decode existing fact BQRS; skip the populate queries",
    )
    parser.add_argument(
        "--graph",
        dest="graphs",
        action="append",
        metavar="NAME",
        help="Practice graph (module) to include; repeatable. Default: all.",
    )
    parser.add_argument(
        "--violations-only",
        dest="violations_only",
        action="store_true",
        help="Print only nodes with violations and their ancestors.",
    )
    parser.add_argument(
        "--practice",
        dest="practices",
        action="append",
        metavar="NAME",
        help="Practice to evaluate; repeatable. Default: clean_engineering, bdd, stories, ddd.",
    )
    parser.add_argument(
        "--ddd",
        dest="ddd",
        action="store_true",
        help="Also evaluate DDD graph rules. Default already includes DDD.",
    )
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Print the explorer KnowledgeGraph JSON on stdout.",
    )
    parser.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=_REPO,
        help="Workspace to load. Default: repository root.",
    )
    parser.set_defaults(
        populate=True,
        graphs=None,
        violations_only=False,
        ddd=False,
        as_json=False,
        practices=None,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    main(
        populate=args.populate,
        graphs=args.graphs,
        violations_only=args.violations_only,
        root=args.root,
        ddd=args.ddd,
        as_json=args.as_json,
        practices=tuple(args.practices) if args.practices else None,
        rules=args.rules,
    )
