"""Workspace — the parsed-artifact aggregate that scanners consume.

Use `Workspace.load(root)` to populate from a workspace folder.

Canonical locations per `domain-context.md`:
- Increments live on `story_map.increments` (reconciled by translate_from).
- TestSuites live on each `SubEpic.test_suites` (value-copied by update_self).
- TestCases live on each `Story.test_cases` (value-copied by update_self).

`workspace.test_suites` is a flattened view convenience so scanners can walk
tests without recursing the tree themselves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, List

from .scenario import Scenario
from .story_context import StoryContext
from .story_map import StoryMap
from .test_file import TestSuite
from .thin_slice import Increment


@dataclass
class Workspace:
    """Everything a scanner needs, already parsed."""

    root: Path
    story_map: StoryMap
    scenarios: List[Scenario] = field(default_factory=list)
    test_suites: List[TestSuite] = field(default_factory=list)
    story_contexts: List[StoryContext] = field(default_factory=list)

    @classmethod
    def load(cls, root: Path) -> "Workspace":
        """Discover and parse every artifact kind under *root*."""
        from stories.src.stories.code.java.nodes import JavaStoryMap
        from stories.src.stories.code.javascript.nodes import JavaScriptStoryMap
        from stories.src.stories.code.python.nodes import PythonStoryMap
        from stories.src.stories.code.typescript.nodes import TypeScriptStoryMap
        from stories.src.stories.document.json.nodes import JsonStoryMap
        from stories.src.stories.document.markdown.nodes import (
            MarkdownIncrement,
            MarkdownScenario,
            MarkdownStoryMap,
        )

        root = Path(root).resolve()

        story_map: StoryMap = (
            JsonStoryMap.from_workspace(root)
            or MarkdownStoryMap.from_workspace(root)
            or StoryMap()
        )

        scenarios = MarkdownScenario.from_workspace(root)
        story_map.attach_scenarios(scenarios)

        # Increments may already be present if loaded from story-graph.json.
        # Only fall back to markdown if JSON did not supply them.
        if not story_map.increments:
            for inc in MarkdownIncrement.from_workspace(root):
                story_map.increments.append(inc)

        test_suites = [
            *TypeScriptStoryMap.from_workspace(root),
            *JavaScriptStoryMap.from_workspace(root),
            *PythonStoryMap.from_workspace(root),
            *JavaStoryMap.from_workspace(root),
        ]
        story_map.attach_test_suites(test_suites)

        return cls(
            root=root,
            story_map=story_map,
            scenarios=scenarios,
            test_suites=test_suites,
            story_contexts=StoryContext.from_workspace(root),
        )

    # ── canonical guards ────────────────────────────────────────────────────

    def has_story_map(self) -> bool:
        try:
            return bool(self.story_map and getattr(self.story_map, "epics", None))
        except Exception:
            return False

    def has_increments(self) -> bool:
        return bool(getattr(self.story_map, "increments", None))

    def has_scenarios(self) -> bool:
        return bool(self.scenarios)

    def has_test_suites(self) -> bool:
        return bool(self.test_suites)

    def has_story_contexts(self) -> bool:
        return bool(self.story_contexts)

    # ── convenience views ───────────────────────────────────────────────────

    @property
    def increments(self) -> List[Increment]:
        """Flat list of Increments living on `story_map.increments`."""
        return list(getattr(self.story_map, "increments", []) or [])

    @property
    def tests(self) -> List[TestSuite]:
        """Alias for `test_suites` — scanner-facing name for the flat suite list."""
        return list(self.test_suites)

    def iter_test_cases(self) -> Iterator:
        """Yield every TestCase across every TestSuite (rarely useful; scanners
        usually walk `suite.cases` themselves)."""
        for suite in self.test_suites:
            for case in suite.cases:
                yield case
