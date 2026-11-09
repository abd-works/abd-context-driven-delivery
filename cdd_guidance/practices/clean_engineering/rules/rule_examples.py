"""Spec support: run Clean Engineering graph rules against a real working-copy build of small fixture trees.

Fixtures go through the same path as a live load: language parser, model nodes loading
their own facts, each node holding its parsed object, rules reading ``node.get_fact``.
"""

from __future__ import annotations

from pathlib import Path

from harness.graph.rule_fixture import RuleFixture, RulePair

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.base_class_model import OoadClass
from cdd_guidance.practices.clean_engineering.model.code_body import CODE_LANGUAGES
from cdd_guidance.practices.clean_engineering.rules import BY_SLUG

FIXTURE_FOLDER = "example"
_PRACTICE = Path(__file__).resolve().parents[1]
# The extension a fixture written in each language takes: the first its language reads.
_SUFFIX = {language.name: language.suffixes[0] for language in CODE_LANGUAGES}


def source_suffix(language: str) -> str:
    """The extension a fixture written in language takes, such as ``.py`` for python."""
    return _SUFFIX[language]


def ce_rule_by_slug(slug: str):
    return BY_SLUG[slug]


def practice_from_files(files: dict[str, str]) -> RuleFixture:
    """The files, read by Clean Engineering from a folder of their own."""
    return RuleFixture(CleanEngineering, files)


def practice_from_class_text(name: str, text: str, relative: str) -> RuleFixture:
    """One class node recorded from source the working copy does not scan (markdown model files)."""
    oclass = OoadClass(name=name, sequential_order=1, line=1)
    oclass.end_line = text.count("\n") + 1
    oclass.take_lines(text.split("\n"))
    oclass.load_source_facts()
    fixture = practice_from_files({relative: text})
    fixture.practice.reading.in_graph.add(oclass, f"clean_engineering:OoadClass:{relative}:{name}", relative, 1, text.count("\n") + 1)
    return fixture


def practice_from_source(source: str, *, lang: str = "python", filename: str | None = None) -> RuleFixture:
    name = filename or f"example{source_suffix(lang)}"
    return practice_from_files({f"{FIXTURE_FOLDER}/{name}": source.strip() + "\n"})


def assert_rule_pair(slug: str, fault_source: str, clean_source: str, *, lang: str = "python") -> None:
    RulePair(ce_rule_by_slug(slug), practice_from_source(fault_source, lang=lang), practice_from_source(clean_source, lang=lang)).check()


def assert_files_rule_pair(slug: str, fault_files: dict[str, str], clean_files: dict[str, str]) -> None:
    RulePair(ce_rule_by_slug(slug), practice_from_files(fault_files), practice_from_files(clean_files)).check()


def example_asset_paths(slug: str, *, channel: str = "python") -> tuple[Path, Path]:
    root = _PRACTICE / "model" / channel / "_examples" / slug
    suffix = source_suffix(channel)
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
    root_path = _PRACTICE / "model" / "python" / "_examples" / slug
    faulty = practice_from_files(_example_files(root_path / "faulty"))
    repaired = practice_from_files(_example_files(root_path / "repaired"))
    RulePair(ce_rule_by_slug(slug), faulty, repaired).check()
