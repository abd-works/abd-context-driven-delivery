#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/ac_domain_crossing_scanner.py`."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Set

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


class ACDomainCrossingScanner(StoryScanner):
    BEHAVIORAL_VERBS = {
        "renders",
        "extracts",
        "validates",
        "assigns",
        "generates",
        "updates",
        "applies",
        "detects",
        "reports",
        "synchronizes",
        "routes",
        "processes",
        "creates",
        "removes",
        "moves",
    }

    DOMAIN_KEYWORDS = {
        "epic": "epic",
        "sub-epic": "sub-epic",
        "sub_epic": "sub-epic",
        "story": "story",
        "stories": "story",
        "actor": "actor",
        "actors": "actor",
        "increment": "increment",
        "lane": "increment",
        "acceptance criteria": "acceptance_criteria",
        "ac box": "acceptance_criteria",
        "ac cell": "acceptance_criteria",
    }

    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        if not isinstance(node, Story):
            return violations

        ac_list = node.data.get("acceptance_criteria", [])
        for ac_idx, ac in enumerate(ac_list):
            text = self._get_ac_text(ac)
            violation = self._check_ac_crosses_domains(node, text, ac_idx)
            if violation:
                violations.append(violation)

        return violations

    def _check_ac_crosses_domains(self, story: Story, ac_text: str, ac_idx: int) -> Dict[str, Any] | None:
        text_lower = ac_text.lower()
        domains_with_verbs: Set[str] = set()

        for keyword, domain in self.DOMAIN_KEYWORDS.items():
            if keyword in text_lower:
                words = text_lower.split()
                has_verb = any(w in self.BEHAVIORAL_VERBS for w in words)
                if has_verb:
                    domains_with_verbs.add(domain)

        if len(domains_with_verbs) >= 2:
            snippet = ac_text[:80] + "..." if len(ac_text) > 80 else ac_text
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'AC in story "{story.name}" mixes behaviors of '
                    f'{", ".join(sorted(domains_with_verbs))} -- '
                    f"signal to split story by domain. "
                    f'AC: "{snippet}"'
                ),
                location=story.map_location("acceptance_criteria"),
                severity="warning",
            ).to_dict()

        return None


if __name__ == "__main__":
    sys.exit(
        main_with_scanner(
            ACDomainCrossingScanner,
            rule_md_name="keep-acceptance-criteria-consistent-across-connected-domains",
        )
    )
