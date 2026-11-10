"""Module-context rules need the full .examples faulty/ folder tree, context files included."""

from __future__ import annotations

from pathlib import Path

from harness.graph.ce_rule_eval_harness import FIXTURE_FOLDER, practice_from_files, violations_for_rule
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG


def _example_files(folder: Path) -> dict[str, str]:
    """The example's asset plus its `.context` files, placed in one fixture folder."""
    files: dict[str, str] = {}
    for path in folder.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts:
            relative = path.relative_to(folder).as_posix()
            files[f"{FIXTURE_FOLDER}/{relative}"] = path.read_text(encoding="utf-8")
    return files


def assert_module_example_pair(slug: str) -> None:
    rule = BY_SLUG[slug]
    root_path = (
        Path(__file__).resolve().parents[2]
        / "cdd_guidance/practices/clean_engineering/model/python/_examples"
        / slug
    )
    fault_hits = violations_for_rule(rule, *practice_from_files(_example_files(root_path / "faulty")))
    clean_hits = violations_for_rule(rule, *practice_from_files(_example_files(root_path / "repaired")))
    if not fault_hits:
        raise AssertionError(f"{slug}: expected fault violations, got none")
    if clean_hits:
        raise AssertionError(f"{slug}: expected clean, got {clean_hits!r}")
