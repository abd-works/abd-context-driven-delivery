"""Run practice graph rules from ``practices/<practice>/rules/`` and record violations on each node's rules collection."""

from __future__ import annotations

from pathlib import Path

from harness.graph.node_rules import attach_node_rules
from harness.graph.practice_rules_registry import checks_for_practice
from harness.graph.schema_rules import bind_practice_rules


def attach_rules(practice) -> None:
    """Run executable checks for this practice and attach violations to each node."""
    bind_practice_rules(practice)
    checks = checks_for_practice(practice.name)
    if not checks:
        return
    root = Path(practice.source_root) if practice.source_root else None
    files: dict[str, str] = {}
    for check in checks.values():
        rows: list[list[str]] = []
        for node_type in check.node_types:
            for node in practice.nodes.get(node_type, []):
                if not hasattr(node, "_rules") or node._rules is None:
                    attach_node_rules(node)
                text = _file_text(root, node, files)
                for message in check.check(node, text):
                    node._rules.record_violation(check.slug, message)
                    rows.append([check.slug, node.node_id, message])
        if rows:
            practice.apply_rules(check.slug, rows)


def _file_text(root: Path | None, node, files: dict[str, str]) -> str:
    if root is None or not node.source.file:
        return ""
    relative = node.source.file
    if relative not in files:
        path = root / relative
        files[relative] = path.read_text(encoding="utf-8") if path.is_file() else ""
    return files[relative]
