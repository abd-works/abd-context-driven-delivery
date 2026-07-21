"""scenario-test-coverage — every Scenario has a covering TestCase (any language)."""

from __future__ import annotations

import re

from story_workspace_base import StoryWorkspaceScanner


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def _case_covers(scenario_name: str, case) -> bool:
    target = _norm(scenario_name)
    if not target:
        return False
    for candidate in (case.covers_scenario, case.name):
        cn = _norm(candidate)
        if not cn:
            continue
        if target in cn or cn in target:
            return True
    return False


class ScenarioTestCoverageScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_story_map():
            return
        # Flatten all cases once — language is irrelevant after channel parse.
        all_cases = list(workspace.iter_test_cases())
        for story in workspace.story_map.all_stories():
            scenarios = list(getattr(story, "scenarios", []) or [])
            if not scenarios:
                continue
            # Prefer cases attached to the story; fall back to workspace-wide.
            cases = list(getattr(story, "test_cases", []) or []) or all_cases
            if not cases:
                continue
            for scenario in scenarios:
                if any(_case_covers(scenario.name, c) for c in cases):
                    continue
                yield self.violation(
                    f"Scenario {scenario.name!r} on story {story.name!r} "
                    f"has no covering test case in any language channel",
                    location=self.loc(scenario, f"scenario {scenario.name!r}"),
                    severity="error",
                )
