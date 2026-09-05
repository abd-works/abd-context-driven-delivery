#!/usr/bin/env python3
"""Flag Scenario Outline Then/And steps that lack any assertable value.

A Then step in an outline must contain at least one of:
  - A {token} referencing an example table column
  - A *italic* concrete value
  - A "quoted" literal string

Steps with none of these are describing behavior abstractly without any
value to assert on — making the scenario untestable.
"""
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
from story_map import Story  # noqa: E402
from story_scanner import StoryScanner  # noqa: E402

TOKEN_RE = re.compile(r"\{[^}]+\}")
ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
QUOTED_RE = re.compile(r'"[^"]+"')

THEN_KEYWORDS = ("then", "and", "but")

NAVIGATION_VERBS = (
    "navigates to",
    "returns to",
    "remains on",
    "advances to",
    "does not allow",
    "is disabled",
    "is enabled",
)


def _is_then_or_continuation(step: str) -> bool:
    """Check if step is a Then, And (after Then), or But (after Then)."""
    lower = step.strip().lower()
    return lower.startswith("then ") or lower.startswith("and ") or lower.startswith("but ")


def _has_assertable_value(step: str) -> bool:
    """Check if step contains at least one assertable value."""
    if TOKEN_RE.search(step):
        return True
    if ITALIC_RE.search(step):
        return True
    if QUOTED_RE.search(step):
        return True
    return False


def _is_navigation_only(step: str) -> bool:
    """Navigation steps (screen transitions) don't need value assertions."""
    lower = step.lower()
    return any(verb in lower for verb in NAVIGATION_VERBS)


class ThenAssertsConcreteOutputScanner(StoryScanner):

    def scan_story_node(self, node: Any) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        for scenario in node.scenarios:
            if not scenario.has_examples:
                continue

            in_then_block = False
            for step in scenario.steps:
                stripped = step.strip()
                lower = stripped.lower()

                if lower.startswith("then "):
                    in_then_block = True
                elif lower.startswith("when ") or lower.startswith("given "):
                    in_then_block = False
                    continue

                if not in_then_block:
                    continue

                if not _is_then_or_continuation(stripped):
                    continue

                if _is_navigation_only(stripped):
                    continue

                if not _has_assertable_value(stripped):
                    loc = scenario.map_location("steps") if hasattr(scenario, "map_location") else None
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f'Story "{node.name}" outline "{scenario.name}": '
                                f'Then/And step has no assertable value '
                                f'(no {{token}}, no *italic*, no "quoted" literal): '
                                f'"{stripped}"'
                            ),
                            location=loc,
                            severity="warning",
                        ).to_dict()
                    )
        return violations


if __name__ == "__main__":
    sys.exit(
        main_with_scanner(
            ThenAssertsConcreteOutputScanner,
            rule_md_name="then-asserts-concrete-output",
        )
    )
