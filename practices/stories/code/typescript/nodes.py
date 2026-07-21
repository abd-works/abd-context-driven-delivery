"""Format-specific StoryNode subtypes for the TypeScript code format.

TypeScriptStoryMap also knows how to discover and parse TypeScript/TSX test files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from stories.story_model.nodes import Epic, Story, SubEpic
from stories.story_model.scenario import Scenario
from stories.story_model.source_location import SourceLocation
from stories.story_model.story_map import StoryMap
from stories.code.step_body import case_body_is_stub, unimplemented_steps_typescript
from stories.story_model.test_file import Language, Test, TestCase, TestSuite, Tier, extract_bug_id

_DESCRIBE = re.compile(r"\bdescribe\s*\(\s*[\"'`](?P<title>[^\"'`]+)[\"'`]")
_IT = re.compile(r"\b(it|test)\s*\(\s*[\"'`](?P<title>[^\"'`]+)[\"'`]")
_EXPECT = re.compile(r"\bexpect\s*\(")
_TIER = re.compile(r"-(?P<tier>[a-z][a-z0-9]{0,20})\.(?:test|spec)\.(?:ts|tsx)$")
_GLOBS = (
    "**/tests/**/*.test.ts",
    "**/tests/**/*.test.tsx",
    "**/tests/**/*.spec.ts",
    "tests/**/*.test.ts",
    "tests/**/*.test.tsx",
    "tests/**/*.spec.ts",
    "*.test.ts",
)


class TypeScriptScenario(Scenario):
    pass


class TypeScriptStory(Story):
    def create_child_scenario(self, source: Scenario) -> TypeScriptScenario:
        return TypeScriptScenario(source.name, source.sequential_order, source.story_name)


class TypeScriptSubEpic(SubEpic):
    def create_child_sub_epic(self, source: SubEpic) -> "TypeScriptSubEpic":
        return TypeScriptSubEpic(source.name, source.sequential_order)

    def create_child_story(self, source: Story) -> TypeScriptStory:
        return TypeScriptStory(source.name, source.sequential_order, source.story_type)


class TypeScriptEpic(Epic):
    def create_child_sub_epic(self, source: SubEpic) -> TypeScriptSubEpic:
        return TypeScriptSubEpic(source.name, source.sequential_order)


class TypeScriptStoryMap(StoryMap):
    """Format-typed root for the TypeScript code format. Parses *.test.ts files."""

    def create_child_epic(self, source: TypeScriptEpic) -> TypeScriptEpic:
        return TypeScriptEpic(source.name, source.sequential_order)

    @classmethod
    def from_workspace(cls, root: Path) -> List[TestSuite]:
        """Find and parse all TypeScript test files under *root*."""
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
            tier=tier, language=Language("ts"),
            name=describe, cases=cases,
            imports_real=cls._imports_real(text),
            source=SourceLocation(rel, 1),
            unimplemented_steps=unimplemented_steps_typescript(text),
        )

    @staticmethod
    def _tier(name: str) -> Tier:
        m = _TIER.search(name)
        return Tier(m.group("tier")) if m else Tier("")

    @staticmethod
    def _imports_real(text: str) -> bool:
        for line in text.splitlines():
            m = re.match(r"^\s*import\s.+from\s+['\"](?P<mod>[^'\"]+)['\"]", line)
            if not m:
                continue
            mod = m.group("mod")
            if mod.startswith(("vitest", "jest", "@testing-library")):
                continue
            return True
        return False
