"""Load a PracticeGraph and write the practice hierarchy report."""

from __future__ import annotations

import argparse
import json
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

from harness.knowledge_graph.model import PracticeGraph, RuleSlugs
from harness.knowledge_graph.model.codeql import (
    CodeQL,
    attach_query_server,
    detach_query_server,
)
from harness.knowledge_graph.model.graph_rules import closest_fidelity
from harness.mcp.codeql_query_daemon import ensure_query_server
from harness.knowledge_graph.model.dot_graph import (
    _hierarchy_line,
    _hierarchy_violations,
    graph_name_matches,
    prune_to_violations,
    walk_hierarchy,
)
from practices.clean_engineering.model.codeql.codeql_model import Module

_DEFAULT_PRACTICES = ("clean_engineering", "bdd", "stories")


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


def _source_dto(node, folder: Path) -> dict | None:
    src = getattr(node, "source", None)
    file = str(getattr(src, "file", "") or "").replace("\\", "/")
    if not file:
        return None
    start = int(getattr(src, "line", 0) or 0)
    end = int(getattr(src, "end_line", 0) or start)
    text = str(getattr(src, "text", "") or "")
    from practices.clean_engineering.model.codeql.codeql_model import read_source_span

    if start > 0:
        sliced_start, sliced_end, sliced = read_source_span(folder, file, start, end)
        if sliced:
            start, end, text = sliced_start, sliced_end, sliced
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
    rule_slugs: dict[tuple[str, str], list[str]] = {}
    for node in graph.nodes.values():
        practice = getattr(node, "practice", "") or "node"
        practices[node.node_id] = practice
        semantic = node.semantic_type()
        key = (practice, semantic)
        if key not in rule_slugs:
            rule_slugs[key] = [
                rule.slug
                for rule in graph.rule_registry.rules_for_node(
                    practice=practice,
                    semantic_type=semantic,
                )
            ]
        hits = graph.violations_for(node)
        grouped[practice]["nodes"].append(
            {
                "node_id": node.node_id,
                "name": (getattr(node, "name", None) or semantic or node.node_id),
                "practice": practice,
                "fidelity": closest_fidelity(practice, semantic),
                "semantic_type": semantic,
                "properties": {},
                "applicable_rules": rule_slugs[key],
                "violations": [
                    {
                        "rule_slug": hit.rule_slug,
                        "message": hit.message,
                        "practice": hit.practice,
                        "fidelity": hit.fidelity,
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
    ctx = graph.working_context()
    hierarchy_path = ctx / "knowledge-graph-ce-hierarchy.txt"
    timings_path = ctx / "knowledge-graph-ce-rule-timings.txt"
    zero_hits_path = ctx / "knowledge-graph-zero-hit-rules.txt"
    server = None
    try:
        server = ensure_query_server(workspace)
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
        CodeQL(workspace).populate(graph, populate=populate)
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


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
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
        help="Practice to evaluate; repeatable. Default: clean_engineering, bdd, stories.",
    )
    parser.add_argument(
        "--ddd",
        dest="ddd",
        action="store_true",
        help="Also evaluate DDD graph rules. Default: Clean Engineering, BDD, Stories.",
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
    )
