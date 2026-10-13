"""Run PracticeGraphRule checks the way historical scanners used eval fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path

from harness.graph.graph import PracticeGraph
from harness.graph.rule_context import RuleCheckContext
from harness.graph.working_copy import _class_fact
from practices.clean_engineering.model.javascript.javascript_class_model import (
    JavaScriptCleanEngineeringModel,
)
from practices.clean_engineering.model.python.python_class_model import PythonCleanEngineeringModel
from practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
)

_LANG = {
    "python": (".py", PythonCleanEngineeringModel),
    "typescript": (".ts", TypeScriptCleanEngineeringModel),
    "javascript": (".js", JavaScriptCleanEngineeringModel),
}


def ce_rule_by_slug(slug: str):
    from practices.clean_engineering.model.python.rules import BY_SLUG as code
    from practices.clean_engineering.rules import BY_SLUG as graph

    rule = code.get(slug) or graph.get(slug)
    if rule is None:
        raise KeyError(slug)
    return rule


def practice_from_source(source: str, *, lang: str = "python", filename: str | None = None) -> tuple[PracticeGraph, Path]:
    suffix, parser = _LANG[lang]
    name = filename or f"example{suffix}"
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    # Keep temp dir alive on practice object for caller lifetime.
    practice = PracticeGraph("clean_engineering")
    practice.source_root = str(root)
    practice._temp_dir = temp  # type: ignore[attr-defined]
    relative = name
    text = source.strip() + "\n"
    (root / relative).write_text(text, encoding="utf-8")
    model = parser().parse(text)
    nodes: list = []
    edges: list = []
    module_id = practice.root_node.node_id
    class_names = {cls.name for module in model.modules for cls in module.classes}
    for module in model.modules:
        for cls in module.classes:
            _class_fact(practice, text, relative, module_id, cls, class_names, nodes, edges)
    practice.apply_nodes(nodes)
    practice.apply_edges(edges)
    return practice, root


def violations_for_rule(rule, practice: PracticeGraph, root: Path) -> list[str]:
    context = RuleCheckContext(practice, root)
    messages: list[str] = []
    for _node_id, message in rule.check_practice(context):
        messages.append(message)
    for node_type in rule.node_types:
        for node in practice.nodes.get(node_type, []):
            messages.extend(rule.check(node, context))
    return messages


def assert_rule_pair(slug: str, fault_source: str, clean_source: str, *, lang: str = "python") -> None:
    rule = ce_rule_by_slug(slug)
    fault_practice, fault_root = practice_from_source(fault_source, lang=lang)
    clean_practice, clean_root = practice_from_source(clean_source, lang=lang)
    fault_hits = violations_for_rule(rule, fault_practice, fault_root)
    clean_hits = violations_for_rule(rule, clean_practice, clean_root)
    if not fault_hits:
        raise AssertionError(f"{slug}: expected violations on fault fixture, got none")
    if clean_hits:
        raise AssertionError(f"{slug}: expected no violations on clean fixture, got {clean_hits!r}")


def example_asset_paths(slug: str, *, channel: str = "python") -> tuple[Path, Path]:
    root = (
        Path(__file__).resolve().parents[2]
        / "practices/clean_engineering/model"
        / channel
        / ".examples"
        / slug
    )
    faulty = root / "faulty" / "faultyAsset.py"
    repaired = root / "repaired" / "repairedAsset.py"
    if channel != "python":
        faulty = root / "faulty" / f"faultyAsset{ _LANG[channel][0] }"
        repaired = root / "repaired" / f"repairedAsset{ _LANG[channel][0] }"
    return faulty, repaired


def assert_python_example_pair(slug: str) -> None:
    faulty_path, repaired_path = example_asset_paths(slug)
    assert_rule_pair(
        slug,
        faulty_path.read_text(encoding="utf-8"),
        repaired_path.read_text(encoding="utf-8"),
        lang="python",
    )
