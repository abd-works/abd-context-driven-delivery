#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/channel_specific_language_scanner.py`."""
from __future__ import annotations

import re
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


class ChannelSpecificLanguageScanner(StoryScanner):
    _GENERIC_BOT = re.compile(r"\b(WHEN|THEN|AND)\s+Bot\s", re.IGNORECASE)
    _GENERIC_USER_COMMAND = re.compile(r"WHEN\s+User\s+enters\s+command", re.IGNORECASE)
    _GENERIC_PANEL = re.compile(r"WHEN\s+User\s+.*\s+in\s+panel", re.IGNORECASE)

    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        acceptance_criteria = node.data.get("acceptance_criteria", [])
        for idx, ac in enumerate(acceptance_criteria):
            text = self._get_ac_text(ac)
            if not text.strip():
                continue
            msg = self._check_text(text)
            if msg:
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

    def _has_concrete_cue(self, text: str) -> bool:
        t = text
        return (
            "cli." in t
            or "(Example" in t
            or "(example" in t
            or "`cli." in t
            or "Panel shows" in t
            or '"' in t
            or "createChild" in t
            or "story_graph" in t
        )

    def _check_text(self, text: str) -> Optional[str]:
        if self._GENERIC_BOT.search(text) and not self._has_concrete_cue(text):
            return (
                'Uses generic "Bot …" steps; prefer concrete API/CLI/Panel examples '
                "(e.g. method calls, cli.… dot paths, or quoted UI labels)."
            )
        if self._GENERIC_USER_COMMAND.search(text) and "cli." not in text:
            return 'Describes CLI by "enters command" without example cli. path or syntax.'
        if self._GENERIC_PANEL.search(text) and '"' not in text and "Panel shows" not in text:
            return 'Panel interaction without quoted control name or explicit "Panel shows …" detail.'
        return None


if __name__ == "__main__":
    sys.exit(main_with_scanner(ChannelSpecificLanguageScanner, rule_md_name="use-channel-specific-language"))
