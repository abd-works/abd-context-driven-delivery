"""Spec support: evaluate DDD tactical rules against python/_examples fixtures.

The fixture goes through the clean engineering working-copy build; the DDD building block
for the chosen kind then loads its own tactical facts, exactly as the DDD practice's graph reader does.
"""

from __future__ import annotations

from pathlib import Path

from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_source
from harness.graph.rule_context import RuleCheckContext
from cdd_guidance.practices.ddd.model.stereotypes import decorated_name, inferred_tactical_kind


def ddd_rule_by_slug(slug: str):
    from cdd_guidance.practices.ddd.rules import BY_SLUG

    rule = BY_SLUG.get(slug)
    if rule is None:
        raise KeyError(slug)
    return rule


def _node_type_for_class(clean, class_node) -> str:
    """The building block the DDD practice's graph reader names the class: its stereotypes first, then its name."""
    names = {node.name for node in clean.nodes.get("OoadClass", [])}
    kind = inferred_tactical_kind(decorated_name(class_node.name, class_node.get_fact("stereotypes") or []), names)
    if kind is None and class_node.name.endswith("Repository"):
        return "Repository"
    if kind is None and class_node.name.endswith("Service"):
        return "DomainService"
    return kind or "Entity"


def _ddd_node(source: str, class_name: str, kind: str | None, lang: str, filename: str | None):
    from cdd_guidance.practices.ddd.graph_practice import _tactical_block

    clean, root = practice_from_source(source, lang=lang, filename=filename)
    class_node = next((node for node in clean.nodes.get("OoadClass", []) if node.name == class_name), None)
    if class_node is None:
        raise ValueError(f"class {class_name!r} not found in parsed source")
    kind = kind or _node_type_for_class(clean, class_node)
    source = class_node.source
    ddd = clean.graph.practice("ddd")
    node = ddd.add(_tactical_block(class_node, kind), f"ddd:{kind}:{source.file}:{class_name}", source.file, source.start_line, source.end_line)
    node.set_fact("folder", class_node.get_fact("folder"))
    return node, ddd, root


def violations_for_ddd_rule(
    rule,
    source: str,
    *,
    class_name: str,
    node_type: str | None = None,
    lang: str = "python",
    filename: str | None = None,
) -> list[str]:
    node, practice, root = _ddd_node(source, class_name, node_type, lang, filename)
    return list(rule.check(node, RuleCheckContext(practice, root)))


def assert_ddd_example_pair(
    slug: str,
    fault_class: str,
    *,
    clean_class: str | None = None,
    node_type: str | None = None,
    clean_node_type: str | None = None,
) -> None:
    root = Path(__file__).resolve().parents[1] / "model" / "python" / "_examples" / slug
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
