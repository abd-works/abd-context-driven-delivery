#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/reaction_chaining_scanner.py`; uses `_get_ac_text` for dict AC."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

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


class ReactionChainingScanner(StoryScanner):
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        if isinstance(node, Story):
            acceptance_criteria = node.data.get("acceptance_criteria", [])

            for idx, ac in enumerate(acceptance_criteria):
                text = self._get_ac_text(ac)
                if not text.strip():
                    continue

                violation = self._check_reaction_chaining(text, node, idx)
                if violation:
                    violations.append(violation)

        return violations

    def _check_reaction_chaining(self, ac: str, story: Story, ac_index: int) -> Optional[Dict[str, Any]]:
        lines = [line.strip() for line in ac.split("\n") if line.strip()]

        if len(lines) < 2:
            return None

        for i in range(len(lines) - 1):
            current_line = lines[i].lower()
            next_line = lines[i + 1].lower()

            if current_line.startswith("then ") and self._is_system_action(current_line):
                if next_line.startswith("when ") and self._is_system_action(next_line):
                    location = story.map_location(f"acceptance_criteria[{ac_index}]")
                    return Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Story "{story.name}" AC #{ac_index + 1} has separate WHEN/THEN for sequential system '
                            f"actions (should use AND to chain reactions)"
                        ),
                        location=location,
                        severity="warning",
                    ).to_dict()

        and_chain_count = 0
        for line in lines:
            line_lower = line.lower()
            if line_lower.startswith("and "):
                and_chain_count += 1
                if and_chain_count > 4:
                    location = story.map_location(f"acceptance_criteria[{ac_index}]")
                    return Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Story "{story.name}" AC #{ac_index + 1} has excessive And chain ({and_chain_count} '
                            f"reactions, should be max 4)"
                        ),
                        location=location,
                        severity="warning",
                    ).to_dict()
            else:
                and_chain_count = 0

        return None

    def _is_system_action(self, line: str) -> bool:
        line_lower = line.lower()

        for keyword in ["when ", "then ", "and ", "given "]:
            if line_lower.startswith(keyword):
                line_lower = line_lower[len(keyword) :].strip()
                break

        system_keywords = [
            "system ",
            "bot ",
            "application ",
            "server ",
            "workflow ",
            "action ",
            "behavior ",
        ]
        return any(keyword in line_lower for keyword in system_keywords)


if __name__ == "__main__":
    sys.exit(main_with_scanner(ReactionChainingScanner, rule_md_name="use-and-for-multiple-reactions"))
