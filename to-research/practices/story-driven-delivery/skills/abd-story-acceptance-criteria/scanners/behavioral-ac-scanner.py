#!/usr/bin/env python3
"""Flag non-behavioral wording in story acceptance_criteria: Given in AC, obvious implementation jargon."""
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

# Heuristic patterns aligned with exploration rule DO/DON'T (behavior vs implementation).
_TECH_PATTERNS: List[Tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\b(?:json|xml|yaml)\s+file\b", re.IGNORECASE),
        "prefer behavioral outcome instead of file-format storage (e.g. saved configuration)",
    ),
    (
        re.compile(r"\bparses?\s+(?:json|xml|yaml)\b", re.IGNORECASE),
        "describe the behavioral result, not parsing a format",
    ),
    (
        re.compile(r"\bexecute(?:s|d)?\s+sql\b|\bsql\s+query\b", re.IGNORECASE),
        "describe data behavior, not SQL mechanics",
    ),
    (
        re.compile(r"\bapi\s+endpoint\b|\brest\s+(?:get|post|put|delete)\b", re.IGNORECASE),
        "describe the system response, not REST/API plumbing",
    ),
    (
        re.compile(
            r"\bcalls?\s+method\b|\binvokes?\s+method\b|\bclass\s+instantiates\b",
            re.IGNORECASE,
        ),
        "describe observable behavior, not programming constructs",
    ),
    (
        re.compile(r"\bsystem\s+parses\s+json\s+config\b", re.IGNORECASE),
        "rephrase as user/system outcome",
    ),
]

_GIVEN_LINE = re.compile(r"^\s*Given\b", re.IGNORECASE | re.MULTILINE)


class BehavioralACScanner(StoryScanner):
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        acceptance_criteria = node.data.get("acceptance_criteria", [])
        for idx, ac in enumerate(acceptance_criteria):
            text = self._get_ac_text(ac)
            if not text.strip():
                continue

            msg = self._check_given(text)
            if not msg:
                msg = self._check_technical(text)
            if not msg:
                continue

            loc = node.map_location(f"acceptance_criteria[{idx}]")
            violations.append(
                Violation(
                    rule=self.rule,
                    violation_message=f'Story "{node.name}" AC #{idx + 1}: {msg}',
                    location=loc,
                    severity="warning",
                ).to_dict()
            )
        return violations

    def _check_given(self, text: str) -> Optional[str]:
        if _GIVEN_LINE.search(text):
            return (
                'uses "Given" - reserve Given for scenario steps; use WHEN/THEN in acceptance_criteria'
            )
        return None

    def _check_technical(self, text: str) -> Optional[str]:
        for pattern, hint in _TECH_PATTERNS:
            m = pattern.search(text)
            if m:
                return f'possibly implementation wording ("{m.group(0)}"): {hint}'
        return None


if __name__ == "__main__":
    sys.exit(main_with_scanner(BehavioralACScanner, rule_md_name="behavioral-ac-at-story-level"))
