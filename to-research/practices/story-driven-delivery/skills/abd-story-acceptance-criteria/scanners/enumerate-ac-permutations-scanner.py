#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/enumerate_ac_permutations_scanner.py` (stub; parity with bot)."""
from __future__ import annotations

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
from story_map import StoryNode  # noqa: E402
from story_scanner import StoryScanner  # noqa: E402


class EnumerateACPermutationsScanner(StoryScanner):
    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        return []


if __name__ == "__main__":
    sys.exit(main_with_scanner(EnumerateACPermutationsScanner, rule_md_name="enumerate-all-ac-permutations"))
