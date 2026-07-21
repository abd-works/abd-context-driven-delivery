"""Format-specific StoryNode subtypes for the Python code format.

PythonStoryMap also knows how to discover and parse Python test files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from stories.story_model.nodes import Epic, Story, SubEpic
from stories.story_model.scenario import Scenario
from stories.story_model.source_location import SourceLocation
from stories.story_model.story_map import StoryMap
from stories.code.step_body import case_body_is_stub, unimplemented_steps_python
from stories.story_model.test_file import Language, Test, TestCase, TestSuite, Tier, extract_bug_id

_CLASS = re.compile(r"^\s*class\s+(?P<name>Test\w+)", re.MULTILINE)
_FUNC = re.compile(r"^\s*def\s+(?P<name>test_\w+)\s*\(", re.MULTILINE)
_ASSERT = re.compile(r"^\s*(assert |self\.assert)", re.MULTILINE)
_TIER = re.compile(r"^test_[a-z0-9_]+?_(?P<tier>[a-z][a-z0-9]{0,20})\.py$")
_GLOBS = (
    "**/tests/**/test_*.py",
    "**/tests/**/*_test.py",
    "tests/**/test_*.py",
    "tests/**/*_test.py",
    "test_*.py",
)


class PythonScenario(Scenario):
    pass


class PythonStory(Story):
    def create_child_scenario(self, source: Scenario) -> PythonScenario:
        return PythonScenario(source.name, source.sequential_order, source.story_name)


class PythonSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "PythonSubEpic":
        return PythonSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> PythonStory:
        return PythonStory(source.name, source.sequential_order, source.story_type)


class PythonEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> PythonSubEpic:
        return PythonSubEpic(source.name, source.sequential_order)


class PythonStoryMap(StoryMap):
    """Format-typed root for the Python code format. Parses test_*.py / *_test.py files."""

    def create_child_epic(self, source: PythonEpic) -> PythonEpic:
        return PythonEpic(source.name, source.sequential_order)

    @classmethod
    def from_workspace(cls, root: Path) -> List[TestSuite]:
        """Find and parse all Python test files under *root*."""
        root = Path(root).resolve()
        seen: set = set()
        suites: List[TestSuite] = []
        for pattern in _GLOBS:
            for p in root.glob(pattern):
                if p in seen or not p.is_file():
                    continue
                seen.add(p)
                suites.append(cls._parse_file(p, root))
        return suites

    @classmethod
    def _parse_file(cls, path: Path, root: Path) -> TestSuite:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = str(path.relative_to(root)).replace("\\", "/")
        tier = cls._tier(path.name)
        describe = m.group("name") if (m := _CLASS.search(text)) else ""
        cases: List[TestCase] = []
        for func in _FUNC.finditer(text):
            offset = func.start()
            body = text[offset: offset + 1200]
            assertions = len(_ASSERT.findall(body))
            cases.append(TestCase(
                tier=tier, name=func.group("name"),
                tests=[Test()], assertions_count=assertions,
                has_real_assertion=assertions > 0,
                has_unimplemented_body=case_body_is_stub(body),
                references_bug_id=extract_bug_id(body),
                story_source=SourceLocation(rel, text.count("\n", 0, offset) + 1),
                covers_scenario=_scenario_name_from_test(func.group("name")),
            ))
        return TestSuite(
            tier=tier, language=Language("py"),
            name=describe, cases=cases,
            imports_real=True,
            source=SourceLocation(rel, 1),
            unimplemented_steps=unimplemented_steps_python(text),
        )

    @staticmethod
    def _tier(name: str) -> Tier:
        m = _TIER.search(name)
        return Tier(m.group("tier")) if m else Tier("")


def _scenario_name_from_test(test_name: str) -> str:
    """Best-effort: test_order_accepted_… → order accepted …"""
    slug = test_name[5:] if test_name.startswith("test_") else test_name
    return slug.replace("_", " ").strip()
