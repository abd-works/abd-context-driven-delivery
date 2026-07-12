"""assertions-against-real-behavior — tests carry real assertions on real imports.

Mechanical checks on `workspace.tests`:
- Every `TestCase.has_real_assertion` is True (i.e. the case body contains at
  least one `expect(...)` / `assert` / `assertEquals`). A test with no assertion
  proves nothing.
- Every `TestFile.imports_real` is True — the file imports at least one
  non-mock/non-testing-framework module. A file that imports only mocks is
  testing the mocks.

Full-result-shape and public-surface disciplines are AI-judge territory —
the mechanical check catches only the coarse "no assertion" / "no real code"
failures.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class AssertionsAgainstRealBehaviorScanner(ArtifactScanner):
    """Every test has at least one real assertion; every test file imports real code."""
    rule = "assertions-against-real-behavior"
    kind = "quality"
    reads = ("test_suites",)

    def scan(self) -> Iterator[Violation]:
        for suite in self.workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            if not suite.imports_real:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Test file {path} imports no production code "
                        f"(only mocks / test framework imports)"
                    ),
                    location=self.location(suite.source, path),
                    severity="warning",
                    hint=(
                        "Import the production module the scenario exercises — a "
                        "test asserting on mock return values is testing the mock"
                    ),
                )
                continue
            for case in suite.cases:
                if not case.has_real_assertion:
                    yield Violation(
                        rule=self.rule,
                        message=(
                            f"Test case {case.name!r} in {path} has no assertions"
                        ),
                        location=self.location(case.story_source, f"{path}::{case.name!r}"),
                        severity="error",
                        hint=(
                            "Add an assertion against the observable outcome — "
                            "assert on the full result object, not a single field"
                        ),
                    )


if __name__ == "__main__":
    sys.exit(run(AssertionsAgainstRealBehaviorScanner))
