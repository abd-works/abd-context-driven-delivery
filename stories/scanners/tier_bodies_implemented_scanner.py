"""tier-bodies-implemented — tier step / case bodies must not be stubs.

Language channels fill `TestSuite.unimplemented_steps` and
`TestCase.has_unimplemented_body`. This scanner never reads source text.
"""

from __future__ import annotations

from story_workspace_base import StoryWorkspaceScanner


class TierBodiesImplementedScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        for suite in workspace.test_suites:
            loc = self.loc(suite, suite.source.file if suite.source else suite.name)
            for step in getattr(suite, "unimplemented_steps", []) or []:
                yield self.violation(
                    f"Tier step {step!r} in {loc} has an unimplemented body — "
                    f"engineering fidelity must produce real code, not scaffolder TODOs",
                    location=loc,
                    severity="warning",
                )
            for case in suite.cases:
                if getattr(case, "has_unimplemented_body", False):
                    yield self.violation(
                        f"Test case {case.name!r} in {loc} has an unimplemented body — "
                        f"engineering fidelity must produce real code, not scaffolder TODOs",
                        location=self.loc(case, f"{loc}:{case.name}"),
                        severity="warning",
                    )
