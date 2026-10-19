"""Evaluate DDD tactical rules against python/_examples fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path

from harness.graph.ce_rule_eval_harness import practice_from_source
from harness.graph.rule_context import RuleCheckContext
from cdd_guidance.practices.ddd.model.stereotypes import inferred_tactical_kind
from cdd_guidance.practices.ddd.rules.tactical_helpers import stereotyped_declaration_name


def ddd_rule_by_slug(slug: str):
    from cdd_guidance.practices.ddd.rules import BY_SLUG

    rule = BY_SLUG.get(slug)
    if rule is None:
        raise KeyError(slug)
    return rule


def _node_type_for_class(source: str, class_name: str) -> str:
    names = set()
    import re

    for match in re.finditer(r"^class\s+(\w+)", source, re.MULTILINE):
        names.add(match.group(1))
    decorated = stereotyped_declaration_name(source, class_name)
    kind = inferred_tactical_kind(decorated, names)
    if kind is None and class_name.endswith("Repository"):
        return "Repository"
    if kind is None and class_name.endswith("Service"):
        return "DomainService"
    return kind or "Entity"


def violations_for_ddd_rule(
    rule,
    source: str,
    *,
    class_name: str,
    node_type: str | None = None,
) -> list[str]:
    practice, root = practice_from_source(source, lang="python")
    practice.name = "ddd"
    resolved_type = node_type or _node_type_for_class(source, class_name)
    node = None
    for candidate in practice.nodes.get("OoadClass", []):
        if candidate.name == class_name:
            node = candidate
            break
    if node is None:
        raise ValueError(f"class {class_name!r} not found in parsed source")
    node.type = resolved_type
    node.practice = practice
    context = RuleCheckContext(practice, root)
    return list(rule.check(node, context))


def assert_ddd_example_pair(
    slug: str,
    fault_class: str,
    *,
    clean_class: str | None = None,
    node_type: str | None = None,
    clean_node_type: str | None = None,
) -> None:
    root = (
        Path(__file__).resolve().parents[2]
        / "cdd_guidance/practices/ddd/model/python/_examples"
        / slug
    )
    faulty = (root / "faulty" / "faultyAsset.py").read_text(encoding="utf-8")
    repaired = (root / "repaired" / "repairedAsset.py").read_text(encoding="utf-8")
    rule = ddd_rule_by_slug(slug)
    fault_hits = violations_for_ddd_rule(rule, faulty, class_name=fault_class, node_type=node_type)
    clean_hits = violations_for_ddd_rule(
        rule,
        repaired,
        class_name=clean_class or fault_class,
        node_type=clean_node_type or node_type,
    )
    if not fault_hits:
        raise AssertionError(f"{slug}/{class_name}: expected violations on fault fixture, got none")
    if clean_hits:
        raise AssertionError(f"{slug}/{class_name}: expected clean fixture, got {clean_hits!r}")
