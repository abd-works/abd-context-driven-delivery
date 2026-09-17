"""assertions-against-real-behavior - tests carry real assertions on real imports."""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


def _case_loc(case, path: str) -> str:
    if case.story_source is not None:
        try:
            return case.story_source.render()
        except Exception:
            pass
    return f"{path}::{case.name!r}"


class AssertionsAgainstRealBehaviorScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for suite in workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            if not suite.imports_real:
                yield self.violation(
                    f"Test file {path} imports no production code "
                    f"(only mocks / test framework imports)",
                    location=self.loc(suite, path),
                    severity="warning",
                )
                continue
            for case in suite.cases:
                if not case.has_real_assertion:
                    yield self.violation(
                        f"Test case {case.name!r} in {path} has no assertions",
                        location=_case_loc(case, path),
                        severity="error",
                    )
