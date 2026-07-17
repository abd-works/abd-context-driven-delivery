"""Format-specific StoryNode subtypes for the JavaScript code format.

JavaScriptStoryMap also knows how to discover and parse JavaScript test files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from stories.story_model.nodes import Epic, Story, SubEpic
from stories.story_model.scenario import Scenario
from stories.story_model.source_location import SourceLocation
from stories.story_model.story_map import StoryMap
from stories.code.step_body import case_body_is_stub, unimplemented_steps_javascript
from stories.story_model.test_file import Language, Test, TestCase, TestSuite, Tier, extract_bug_id

_DESCRIBE = re.compile(r"\bdescribe\s*\(\s*[\"'`](?P<title>[^\"'`]+)[\"'`]")
_IT = re.compile(r"\b(it|test)\s*\(\s*[\"'`](?P<title>[^\"'`]+)[\"'`]")
_EXPECT = re.compile(r"\bexpect\s*\(")
_TIER = re.compile(r"-(?P<tier>[a-z][a-z0-9]{0,20})\.(?:test|spec)\.(?:js|jsx)$")
_GLOBS = (
    "**/tests/**/*.test.js",
    "**/tests/**/*.spec.js",
    "tests/**/*.test.js",
)


class JavaScriptScenario(Scenario):
    pass


class JavaScriptStory(Story):
    def create_child_scenario(self, source: Scenario) -> JavaScriptScenario:
        return JavaScriptScenario(source.name, source.sequential_order, source.story_name)


class JavaScriptSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "JavaScriptSubEpic":
        return JavaScriptSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> JavaScriptStory:
        return JavaScriptStory(source.name, source.sequential_order, source.story_type)


class JavaScriptEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> JavaScriptSubEpic:
        return JavaScriptSubEpic(source.name, source.sequential_order)


class JavaScriptStoryMap(StoryMap):
    """Format-typed root for the JavaScript code format. Parses *.test.js files."""

    def create_child_epic(self, source: JavaScriptEpic) -> JavaScriptEpic:
        return JavaScriptEpic(source.name, source.sequential_order)

    @classmethod
    def from_workspace(cls, root: Path) -> List[TestSuite]:
        """Find and parse all JavaScript test files under *root*."""
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
        describe = m.group("title").strip() if (m := _DESCRIBE.search(text)) else ""
        cases: List[TestCase] = []
        for it in _IT.finditer(text):
            offset = it.start()
            body = text[offset: offset + 800]
            title = it.group("title").strip()
            assertions = len(_EXPECT.findall(body))
            cases.append(TestCase(
                tier=tier, name=title,
                tests=[Test()], assertions_count=assertions,
                has_real_assertion=assertions > 0,
                has_unimplemented_body=case_body_is_stub(body),
                references_bug_id=extract_bug_id(body),
                story_source=SourceLocation(rel, text.count("\n", 0, offset) + 1),
                covers_scenario=title,
            ))
        return TestSuite(
            tier=tier, language=Language("js"),
            name=describe, cases=cases,
            imports_real=True,
            source=SourceLocation(rel, 1),
            unimplemented_steps=unimplemented_steps_javascript(text),
        )

    @staticmethod
    def _tier(name: str) -> Tier:
        m = _TIER.search(name)
        return Tier(m.group("tier")) if m else Tier("")
