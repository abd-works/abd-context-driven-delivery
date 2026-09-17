"""tests-shape - every test suite has a describe/class wrapper + at least one case."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class TestsShapeScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_test_suites():
            yield self.violation(
                "No test suites found",
                location="tests/",
                severity="error",
            )
            return

        for suite in workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            if not suite.name:
                yield self.violation(
                    f"Test suite {path} has no describe/class wrapper",
                    location=self.loc(suite, path),
                    severity="error",
                )
                continue
            if not suite.cases:
                yield self.violation(
                    f"Test suite {path} has {suite.name!r} "
                    "wrapper but no `it`/`test_`/`@Test` cases",
                    location=self.loc(suite, path),
                    severity="error",
                )
