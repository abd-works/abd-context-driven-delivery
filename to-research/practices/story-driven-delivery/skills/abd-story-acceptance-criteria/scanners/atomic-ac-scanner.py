#!/usr/bin/env python3
"""Migrated from agile_bots `src/scanners/atomic_ac_scanner.py`."""
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
from scanner_bases.violation import Violation  # noqa: E402
from story_map import Story, StoryNode  # noqa: E402
from story_scanner import StoryScanner  # noqa: E402


class AtomicACScanner(StoryScanner):
    """Flags pairs of AC that share a long identical prefix (likely repeated base logic)."""

    _PREFIX_LINES = 4

    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        acceptance_criteria = node.data.get("acceptance_criteria", [])
        texts = [self._get_ac_text(ac) for ac in acceptance_criteria]
        texts = [t for t in texts if t.strip()]
        if len(texts) < 2:
            return violations

        seen_pairs = set()
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                prefix_i = self._line_prefix(texts[i])
                prefix_j = self._line_prefix(texts[j])
                k = min(len(prefix_i), len(prefix_j), self._PREFIX_LINES)
                if k < 3:
                    continue
                if prefix_i[:k] == prefix_j[:k]:
                    pair = (i, j)
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    loc = node.map_location(f"acceptance_criteria[{i}]")
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f'Story "{node.name}": AC #{i + 1} and AC #{j + 1} share the same first {k} step(s); '
                                f"state the general case once and let variations only describe what differs."
                            ),
                            location=loc,
                            severity="warning",
                        ).to_dict()
                    )
        return violations

    def _line_prefix(self, text: str) -> List[str]:
        return [ln.strip().lower() for ln in text.splitlines() if ln.strip()]


if __name__ == "__main__":
    sys.exit(main_with_scanner(AtomicACScanner, rule_md_name="use-atomic-acceptance-criteria"))
