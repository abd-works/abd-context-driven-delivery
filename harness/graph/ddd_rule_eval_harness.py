"""Evaluate DDD tactical rules against python/_examples fixtures.

The fixture goes through the clean engineering working-copy build; the DDD building block
for the chosen kind then loads its own tactical facts, exactly as ``_record_ddd`` does.
"""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.ce_rule_eval_harness import practice_from_source
from harness.graph.rule_context import RuleCheckContext
from cdd_guidance.practices.ddd.model.stereotypes import class_declaration_decorated_name, inferred_tactical_kind


def ddd_rule_by_slug(slug: str):
    from cdd_guidance.practices.ddd.rules import BY_SLUG

    rule = BY_SLUG.get(slug)
    if rule is None:
        raise KeyError(slug)
    return rule


def _node_type_for_class(source: str, class_name: str) -> str:
    names = set(re.findall(r"^class\s+(\w+)", source, re.MULTILINE))
    kind = inferred_tactical_kind(class_declaration_decorated_name(source, class_name), names)
    if kind is None and class_name.endswith("Repository"):
        return "Repository"
    if kind is None and class_name.endswith("Service"):
        return "DomainService"
    return kind or "Entity"


def _ddd_node(source: str, class_name: str, kind: str, lang: str, filename: str | None):
    from harness.graph.working_copy import _fact_row, _parsed_module, _tactical_facts

    clean, root = practice_from_source(source, lang=lang, filename=filename)
    class_node = next((node for node in clean.nodes.get("OoadClass", []) if node.name == class_name), None)
    if class_node is None:
        raise ValueError(f"class {class_name!r} not found in parsed source")
    module, text = _parsed_module(root / class_node.source.file, root)
    parsed = next(oclass for oclass in module.classes if oclass.name == class_name)
    member = {"kind": kind, "name": class_name, "model": parsed, "text": text}
    node_id = f"ddd:{kind}:{class_node.source.file}:{class_name}"
    row = [node_id, class_name, kind, "ddd", class_node.source.file, class_node.source.start_line, class_node.source.end_line]
    ddd = clean.graph.practice("ddd")
    ddd.apply_nodes([_fact_row(row, {**class_node.data, **_tactical_facts(member)})])
    return ddd.by_id[node_id], ddd, root


def violations_for_ddd_rule(
    rule,
    source: str,
    *,
    class_name: str,
    node_type: str | None = None,
    lang: str = "python",
    filename: str | None = None,
) -> list[str]:
    kind = node_type or _node_type_for_class(source, class_name)
    node, practice, root = _ddd_node(source, class_name, kind, lang, filename)
    return list(rule.check(node, RuleCheckContext(practice, root)))


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
        raise AssertionError(f"{slug}/{fault_class}: expected violations on fault fixture, got none")
    if clean_hits:
        raise AssertionError(f"{slug}/{fault_class}: expected clean fixture, got {clean_hits!r}")
