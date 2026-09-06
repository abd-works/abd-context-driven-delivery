#!/usr/bin/env python3
"""Heuristic checks for *markdown italics* marking domain-significant phrases in scenario text.

Combines each scenario's name plus Background and step lines (``all_steps``). Plain Gherkin
without asterisks is not flagged unless the block is long — see
``MIN_WORDS_BEFORE_MISSING_ITALIC`` — same bar as acceptance-criteria emphasis.
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

MIN_WORDS_BEFORE_MISSING_ITALIC = 22
MAX_ITALIC_WORD_RATIO = 0.48
MIN_WORDS_FOR_RATIO_CHECK = 10
MAX_WORDS_PER_ITALIC_SPAN = 12
MIN_WORDS_IN_SPAN_WITH_PERIOD = 8


class ScenarioDomainTermEmphasisScanner(StoryScanner):
    _BOLD = re.compile(r"\*\*[^*]+\*\*")
    _ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")

    def scan_story_node(self, node: Any) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        for scenario in node.scenarios:
            parts: List[str] = []
            name = (scenario.name or "").strip()
            if name:
                parts.append(name)
            for line in scenario.all_steps:
                s = (line or "").strip()
                if s:
                    parts.append(s)
            text = "\n".join(parts)
            if not text.strip():
                continue
            label = name or f"#{scenario.scenario_idx + 1}"
            for msg in self._messages_for_text(text):
                loc = scenario.map_location("steps")
                violations.append(
                    Violation(
                        rule=self.rule,
                        violation_message=(
                            f'Story "{node.name}" scenario {scenario.scenario_idx + 1} ({label!r}): {msg}'
                        ),
                        location=loc,
                        severity="warning",
                    ).to_dict()
                )
        return violations

    def _messages_for_text(self, text: str) -> List[str]:
        msgs: List[str] = []
        t = self._BOLD.sub(" ", text)
        spans = [m.group(1).strip() for m in self._ITALIC.finditer(t) if m.group(1).strip()]
        total_words = self._word_count(t)

        if total_words >= MIN_WORDS_BEFORE_MISSING_ITALIC and not spans:
            msgs.append(
                "many words but no *italic* domain phrases; consider emphasizing domain terms "
                "(see Emphasize domain-significant terms in scenarios)."
            )

        if spans:
            italic_words = sum(self._word_count(s) for s in spans)
            if total_words >= MIN_WORDS_FOR_RATIO_CHECK and italic_words / total_words > MAX_ITALIC_WORD_RATIO:
                msgs.append(
                    f"italic spans cover a large share of the text (~{italic_words}/{total_words} words); "
                    "risk of over-emphasis — mark domain terms only."
                )

            for span in spans:
                wc = self._word_count(span)
                if wc > MAX_WORDS_PER_ITALIC_SPAN:
                    msgs.append(
                        f"italic span is long ({wc} words); prefer shorter domain phrases, not whole sentences."
                    )
                elif wc >= MIN_WORDS_IN_SPAN_WITH_PERIOD and ". " in span:
                    msgs.append(
                        "italic span contains sentence-style punctuation; split into shorter domain phrases."
                    )
        return msgs

    @staticmethod
    def _word_count(s: str) -> int:
        return len([w for w in re.split(r"\s+", s.strip()) if w])


if __name__ == "__main__":
    sys.exit(
        main_with_scanner(
            ScenarioDomainTermEmphasisScanner,
            rule_md_name="emphasize-domain-significant-terms-scenarios",
        )
    )
