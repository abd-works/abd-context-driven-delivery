"""tests-implement-specification — every test case names a scenario in the spec."""

from __future__ import annotations

import re
from typing import Set

from story_workspace_base import StoryWorkspaceScanner


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _normalise_case_name(name: str) -> str:
    stripped = name.strip()
    if stripped.startswith("test_"):
        stripped = stripped[5:].replace("_", " ")
    return _slug(stripped)


def _matches_scenario(case_slug: str, scenario_slugs: Set[str]) -> bool:
    if case_slug in scenario_slugs:
        return True
    for slug in scenario_slugs:
        if case_slug.startswith(slug + "-"):
            return True
    return False


def _case_loc(case, path: str) -> str:
    if case.story_source is not None:
        try:
            return case.story_source.render()
        except Exception:
            pass
    return f"{path}::{case.name!r}"


class TestsImplementSpecificationScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        if not workspace.has_test_suites():
            return
        scenario_slugs: Set[str] = {_slug(sc.name) for sc in workspace.scenarios}
        if not scenario_slugs:
            return
        for suite in workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            for case in suite.cases:
                if _matches_scenario(_normalise_case_name(case.name), scenario_slugs):
                    continue
                yield self.violation(
                    f"Test case {case.name!r} in {path} has no matching "
                    f"scenario in the workspace",
                    location=_case_loc(case, path),
                    severity="warning",
                )
