"""Format-specific StoryNode subtypes for the Java code format.

JavaStoryMap also knows how to discover and parse Java test files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from contexts.stories.story_model.nodes import Epic, Story, SubEpic
from contexts.stories.story_model.scenario import Scenario
from contexts.stories.story_model.source_location import SourceLocation
from contexts.stories.story_model.story_map import StoryMap
from contexts.stories.code.step_body import case_body_is_stub, unimplemented_steps_java
from contexts.stories.story_model.test_file import Language, Test, TestCase, TestSuite, Tier, extract_bug_id

_CLASS = re.compile(r"^\s*(?:public\s+)?class\s+(?P<name>\w+Test)\b", re.MULTILINE)
_TEST = re.compile(
    r"@Test\b[^\n]*\n\s*(?:public\s+)?void\s+(?P<name>\w+)\s*\(",
    re.MULTILINE,
)
_ASSERT = re.compile(r"\b(assertEquals|assertTrue|assertNotNull|Assertions\.)")
_TIER = re.compile(r"^(?:[A-Z][A-Za-z0-9]*?)(?P<tier>[A-Z][A-Za-z0-9]*)Test\.java$")
_GLOBS = (
    "**/tests/**/*Test.java",
    "tests/**/*Test.java",
)


class JavaScenario(Scenario):
    pass


class JavaStory(Story):
    def create_child_scenario(self, source: Scenario) -> JavaScenario:
        return JavaScenario(source.name, source.sequential_order, source.story_name)


class JavaSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "JavaSubEpic":
        return JavaSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> JavaStory:
        return JavaStory(source.name, source.sequential_order, source.story_type)


class JavaEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> JavaSubEpic:
        return JavaSubEpic(source.name, source.sequential_order)


class JavaStoryMap(StoryMap):
    """Format-typed root for the Java code format. Parses *Test.java files."""

    def create_child_epic(self, source: JavaEpic) -> JavaEpic:
        return JavaEpic(source.name, source.sequential_order)

    @classmethod
    def from_workspace(cls, root: Path) -> List[TestSuite]:
        """Find and parse all Java test files under *root*."""
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
        for func in _TEST.finditer(text):
            offset = func.start()
            body = text[offset: offset + 1200]
            name = func.group("name")
            assertions = len(_ASSERT.findall(body))
            cases.append(TestCase(
                tier=tier, name=name,
                tests=[Test()], assertions_count=assertions,
                has_real_assertion=assertions > 0,
                has_unimplemented_body=case_body_is_stub(body),
                references_bug_id=extract_bug_id(body),
                story_source=SourceLocation(rel, text.count("\n", 0, offset) + 1),
                covers_scenario=re.sub(r"([a-z])([A-Z])", r"\1 \2", name).replace("_", " ").lower(),
            ))
        return TestSuite(
            tier=tier, language=Language("java"),
            name=describe, cases=cases,
            imports_real=True,
            source=SourceLocation(rel, 1),
            unimplemented_steps=unimplemented_steps_java(text),
        )

    @staticmethod
    def _tier(name: str) -> Tier:
        m = _TIER.search(name)
        return Tier(m.group("tier").lower()) if m else Tier("")
