#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/story_sizing_scanner.py`."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parent.parent
_SKILLS = _ROOT.parent
for _p in (
    _SKILLS / "execute-skill-using-skills-rules" / "scripts",
    _SKILLS / "story-graph-ops" / "scripts",
    _ROOT / "scanners",
):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

from scanner_runner import main_with_scanner  # noqa: E402
from scanner_bases.violation import Violation  # noqa: E402
from story_map import Story, StoryNode  # noqa: E402
from story_scanner import StoryScanner  # noqa: E402


class StorySizingScanner(StoryScanner):
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        if isinstance(node, Story):
            violation = self._check_story_acceptance_criteria_count(node)
            if violation:
                violations.append(violation)

        return violations

    def _check_story_acceptance_criteria_count(self, story: Story) -> Optional[Dict[str, Any]]:
        acceptance_criteria = story.data.get("acceptance_criteria", [])

        if not acceptance_criteria:
            return None

        count = self._count_when_then_and(acceptance_criteria)

        if count == 0:
            return None

        severity, message = self._get_size_violation(count, "acceptance criteria")

        if severity:
            location = story.map_location("acceptance_criteria")
            return Violation(
                rule=self.rule,
                violation_message=f'Story "{story.name}" has {count} {message}',
                location=location,
                severity=severity,
            ).to_dict()

        return None

    def _count_when_then_and(self, acceptance_criteria: List[Any]) -> int:
        combined_text = " ".join([self._get_ac_text(ac) for ac in acceptance_criteria])

        text = re.sub(r"\(AC\)\s*", "", combined_text, flags=re.IGNORECASE)

        when_count = len(re.findall(r"\bWHEN\b", text, re.IGNORECASE))
        and_count = len(re.findall(r"\bAND\b", text, re.IGNORECASE))

        return when_count + and_count

    def _get_size_violation(self, count: int, item_type: str) -> Tuple[Optional[str], str]:
        if 4 <= count <= 10:
            return None, f"{count} {item_type} (perfect)"
        elif count == 3 or count == 11:
            return "warning", f"{count} {item_type} (should be 4-10)"
        elif count <= 2 or count >= 12:
            return "error", f"{count} {item_type} (should be 4-10)"
        else:
            return "warning", f"{count} {item_type} (should be 4-10)"


if __name__ == "__main__":
    sys.exit(main_with_scanner(StorySizingScanner, rule_md_name="stories-have-4-to-9-acceptance-criteria"))
