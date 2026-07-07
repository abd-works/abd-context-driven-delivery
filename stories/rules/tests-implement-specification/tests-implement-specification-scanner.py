"""tests-implement-specification — every test case names a scenario in the spec.

Mechanical check on `workspace.tests` cross-referenced with `workspace.scenarios`:
- For each `TestCase`, the case name (normalised) must slug-match some
  `Scenario.name` in the workspace. A test with no walk-through is a spec gap.

Python cases named `test_snake_case_thing` are normalised by stripping the
`test_` prefix and turning underscores into spaces before slug comparison.

This is the coarser check; deeper structural mirroring (`describe = story`,
`Given/When/Then order matches`) is AI-judge territory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _normalise_case_name(name: str) -> str:
    stripped = name.strip()
    if stripped.startswith("test_"):
        stripped = stripped[5:].replace("_", " ")
    return _slug(stripped)


def _matches_scenario(case_slug: str, scenario_slugs: Set[str]) -> bool:
    """A test case matches a scenario if its slug equals a scenario slug OR
    extends one with an outline-example suffix (`<scenario-slug>-<row>`).

    This lets a single Scenario Outline expand into one test-case per Examples
    row while still enforcing that every case traces back to a named scenario.
    """
    if case_slug in scenario_slugs:
        return True
    for slug in scenario_slugs:
        if case_slug.startswith(slug + "-"):
            return True
    return False


class TestsImplementSpecificationScanner(ArtifactScanner):
    """Every test case matches a scenario in the spec."""
    rule = "tests-implement-specification"
    kind = "shape"
    reads = ("test_suites", "scenarios")

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_test_suites():
            return
        scenario_slugs: Set[str] = {_slug(sc.name) for sc in self.workspace.scenarios}
        if not scenario_slugs:
            return
        for suite in self.workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            for case in suite.cases:
                if _matches_scenario(_normalise_case_name(case.name), scenario_slugs):
                    continue
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Test case {case.name!r} in {path} has no matching "
                        f"scenario in the workspace"
                    ),
                    location=self.location(case.story_source, f"{path}::{case.name!r}"),
                    severity="warning",
                    hint=(
                        "Add the walk-through first — a Scenario with the same "
                        "verbatim title lives in `scenarios/`, and the `it` name "
                        "must match it word-for-word"
                    ),
                )


if __name__ == "__main__":
    sys.exit(run(TestsImplementSpecificationScanner))
