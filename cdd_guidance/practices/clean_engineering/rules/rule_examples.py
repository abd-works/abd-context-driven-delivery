"""Spec support: run Clean Engineering graph rules against a real working-copy build of small fixture trees.

Fixtures go through the same path as a live load: language parser, model nodes loading
their own facts, each node holding its parsed object, rules reading ``node.get_fact``.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from harness.graph.graph import Graph
from harness.guidance.guidance import PracticeGuidance
from harness.graph.rule_context import RuleCheckContext

_SUFFIX = {"python": ".py", "typescript": ".ts", "javascript": ".js"}
FIXTURE_FOLDER = "example"
_PRACTICE = Path(__file__).resolve().parents[1]


def ce_rule_by_slug(slug: str):
    from cdd_guidance.practices.clean_engineering.rules import BY_SLUG

    rule = BY_SLUG.get(slug)
    if rule is None:
        raise KeyError(slug)
    return rule


def practice_from_files(files: dict[str, str]) -> tuple[PracticeGuidance, Path]:
    """Write files under a temp root and load the clean engineering working copy from it."""
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    graph = Graph()
    graph.load_working_copy(str(root), {"clean_engineering": str(root)}, force=True)
    practice = graph.practice("clean_engineering")
    practice._temp_dir = temp  # type: ignore[attr-defined]
    return practice, root


def practice_from_class_text(name: str, text: str, relative: str) -> tuple[PracticeGuidance, Path]:
    """One class node recorded from source the working copy does not scan (markdown model files)."""
    from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass

    oclass = OoadClass(name=name, sequential_order=1, line=1)
    oclass.end_line = text.count("\n") + 1
    oclass.take_lines(text.split("\n"))
    oclass.load_source_facts()
    practice, root = practice_from_files({relative: text})
    practice.in_graph.add(oclass, f"clean_engineering:OoadClass:{relative}:{name}", relative, 1, text.count("\n") + 1)
    return practice, root


def practice_from_source(source: str, *, lang: str = "python", filename: str | None = None) -> tuple[PracticeGuidance, Path]:
    name = filename or f"example{_SUFFIX[lang]}"
    return practice_from_files({f"{FIXTURE_FOLDER}/{name}": source.strip() + "\n"})


def violations_for_rule(rule, practice: PracticeGuidance, root: Path) -> list[str]:
    context = RuleCheckContext(practice, root)
    messages: list[str] = []
    for _node_id, message in rule.check_practice(context):
        messages.append(message)
    for node_type in rule.node_types:
        for node in context.nodes(node_type):
            messages.extend(rule.check(node, context))
    return messages


def _assert_pair(slug: str, fault_hits: list[str], clean_hits: list[str]) -> None:
    if not fault_hits:
        raise AssertionError(f"{slug}: expected violations on fault fixture, got none")
    if clean_hits:
        raise AssertionError(f"{slug}: expected no violations on clean fixture, got {clean_hits!r}")


def assert_rule_pair(slug: str, fault_source: str, clean_source: str, *, lang: str = "python") -> None:
    rule = ce_rule_by_slug(slug)
    fault_hits = violations_for_rule(rule, *practice_from_source(fault_source, lang=lang))
    clean_hits = violations_for_rule(rule, *practice_from_source(clean_source, lang=lang))
    _assert_pair(slug, fault_hits, clean_hits)


def assert_files_rule_pair(slug: str, fault_files: dict[str, str], clean_files: dict[str, str]) -> None:
    rule = ce_rule_by_slug(slug)
    fault_hits = violations_for_rule(rule, *practice_from_files(fault_files))
    clean_hits = violations_for_rule(rule, *practice_from_files(clean_files))
    _assert_pair(slug, fault_hits, clean_hits)


def example_asset_paths(slug: str, *, channel: str = "python") -> tuple[Path, Path]:
    root = (
        _PRACTICE
        / "model"
        / channel
        / "_examples"
        / slug
    )
    suffix = _SUFFIX[channel]
    return root / "faulty" / f"faultyAsset{suffix}", root / "repaired" / f"repairedAsset{suffix}"


def assert_python_example_pair(slug: str) -> None:
    faulty_path, repaired_path = example_asset_paths(slug)
    assert_rule_pair(
        slug,
        faulty_path.read_text(encoding="utf-8"),
        repaired_path.read_text(encoding="utf-8"),
        lang="python",
    )


def _example_files(folder: Path) -> dict[str, str]:
    """The example's asset plus its `.context` files, placed in one fixture folder."""
    files: dict[str, str] = {}
    for path in folder.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(folder).as_posix()
            files[f"{FIXTURE_FOLDER}/{relative}"] = path.read_text(encoding="utf-8")
    return files


def assert_module_example_pair(slug: str) -> None:
    rule = ce_rule_by_slug(slug)
    root_path = _PRACTICE / "model" / "python" / "_examples" / slug
    fault_hits = violations_for_rule(rule, *practice_from_files(_example_files(root_path / "faulty")))
    clean_hits = violations_for_rule(rule, *practice_from_files(_example_files(root_path / "repaired")))
    if not fault_hits:
        raise AssertionError(f"{slug}: expected fault violations, got none")
    if clean_hits:
        raise AssertionError(f"{slug}: expected clean, got {clean_hits!r}")
