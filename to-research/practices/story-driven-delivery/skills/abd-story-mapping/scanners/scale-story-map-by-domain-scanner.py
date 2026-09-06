#!/usr/bin/env python3
"""Soft thresholds when a sub-epic or story AC mixes many domain concepts."""
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
from story_map import Story, StoryNode, SubEpic  # noqa: E402
from story_scanner import StoryScanner  # noqa: E402


def _all_stories_under(node: StoryNode) -> List[Story]:
    out: List[Story] = []

    def _walk(n: StoryNode) -> None:
        if isinstance(n, Story):
            out.append(n)
        for c in n.children:
            _walk(c)

    _walk(node)
    return out


class ScaleStoryMapByDomainScanner(StoryScanner):
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        if isinstance(node, SubEpic):
            violation = self._check_sub_epic_domain_spread(node)
            if violation:
                violations.append(violation)

        if isinstance(node, Story):
            violation = self._check_story_ac_domain_crossing(node)
            if violation:
                violations.append(violation)

        return violations

    def _check_sub_epic_domain_spread(self, node: SubEpic) -> Dict[str, Any] | None:
        stories = _all_stories_under(node)
        if len(stories) < 8:
            return None

        domain_concepts = self._collect_domain_concepts_from_stories(stories)
        if len(domain_concepts) < 3:
            return None

        return Violation(
            rule=self.rule,
            violation_message=(
                f'Sub-epic "{node.name}" references {len(domain_concepts)} domain '
                f"concepts across {len(stories)} stories — consider breaking out "
                f'by domain (scale_story_map_by_domain). '
                f"Concepts: {', '.join(sorted(domain_concepts)[:5])}"
            ),
            location=node.map_location(),
            severity="warning",
        ).to_dict()

    def _check_story_ac_domain_crossing(self, node: Story) -> Dict[str, Any] | None:
        ac_list = node.data.get("acceptance_criteria", [])
        if len(ac_list) < 2:
            return None

        all_concepts: Set[str] = set()
        for ac in ac_list:
            if isinstance(ac, str):
                text = ac
            else:
                text = ac.get("name", "") or ac.get("text", "")
            concepts = self._extract_domain_keywords(text)
            all_concepts.update(concepts)

        if len(all_concepts) >= 3:
            return Violation(
                rule=self.rule,
                violation_message=(
                    f'Story "{node.name}" AC references {len(all_concepts)} '
                    f"distinct domain concepts — consider splitting by domain. "
                    f"Concepts: {', '.join(sorted(all_concepts)[:5])}"
                ),
                location=node.map_location("acceptance_criteria"),
                severity="warning",
            ).to_dict()

        return None

    def _collect_domain_concepts_from_stories(self, stories: List[Story]) -> Set[str]:
        concepts: Set[str] = set()
        for story in stories:
            ac_list = story.data.get("acceptance_criteria", [])
            for ac in ac_list:
                if isinstance(ac, str):
                    text = ac
                else:
                    text = ac.get("name", "") or ac.get("text", "")
                concepts.update(self._extract_domain_keywords(text))
        return concepts

    def _extract_domain_keywords(self, text: str) -> Set[str]:
        keywords = {
            "epic",
            "sub-epic",
            "story",
            "actor",
            "increment",
            "acceptance criteria",
            "scenario",
            "layout",
            "diagram",
        }
        found: Set[str] = set()
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                found.add(kw)
        return found


if __name__ == "__main__":
    sys.exit(main_with_scanner(ScaleStoryMapByDomainScanner, rule_md_name="scale-story-map-by-domain"))
