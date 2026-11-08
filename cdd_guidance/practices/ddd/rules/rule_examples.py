"""Spec support: evaluate DDD tactical rules against python/_examples fixtures.

The fixture goes through the clean engineering working-copy build; the DDD practice that extends that Clean Engineering
practice then sees the chosen class as the building block of the chosen kind, exactly as the DDD practice's graph
reading does.
"""

from __future__ import annotations

from pathlib import Path

from cdd_guidance.practices.clean_engineering.rules.rule_examples import practice_from_source
from cdd_guidance.practices.ddd.model.graph_reading import BuildingBlock
from cdd_guidance.practices.ddd.model.stereotypes import TacticalClass
from harness.graph.rule_context import RuleCheckContext


def ddd_rule_by_slug(slug: str):
    from cdd_guidance.practices.ddd.rules import BY_SLUG

    rule = BY_SLUG.get(slug)
    if rule is None:
        raise KeyError(slug)
    return rule


def _kind_of(tactical: TacticalClass, names: set[str]) -> str:
    """The building block the DDD practice's graph reading names the class: its stereotypes first, then its name."""
    kind = tactical.inferred_kind(names)
    if kind is None and tactical.name.endswith("Repository"):
        return "Repository"
    if kind is None and tactical.name.endswith("Service"):
        return "DomainService"
    return kind or "Entity"


def _ddd_node(source: str, class_name: str, kind: str | None, lang: str, filename: str | None):
    clean, root = practice_from_source(source, lang=lang, filename=filename)
    classes = clean.graph.nodes_of(clean, "OoadClass")
    class_node = next((node for node in classes if node.name == class_name), None)
    if class_node is None:
        raise ValueError(f"class {class_name!r} not found in parsed source")
    ddd = next(practice for practice in clean.graph.every_practice.values() if practice.extended is clean)
    tactical = TacticalClass(class_node)
    kind = kind or _kind_of(tactical, {node.name for node in classes})
    place = class_node.source
    node = clean.graph.add(ddd, BuildingBlock(ddd, tactical, kind), f"ddd:{kind}:{place.file}:{class_name}", place.file, place.start_line, place.end_line)
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
