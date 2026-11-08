"""Spec support: run DDD tactical rules on example sources the way validate runs them.

The example is read by Clean Engineering and the DDD practice that extends it, as a live load reads a working copy, so
the graph's own reading names each building block's kind: from the stereotype the class carries, else the naming
convention its name follows. Each rule then runs through the practice's schema, so a rule the schema never applies to a
node type finds nothing there and its example fails.
"""

from __future__ import annotations

from pathlib import Path

from harness.graph.rule_fixture import RuleFixture, SchemaRuleRun

from cdd_guidance.practices.clean_engineering.rules.rule_examples import FIXTURE_FOLDER, source_suffix
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ddd.rules import BY_SLUG

_EXAMPLES = Path(__file__).resolve().parents[1] / "model" / "python" / "_examples"


def ddd_rule_by_slug(slug: str):
    return BY_SLUG[slug]


def ddd_fixture(files: dict[str, str]) -> RuleFixture:
    """The files, each named from the fixture's one folder, read by Clean Engineering and DDD."""
    return RuleFixture(Ddd, {f"{FIXTURE_FOLDER}/{name}": text.strip() + "\n" for name, text in files.items()})


def violations_for_ddd_rule(
    rule,
    source: str,
    *,
    class_name: str | None = None,
    lang: str = "python",
    filename: str | None = None,
    beside: dict[str, str] | None = None,
) -> list[str]:
    """What the rule reports on the DDD node named class_name, or on every DDD node when none is named, with the source
    read from filename and the files beside it in the same folder."""
    files = {filename or f"example{source_suffix(lang)}": source, **(beside or {})}
    fixture = ddd_fixture(files)
    run = SchemaRuleRun(rule, fixture.context)
    if class_name is None:
        return run.hits()
    nodes = [node for node in fixture.context.nodes() if node.name == class_name]
    if not nodes:
        raise ValueError(f"the graph names no building block for {class_name!r}: give the class a stereotype or a name its kind's convention allows")
    return [hit for node in nodes for hit in run.node_hits(node)]


def assert_ddd_example_pair(slug: str, fault_class: str | None = None, *, clean_class: str | None = None) -> None:
    """The rule flags the example's faulty asset and passes its repaired one: on the classes named, else anywhere."""
    root = _EXAMPLES / slug
    rule = ddd_rule_by_slug(slug)
    fault_hits = violations_for_ddd_rule(rule, (root / "faulty" / "faultyAsset.py").read_text(encoding="utf-8"), class_name=fault_class)
    clean_hits = violations_for_ddd_rule(rule, (root / "repaired" / "repairedAsset.py").read_text(encoding="utf-8"), class_name=clean_class or fault_class)
    if not fault_hits:
        raise AssertionError(f"{slug}/{fault_class}: expected violations on fault fixture, got none")
    if clean_hits:
        raise AssertionError(f"{slug}/{fault_class}: expected clean fixture, got {clean_hits!r}")
