"""Load a PracticeGraph and write the practice hierarchy report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
import mcp.types  # SDK, before harness/mcp is on PYTHONPATH
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from harness.knowledge_graph.model import PracticeGraph, RuleSlugs
from harness.knowledge_graph.model.codeql import CodeQL
from harness.knowledge_graph.model.dot_graph import (
    _hierarchy_line,
    _hierarchy_violations,
    graph_name_matches,
    prune_to_violations,
    walk_hierarchy,
)
from practices.clean_engineering.model.codeql.codeql_model import Module

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


def main(
    populate: bool = True,
    graphs: list[str] | None = None,
    violations_only: bool = False,
    root: Path | None = None,
) -> None:
    workspace = Path(root) if root is not None else _REPO
    names = ",".join(graphs) if graphs else "all"
    print(
        f"loading {workspace} populate={populate} graphs={names} "
        f"violations_only={violations_only}",
        flush=True,
    )
    graph = PracticeGraph(workspace)
    ctx = graph.working_context()
    hierarchy_path = ctx / "knowledge-graph-ce-hierarchy.txt"
    timings_path = ctx / "knowledge-graph-ce-rule-timings.txt"
    zero_hits_path = ctx / "knowledge-graph-zero-hit-rules.txt"
    CodeQL(workspace).populate(graph, populate=populate)
    ce_slugs = RuleSlugs(
        [
            rule.slug
            for rule in graph.rule_registry
            if rule.practice == "clean_engineering" and rule.graph_evaluated
        ]
    )
    skip = RuleSlugs()
    print("full run: no skipped rules", flush=True)
    graph.evaluate_rules(ce_slugs)
    zeros = graph.zero_hit_slugs()
    zeros.write(zero_hits_path)
    print(f"stored {len(zeros.names)} zero-hit rules in {zero_hits_path}", flush=True)
    print(
        f"loaded {len(graph.nodes)} nodes, {len(graph.relationships)} edges",
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
    print(body, flush=True)
    print(f"wrote {timings_path}", flush=True)
    text = _render_kg(graph, graphs=graphs, violations_only=violations_only)
    hierarchy_path.write_text(text, encoding="utf-8")
    print(f"wrote {hierarchy_path} ({len(text)} chars, {text.count(chr(10))} lines)", flush=True)
    failures = list(graph.partial_failures)
    print(f"partial failures: {len(failures)}", flush=True)
    for item in failures:
        print(f"  {item}", flush=True)


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
        "root",
        nargs="?",
        type=Path,
        default=_REPO,
        help="Workspace to load. Default: repository root.",
    )
    parser.set_defaults(populate=True, graphs=None, violations_only=False)
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    main(
        populate=args.populate,
        graphs=args.graphs,
        violations_only=args.violations_only,
        root=args.root,
    )
