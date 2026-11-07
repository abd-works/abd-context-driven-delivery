"""Read the violations a checked graph holds: a saved graph (``.context/graph.json``), or the nodes
``graph.return_nodes`` answered with. Every violation is the graph's own Violation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from harness.graph.violation import Violation
from harness.installation.destination import data_of


def load_graph_json_paths(graph: bool | str | list[str] | None) -> list[Path]:
    if not graph or graph is True:
        return []
    if isinstance(graph, str):
        text = graph.strip()
        return [Path(text)] if text else []
    return [Path(item) for item in graph if str(item).strip()]


def violations_from_graph_json_file(path: Path, practices: list[str] | None = None) -> list[Violation]:
    """The violations in a saved graph document or in a ``graph.return_nodes`` node list; with practices, only those
    found by those practices."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("practices"), dict):
        return _violations_from_saved_graph(raw["practices"], practices)
    if not isinstance(raw, list):
        raise ValueError(f"graph JSON must be a list of nodes or a saved graph document: {path}")
    return [violation for node in raw if not practices or node.get("practice") in practices for violation in _violations_from_node(node)]


def violations_from_graph_json_files(paths: list[Path], practices: list[str] | None = None) -> list[Violation]:
    return [violation for path in paths for violation in violations_from_graph_json_file(path, practices)]


def save_checked_graph(paths: list[Path], destination: Path) -> None:
    """Keep the graph a validation checked at destination. Several graphs merge into one node list holding each one's
    violations."""
    if not paths:
        return
    if len(paths) == 1:
        destination.write_bytes(paths[0].read_bytes())
        return
    nodes = [_violating_node(violation) for violation in violations_from_graph_json_files(paths)]
    destination.write_text(json.dumps(nodes), encoding="utf-8")


def _violating_node(violation: Violation) -> dict[str, Any]:
    """One violation as the node it was found on, in the shape ``graph.return_nodes`` answers with."""
    rule = {"name": violation.rule, "status": "violating", "violations": [data_of(violation)]}
    return {"practice": violation.practice, "node_id": violation.node_id, "rules": [rule]}


def _violations_from_saved_graph(documents: dict[str, Any], practices: list[str] | None) -> list[Violation]:
    """A saved practice keeps its node rows and its violations; a violation saved before it kept its own place sits at
    its node's."""
    violations: list[Violation] = []
    for name, document in documents.items():
        if practices and name not in practices:
            continue
        rows = {row[0]: row for row in (document or {}).get("nodes") or [] if row}
        violations.extend(Violation.from_saved(name, saved, rows) for saved in (document or {}).get("rules") or [])
    return violations


def _violations_from_node(node: dict[str, Any]) -> list[Violation]:
    """The violations of each violating rule on one node ``graph.return_nodes`` answered with."""
    found: list[Violation] = []
    for rule in node.get("rules") or []:
        if rule.get("status") == "violating":
            found.extend(Violation.from_data({"practice": node.get("practice", ""), **hit}) for hit in rule.get("violations") or [])
    return found


def filter_violations_by_path_prefix(violations: list[Violation], prefixes: list[str] | None) -> list[Violation]:
    """The violations in files under one of the path prefixes; every violation when there are none."""
    if not prefixes or not any(str(prefix).strip() for prefix in prefixes):
        return violations
    return [violation for violation in violations if violation.is_under(prefixes)]


def violations_by_rule(violations: list[Violation]) -> dict[str, list[Violation]]:
    grouped: dict[str, list[Violation]] = {}
    for violation in violations:
        grouped.setdefault(violation.rule or "unknown", []).append(violation)
    return grouped
