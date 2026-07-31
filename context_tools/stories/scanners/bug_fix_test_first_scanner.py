"""bug-fix-test-first - every bug-fix test cites a walk-through with the same bug."""

from __future__ import annotations

import re
from typing import Set

from story_workspace_base import StoryWorkspaceScanner

_BUG_ID = re.compile(r"(?:BUG|BUG-|issue\s*)([A-Z]+-\d+|\d+)", re.IGNORECASE)


def _case_loc(case, path: str) -> str:
    if case.story_source is not None:
        try:
            return case.story_source.render()
        except Exception:
            pass
    return f"{path}::{case.name!r}"


class BugFixTestFirstScanner(StoryWorkspaceScanner):
    def scan_workspace(self, workspace):
        scenario_bug_ids = self._collect_scenario_bug_ids(workspace)
        for suite in workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            for case in suite.cases:
                bug = (case.references_bug_id or "").strip()
                if not bug:
                    continue
                if bug.upper() not in scenario_bug_ids:
                    yield self.violation(
                        f"Test case {case.name!r} cites bug {bug!r} but no scenario "
                        f"references it - walk-through must precede the fix",
                        location=_case_loc(case, path),
                        severity="error",
                    )

    def _collect_scenario_bug_ids(self, workspace) -> Set[str]:
        ids: Set[str] = set()
        for sc in workspace.scenarios:
            source = sc.source
            if source is None:
                continue
            source_path = workspace.root / source.file
            if not source_path.exists():
                continue
            text = source_path.read_text(encoding="utf-8", errors="replace")
            for m in _BUG_ID.finditer(text):
                ids.add(m.group(1).upper())
        return ids
