"""bug-fix-test-first — every bug-fix test cites a walk-through carrying the same bug.

Mechanical check:
- For each `TestCase.references_bug_id` (extracted from body comments by the
  tests loader, format `BUG-1234` or `issue 42`), at least one scenario in the
  workspace must reference the same id in its source text.

This proves the walk-through step 1 happened: the bug appears as a documented
scenario, not merely as a code comment in the test.

Steps 2-4 (failing-first, code-fixes-test, verification) are process
disciplines that no scanner can catch.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterator, Set

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from stories.src.skill.scanners._base import ArtifactScanner, Violation, run  # noqa: E402


_BUG_ID = re.compile(r"(?:BUG|BUG-|issue\s*)([A-Z]+-\d+|\d+)", re.IGNORECASE)


class BugFixTestFirstScanner(ArtifactScanner):
    """Every bug-fix test has a matching walk-through."""
    rule = "bug-fix-test-first"
    kind = "quality"
    reads = ("test_suites", "scenarios")

    def scan(self) -> Iterator[Violation]:
        scenario_bug_ids = self._collect_scenario_bug_ids()
        for suite in self.workspace.test_suites:
            path = suite.source.file if suite.source else "<unknown>"
            for case in suite.cases:
                bug = case.references_bug_id.strip()
                if not bug:
                    continue
                if bug.upper() not in scenario_bug_ids:
                    yield Violation(
                        rule=self.rule,
                        message=(
                            f"Test case {case.name!r} cites bug {bug!r} but no scenario "
                            f"references it — walk-through must precede the fix"
                        ),
                        location=self.location(case.story_source, f"{path}::{case.name!r}"),
                        severity="error",
                        hint=(
                            "Add the walk-through first: a scenario titled after "
                            "the correct behaviour with a `# Bug: <id>` citation, "
                            "then let the test derive from it"
                        ),
                    )

    def _collect_scenario_bug_ids(self) -> Set[str]:
        ids: Set[str] = set()
        for sc in self.workspace.scenarios:
            source = sc.source
            if source is None:
                continue
            source_path = self.workspace.root / source.file
            if not source_path.exists():
                continue
            text = source_path.read_text(encoding="utf-8", errors="replace")
            for m in _BUG_ID.finditer(text):
                ids.add(m.group(1).upper())
        return ids


if __name__ == "__main__":
    sys.exit(run(BugFixTestFirstScanner))
