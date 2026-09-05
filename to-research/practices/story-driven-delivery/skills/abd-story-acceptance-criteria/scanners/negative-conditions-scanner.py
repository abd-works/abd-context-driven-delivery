#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/negative_conditions_scanner.py`."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List

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


class NegativeConditionsScanner(StoryScanner):
    _ERROR_PHRASES = (
        "returns error",
        "return error",
        "validation error",
        "validation fails",
        "invalid input",
        "shows validation errors",
    )

    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        acceptance_criteria = node.data.get("acceptance_criteria", [])
        for idx, ac in enumerate(acceptance_criteria):
            text = self._get_ac_text(ac)
            if not text.strip():
                continue
            if not self._implies_error_or_block(text):
                continue
            if self._has_but_step(text):
                continue
            loc = node.map_location(f"acceptance_criteria[{idx}]")
            violations.append(
                Violation(
                    rule=self.rule,
                    violation_message=(
                        f'Story "{node.name}" AC #{idx + 1}: describes error/validation outcome but has no BUT step '
                        f"stating what the system does not do (e.g. save, allow, drop)."
                    ),
                    location=loc,
                    severity="warning",
                ).to_dict()
            )
        return violations

    def _implies_error_or_block(self, text: str) -> bool:
        lower = text.lower()
        if any(p in lower for p in self._ERROR_PHRASES):
            return True
        if re.search(r"\bcannot\s+\w+\s+(create|add|save|drop)", lower):
            return True
        if "prevents" in lower and ("operation" in lower or "create" in lower):
            return True
        return False

    def _has_but_step(self, text: str) -> bool:
        for line in text.splitlines():
            s = line.strip()
            if s.upper().startswith("BUT ") or s.upper().startswith("BUT\t"):
                return True
        return False


if __name__ == "__main__":
    sys.exit(main_with_scanner(NegativeConditionsScanner, rule_md_name="use-but-for-negative-conditions"))
