"""Read graph_return_nodes JSON into validation violation records."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_graph_json_paths(graph: bool | str | list[str] | None) -> list[Path]:
    if not graph:
        return []
    if graph is True:
        return []
    if isinstance(graph, str):
        text = graph.strip()
        return [Path(text)] if text else []
    return [Path(item) for item in graph if str(item).strip()]


def violations_from_graph_json_file(path: Path, practices: list[str] | None = None) -> list[dict[str, Any]]:
    """Violations in graph_return_nodes JSON (a node list) or a saved graph document (``.context/graph.json``).

    With ``practices``, only nodes of those graph practices count.
    """
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and isinstance(raw.get("practices"), dict):
        return _violations_from_saved_graph(raw["practices"], practices)
    if not isinstance(raw, list):
        raise ValueError(f"graph JSON must be a list of nodes or a saved graph document: {path}")
    violations: list[dict[str, Any]] = []
    for node in raw:
        if practices and node.get("practice") and node.get("practice") not in practices:
            continue
        violations.extend(_violations_from_node(node))
    return violations


def violations_from_graph_json_files(
    paths: list[Path], practices: list[str] | None = None
) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for path in paths:
        merged.extend(violations_from_graph_json_file(path, practices))
    return merged


def _violations_from_saved_graph(
    documents: dict[str, Any], practices: list[str] | None
) -> list[dict[str, Any]]:
    """A saved practice keeps node rows ``[id, name, type, practice, file, start, end, ...]`` and
    rule hits ``[slug, node_id, message]``; each hit sits at its node's source."""
    violations: list[dict[str, Any]] = []
    for name, document in documents.items():
        if practices and name not in practices:
            continue
        rows = {row[0]: row for row in (document or {}).get("nodes") or [] if row}
        for slug, node_id, message in (document or {}).get("rules") or []:
            row = rows.get(node_id) or [node_id, "", "", name, "", None, None]
            node = {"practice": name, "type": row[2], "name": row[1]}
            hit = {"message": str(message), "file": row[4], "start": row[5], "end": row[6]}
            violations.append(_record(node, row[2], row[1], str(slug), hit))
    return violations


def refresh_stale_limit_operation_parameter_messages(
    violations: list[dict[str, Any]],
    workspace_directory: Path,
) -> list[dict[str, Any]]:
    """Re-run limit-operation-parameters when graph JSON still has the legacy message."""
    if not any(_needs_limit_parameter_refresh(item) for item in violations):
        return violations
    from harness.graph.ce_rule_eval_harness import ce_rule_by_slug, practice_from_source
    from harness.graph.rule_context import RuleCheckContext

    rule = ce_rule_by_slug("limit-operation-parameters")
    workspace = workspace_directory.resolve()
    by_file: dict[str, list[dict[str, Any]]] = {}
    for item in violations:
        if not _needs_limit_parameter_refresh(item):
            continue
        location = str(item.get("location", "")).replace("\\", "/")
        if location:
            by_file.setdefault(location, []).append(item)

    refreshed: dict[tuple[str, str], str] = {}
    for rel_path, _items in by_file.items():
        source_path = workspace / rel_path
        if not source_path.is_file():
            continue
        lang = _source_language(source_path)
        if lang is None:
            continue
        practice, root = practice_from_source(
            source_path.read_text(encoding="utf-8"),
            lang=lang,
            filename=source_path.name,
        )
        context = RuleCheckContext(practice, root)
        for node in practice.nodes.get("Operation", []):
            hits = rule.check(node, context)
            if hits:
                refreshed[(rel_path, node.name)] = hits[0]

    if not refreshed:
        return violations

    updated: list[dict[str, Any]] = []
    for item in violations:
        if not _needs_limit_parameter_refresh(item):
            updated.append(item)
            continue
        rel_path = str(item.get("location", "")).replace("\\", "/")
        op_name = str(item.get("node_name", ""))
        message = refreshed.get((rel_path, op_name))
        if not message:
            updated.append(item)
            continue
        ntype = str(item.get("node_type", "Operation"))
        nname = str(item.get("node_name", ""))
        prefix = f"{ntype} `{nname}`: " if nname else ""
        updated.append({**item, "violation_message": f"{prefix}{message}".strip()})
    return updated


def _needs_limit_parameter_refresh(item: dict[str, Any]) -> bool:
    if item.get("rule_slug") != "limit-operation-parameters":
        return False
    text = str(item.get("violation_message", ""))
    return "takes more than two parameters" in text or "(maximum 2)" in text


def _source_language(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in {".ts", ".tsx"}:
        return "typescript"
    if suffix == ".js":
        return "javascript"
    if suffix == ".py":
        return "python"
    return None


def _violations_from_node(node: dict[str, Any]) -> list[dict[str, Any]]:
    if "violations" in node and isinstance(node.get("violations"), list):
        return _from_summary_node(node)
    return _from_full_node(node)


def _from_summary_node(node: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ntype = node.get("type", "")
    nname = node.get("name", "")
    for block in node.get("violations") or []:
        rule = str(block.get("rule", ""))
        for hit in block.get("messages") or []:
            out.append(_record(node, ntype, nname, rule, hit))
    return out


def _from_full_node(node: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    ntype = node.get("type", "")
    nname = node.get("name", "")
    for rule in node.get("rules") or []:
        if rule.get("status") != "violating":
            continue
        rule_name = str(rule.get("name", ""))
        for hit in rule.get("violations") or []:
            out.append(_record(node, ntype, nname, rule_name, hit))
    return out


def _record(
    node: dict[str, Any],
    ntype: str,
    nname: str,
    rule: str,
    hit: dict[str, Any] | str,
) -> dict[str, Any]:
    if isinstance(hit, str):
        message = hit
        file = ""
        start = None
        end = None
    else:
        message = str(hit.get("message", ""))
        file = str(hit.get("file", "") or "")
        start = hit.get("start")
        end = hit.get("end")
    line_number = int(start) if start else None
    location = file or "unknown"
    prefix = f"{ntype} `{nname}`: " if nname else ""
    return {
        "location": location,
        "line_number": line_number,
        "violation_message": f"{prefix}{message}".strip(),
        "severity": "error",
        "graph_rule": True,
        "rule_slug": rule,
        "practice": node.get("practice", ""),
        "node_type": ntype,
        "node_name": nname,
        "end_line": int(end) if end else line_number,
    }


def filter_violations_by_path_prefix(
    violations: list[dict[str, Any]],
    prefixes: list[str] | None,
) -> list[dict[str, Any]]:
    if not prefixes:
        return violations
    normalized = [p.replace("\\", "/").strip("/") for p in prefixes if str(p).strip()]
    if not normalized:
        return violations
    kept: list[dict[str, Any]] = []
    for item in violations:
        loc = str(item.get("location", "")).replace("\\", "/")
        if any(loc == prefix or loc.startswith(f"{prefix}/") for prefix in normalized):
            kept.append(item)
    return kept


def violations_by_rule(violations: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in violations:
        key = str(item.get("rule_slug") or "unknown")
        grouped.setdefault(key, []).append(item)
    return grouped
