"""Rule slugs declared on each type in practice/model/schema.yaml."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from harness.graph.schema_edges import _SEMANTIC

_ROOT = Path(__file__).resolve().parents[2]
_PRACTICES = ("stories", "clean_engineering", "ddd", "bdd", "ux")


def semantic_type(schema_key: str) -> str:
    if schema_key in _SEMANTIC:
        return _SEMANTIC[schema_key]
    return schema_key[:1].upper() + schema_key[1:]


@lru_cache(maxsize=None)
def rules_for_practice(practice: str) -> dict[str, tuple[str, ...]]:
    """Map explorer node type → ordered rule slugs from that practice schema."""
    path = _ROOT / "practices" / practice / "model" / "schema.yaml"
    if not path.is_file():
        return {}
    found = _parse_rules(path.read_text(encoding="utf-8"))
    patterns = _ROOT / "patterns"
    if patterns.is_dir():
        for schema in sorted(patterns.glob(f"*/practices/{practice}/model/schema.yaml")):
            overlay = _parse_rules(schema.read_text(encoding="utf-8"))
            for node_type, slugs in overlay.items():
                merged = list(found.get(node_type, ()))
                for slug in slugs:
                    if slug not in merged:
                        merged.append(slug)
                found[node_type] = tuple(merged)
    return found


def slugs_for_type(practice: str, node_type: str) -> tuple[str, ...]:
    return rules_for_practice(practice).get(node_type, ())


def bind_practice_rules(practice_graph) -> None:
    """Register every schema rule slug against the node types it applies to."""
    for node_type, slugs in rules_for_practice(practice_graph.name).items():
        for slug in slugs:
            practice_graph.bind_rule(slug, [node_type])


def _parse_rules(text: str) -> dict[str, tuple[str, ...]]:
    by_type: dict[str, list[str]] = {}
    owner_key = ""
    in_rules = False
    for line in text.splitlines():
        header = re.match(r"^([A-Za-z]\w*):\s*$", line)
        if header:
            owner_key = header.group(1)
            in_rules = False
            continue
        if re.match(r"^  rules:\s*$", line) and owner_key:
            in_rules = True
            node_type = semantic_type(owner_key)
            by_type.setdefault(node_type, [])
            continue
        if in_rules:
            bullet = re.match(r"^\s+-\s+(\S+)\s*$", line)
            if bullet is None:
                if line.startswith("  ") and not line.startswith("    "):
                    in_rules = False
                continue
            node_type = semantic_type(owner_key)
            slugs = by_type.setdefault(node_type, [])
            slug = bullet.group(1).strip()
            if slug not in slugs:
                slugs.append(slug)
    return {node_type: tuple(slugs) for node_type, slugs in by_type.items()}
