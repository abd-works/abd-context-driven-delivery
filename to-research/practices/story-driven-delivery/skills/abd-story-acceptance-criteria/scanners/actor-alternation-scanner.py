#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/actor_alternation_scanner.py`; uses `_get_ac_text` for dict AC."""
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


class ActorAlternationScanner(StoryScanner):
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        if isinstance(node, Story):
            acceptance_criteria = node.data.get("acceptance_criteria", [])

            for idx, ac in enumerate(acceptance_criteria):
                text = self._get_ac_text(ac)
                if not text.strip():
                    continue

                violation = self._check_actor_alternation(text, node, idx)
                if violation:
                    violations.append(violation)

        return violations

    def _check_actor_alternation(self, ac: str, story: Story, ac_index: int) -> Optional[Dict[str, Any]]:
        lines = ac.split("\n")

        actors: List[str] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            actor = self._extract_actor(line)
            if actor:
                actors.append(actor)

        if len(actors) < 3:
            return None

        consecutive_count = 1
        prev_actor = actors[0]

        for i in range(1, len(actors)):
            current_actor = actors[i]

            if current_actor == prev_actor:
                consecutive_count += 1

                if consecutive_count > 2:
                    location = story.map_location(f"acceptance_criteria[{ac_index}]")
                    return Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Story "{story.name}" AC #{ac_index + 1} has {consecutive_count} consecutive '
                            f"{prev_actor} steps without alternating"
                        ),
                        location=location,
                        severity="warning",
                    ).to_dict()
            else:
                consecutive_count = 1
                prev_actor = current_actor

        return None

    def _extract_actor(self, line: str) -> Optional[str]:
        line_lower = line.lower()

        for keyword in ["when ", "then ", "and ", "given "]:
            if line_lower.startswith(keyword):
                line_lower = line_lower[len(keyword) :].strip()
                break

        if any(
            word in line_lower
            for word in ["user ", "actor ", "customer ", "developer ", "human ", "cli ", "repl "]
        ):
            return "user"
        elif any(
            word in line_lower
            for word in ["system ", "bot ", "application ", "server ", "workflow "]
        ):
            return "system"

        return "system"


if __name__ == "__main__":
    sys.exit(main_with_scanner(ActorAlternationScanner, rule_md_name="alternate-actors-in-steps"))
