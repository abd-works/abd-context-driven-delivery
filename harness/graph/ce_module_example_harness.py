"""Module-context rules need the full .examples faulty/ folder tree."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from harness.graph.ce_rule_eval_harness import violations_for_rule
from harness.graph.rule_context import RuleCheckContext
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG


def _practice_from_example_folder(folder: Path):
    from harness.graph.ce_rule_eval_harness import practice_from_source

    asset = folder / "faultyAsset.py"
    if not asset.is_file():
        asset = folder / "repairedAsset.py"
    source = asset.read_text(encoding="utf-8")
    practice, root = practice_from_source(source, lang="python", filename=asset.name)
    context_dir = folder / ".context"
    if context_dir.is_dir():
        target = root / ".context"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(context_dir, target)
    return practice, root


def assert_module_example_pair(slug: str) -> None:
    rule = BY_SLUG[slug]
    root_path = (
        Path(__file__).resolve().parents[2]
        / "cdd_guidance/practices/clean_engineering/model/python/_examples"
        / slug
    )
    fault_practice, fault_root = _practice_from_example_folder(root_path / "faulty")
    clean_practice, clean_root = _practice_from_example_folder(root_path / "repaired")
    fault_hits = violations_for_rule(rule, fault_practice, fault_root)
    clean_hits = violations_for_rule(rule, clean_practice, clean_root)
    if not fault_hits:
        raise AssertionError(f"{slug}: expected fault violations, got none")
    if clean_hits:
        raise AssertionError(f"{slug}: expected clean, got {clean_hits!r}")
