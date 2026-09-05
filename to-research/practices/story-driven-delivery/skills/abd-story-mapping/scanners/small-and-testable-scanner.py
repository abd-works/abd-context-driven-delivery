#!/usr/bin/env python3
"""Stories should describe outcomes, not low-level implementation operations in the title."""
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


class SmallAndTestableScanner(StoryScanner):
    IMPLEMENTATION_VERBS = [
        "serialize",
        "deserialize",
        "convert",
        "transform",
        "format",
        "calculate",
        "compute",
        "generate",
        "create",
        "apply",
        "set",
        "configure",
        "save",
        "write",
        "store",
    ]

    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []

        if not isinstance(node, Story):
            return violations

        if not hasattr(node, "name") or not node.name:
            return violations

        name_lower = node.name.lower()

        for verb in self.IMPLEMENTATION_VERBS:
            pattern = rf"\b{verb}\b"
            if re.search(pattern, name_lower):
                words = name_lower.split()
                if verb in words[0] or (len(words) > 1 and verb in words[0:2]):
                    violation = Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Story "{node.name}" appears to be an implementation operation — '
                            "should be a step within a story that describes user/system outcome"
                        ),
                        location=node.name,
                        severity="error",
                    ).to_dict()
                    violations.append(violation)
                    break

        return violations


if __name__ == "__main__":
    sys.exit(main_with_scanner(SmallAndTestableScanner, rule_md_name="small-and-testable"))
