#!/usr/bin/env python3
"""Heuristic checks for *markdown italics* marking domain-significant phrases in AC text.

Plain-text AC (no asterisks) is not flagged unless the criterion is very long — see
MIN_WORDS_BEFORE_MISSING_ITALIC — so existing graphs without markdown get fewer hits.
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
from story_map import Story, StoryNode  # noqa: E402
from story_scanner import StoryScanner  # noqa: E402

# AC with this many words but no *italic* spans suggests missing domain emphasis.
MIN_WORDS_BEFORE_MISSING_ITALIC = 22
# More than this fraction of words sitting inside italics → "wall of emphasis" risk.
MAX_ITALIC_WORD_RATIO = 0.48
MIN_WORDS_FOR_RATIO_CHECK = 10
# Italic span longer than this reads like a sentence, not a domain phrase.
MAX_WORDS_PER_ITALIC_SPAN = 12
# If an italic span looks like multiple sentences, nudge the author.
MIN_WORDS_IN_SPAN_WITH_PERIOD = 8


class DomainTermEmphasisScanner(StoryScanner):
    _BOLD = re.compile(r"\*\*[^*]+\*\*")
    # Single-asterisk italics; avoid matching **bold** (handled by stripping bold first).
    _ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")

    def scan_story_node(self, node: StoryNode) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        if not isinstance(node, Story):
            return violations

        acceptance_criteria = node.data.get("acceptance_criteria", [])
        for idx, ac in enumerate(acceptance_criteria):
            text = self._get_ac_text(ac)
            if not text.strip():
                continue
            for msg in self._messages_for_text(text):
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

    def _messages_for_text(self, text: str) -> List[str]:
        msgs: List[str] = []
        t = self._BOLD.sub(" ", text)
        spans = [m.group(1).strip() for m in self._ITALIC.finditer(t) if m.group(1).strip()]
        total_words = self._word_count(t)

        if total_words >= MIN_WORDS_BEFORE_MISSING_ITALIC and not spans:
            msgs.append(
                "many words but no *italic* domain phrases; consider emphasizing domain terms "
                "(see Emphasize domain-significant terms)."
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
            DomainTermEmphasisScanner,
            rule_md_name="emphasize-domain-significant-terms",
        )
    )
