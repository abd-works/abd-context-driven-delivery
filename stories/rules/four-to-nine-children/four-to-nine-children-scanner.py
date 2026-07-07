"""four-to-nine-children — every parent has 4-9 direct children.

Applies uniformly across the four artifact kinds by walking the Workspace
domain model — no text parsing.

Dimensions checked:
- story map:   Epic -> sub_epics, SubEpic -> (sub_epics or stories)
- increments:  Increment -> stories (living on story_map.increments)
- scenarios:   Scenario -> clauses
- test suites: TestSuite -> cases

Bands (per the rule doc):
- 4-9   OK
- 3, 10 warning
- <=2, >=11 error

Zero-children parents are ignored here — the shape scanners
(story-map-shape, scenarios-shape, tests-shape) own the empty-parent case.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


def _band(count: int):
    if 4 <= count <= 9:
        return None
    if count in (3, 10):
        return "warning"
    return "error"


class FourToNineChildrenScanner(ArtifactScanner):
    """Enforce 4-9 direct children across the story hierarchy."""
    rule = "four-to-nine-children"
    kind = "shape"
    reads = ("story_map", "increments", "scenarios", "test_suites")

    def scan(self) -> Iterator[Violation]:
        yield from self._scan_story_map()
        yield from self._scan_increments()
        yield from self._scan_scenarios()
        yield from self._scan_test_suites()

    def _scan_story_map(self) -> Iterator[Violation]:
        if not self.workspace.has_story_map():
            return
        for epic in self.workspace.story_map.epics:
            yield from self._check(epic, "epic", "sub-epics", len(epic.sub_epics))
            for sub in _walk_sub_epics(epic):
                child_count = len(sub.sub_epics) + len(sub.stories)
                label = "children" if sub.sub_epics and sub.stories else (
                    "sub-epics" if sub.sub_epics else "stories"
                )
                yield from self._check(sub, "sub-epic", label, child_count)

    def _scan_increments(self) -> Iterator[Violation]:
        if not self.workspace.has_increments():
            return
        for inc in self.workspace.story_map.increments:
            yield from self._check(inc, "increment", "stories", len(inc.stories))

    def _scan_scenarios(self) -> Iterator[Violation]:
        for sc in self.workspace.scenarios:
            yield from self._check(sc, "scenario", "clauses", sc.clause_count)

    def _scan_test_suites(self) -> Iterator[Violation]:
        for suite in self.workspace.test_suites:
            label = _suite_label(suite)
            yield from self._check_suite(suite, label, len(suite.cases))

    def _check(self, node, kind_label: str, child_label: str, count: int) -> Iterator[Violation]:
        if count == 0:
            return
        severity = _band(count)
        if severity is None:
            return
        name = getattr(node, "name", None) or getattr(node, "path", None) or "?"
        yield Violation(
            rule=self.rule,
            message=f"{kind_label} {name!r}: {count} {child_label} (target 4-9)",
            location=self.location(getattr(node, "source", None), f"{kind_label} {name!r}"),
            severity=severity,
            hint="Split parents past 9; expand parents below 4; merge or drop parents with 1 child",
        )

    def _check_suite(self, suite, label: str, count: int) -> Iterator[Violation]:
        if count == 0:
            return
        severity = _band(count)
        if severity is None:
            return
        yield Violation(
            rule=self.rule,
            message=f"test suite {label!r}: {count} cases (target 4-9)",
            location=self.location(getattr(suite, "source", None), f"test suite {label!r}"),
            severity=severity,
            hint="Split suites past 9; expand suites below 4; merge or drop suites with 1 case",
        )


def _suite_label(suite) -> str:
    if suite.source is not None and suite.source.file:
        return suite.source.file
    return suite.name or f"{suite.tier}/{suite.language}"


def _walk_sub_epics(epic):
    for sub in epic.sub_epics:
        yield sub
        for nested in _walk_sub_epics(sub):
            yield nested


if __name__ == "__main__":
    sys.exit(run(FourToNineChildrenScanner))
