"""tests-shape — every test suite has a describe/class wrapper + at least one case.

The tests loader normalises `describe(...) + it(...)` (TS/JS), `class TestX +
def test_...` (Python) and `class XTest + @Test` (Java) into
`TestSuite` / `TestCase` / `Test` triads. This scanner asserts the invariants:

- The workspace has at least one TestSuite when tests are expected.
- Each TestSuite has a non-empty `name` (the outer describe / class name).
- Each TestSuite has at least one TestCase.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


class TestsShapeScanner(ArtifactScanner):
    """Every test suite has a describe/class wrapper + at least one case."""
    rule = "tests-shape"
    kind = "shape"
    reads = ("test_suites",)

    def scan(self) -> Iterator[Violation]:
        if not self.workspace.has_test_suites():
            yield Violation(
                rule=self.rule,
                message="No test suites found",
                location="tests/",
                severity="error",
                hint=(
                    "Add at least one `*.test.ts`, `test_*.py`, or `*Test.java` file under `tests/`"
                ),
            )
            return

        for suite in self.workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            if not suite.name:
                yield Violation(
                    rule=self.rule,
                    message=f"Test suite {path} has no describe/class wrapper",
                    location=self.location(getattr(suite, "source", None), path),
                    severity="error",
                    hint=(
                        "Wrap the test cases in a `describe(...)` block (TS/JS), a "
                        "`class Test...` (Python), or a `class ...Test` (Java)"
                    ),
                )
                continue
            if not suite.cases:
                yield Violation(
                    rule=self.rule,
                    message=(
                        f"Test suite {path} has {suite.name!r} "
                        "wrapper but no `it`/`test_`/`@Test` cases"
                    ),
                    location=self.location(getattr(suite, "source", None), path),
                    severity="error",
                    hint="Add at least one `it(...)`, `def test_...`, or `@Test void ...` case",
                )


if __name__ == "__main__":
    sys.exit(run(TestsShapeScanner))
