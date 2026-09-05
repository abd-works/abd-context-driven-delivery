#!/usr/bin/env python3
"""Flag AC lines that use internal-action verbs, generic nouns, or label lists without domain grounding."""
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

_INTERNAL_VERBS = re.compile(
    r"\b(?:provides?|records?|sets?|triggers?|loads?|accepts?|processes?|stores?|fetches?|retrieves?)\b",
    re.IGNORECASE,
)

_GENERIC_NOUNS = re.compile(
    r"\bthe\s+(?:data|balances?|details?|information|items?|results?|content)\b",
    re.IGNORECASE,
)

_THEN_LINE = re.compile(r"^\s*(?:THEN|AND|BUT)\b", re.IGNORECASE | re.MULTILINE)


class DomainGroundedACScanner(StoryScanner):
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        acceptance_criteria = node.data.get("acceptance_criteria", [])
        for idx, ac in enumerate(acceptance_criteria):
            text = self._get_ac_text(ac)
            if not text.strip():
                continue

            for line in text.splitlines():
                if not _THEN_LINE.match(line):
                    continue

                msg = self._check_internal_verb(line)
                if not msg:
                    msg = self._check_generic_noun(line)
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
                break
        return violations

    def _check_internal_verb(self, line: str) -> str | None:
        m = _INTERNAL_VERBS.search(line)
        if m:
            return (
                f'uses internal-action verb "{m.group(0)}" — '
                f"describe observable outcome instead"
            )
        return None

    def _check_generic_noun(self, line: str) -> str | None:
        m = _GENERIC_NOUNS.search(line)
        if m:
            return (
                f'uses generic noun "{m.group(0).strip()}" — '
                f"use the precise domain term(s)"
            )
        return None


if __name__ == "__main__":
    sys.exit(main_with_scanner(DomainGroundedACScanner, rule_md_name="ground-ac-in-domain-concepts"))
