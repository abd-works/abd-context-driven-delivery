#!/usr/bin/env python3
"""Flag sentiment-based bullet points in a mechanism's Rules section.

Every rule in a mechanism context file must be a falsifiable code-level
constraint — something a reviewer can confirm or refute by reading source code.
Sentiment words ("prefer", "strive", "aim", "good idea", "consider", "properly",
"where possible") signal that the author has written an aspiration, not a rule.

Only mechanism context files (identified by having a ## Participants section)
are scanned. Package context files do not have a Rules section in the same sense.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

_ROOT = Path(__file__).resolve().parent.parent
_REPO = _ROOT.parent.parent.parent.parent
for _p in (
    _REPO / "common" / "scripts",
    _ROOT / "scanners",
):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

from scanner_runner import execute_scan_with_workspace  # noqa: E402
from scanner_bases import Scanner, Violation  # noqa: E402
from scanner_bases.resources.scan_context import FileScanContext  # noqa: E402
from arch_spec_context import build_arch_spec_context, is_mechanism_context, extract_section  # noqa: E402

# Sentiment words that indicate a rule cannot be falsified by reading code.
_SENTIMENT_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\bprefer\b", re.IGNORECASE),          "use 'must' or 'must not' instead of 'prefer'"),
    (re.compile(r"\bstrive\b", re.IGNORECASE),           "use 'must' or 'must not' instead of 'strive'"),
    (re.compile(r"\baim\s+for\b", re.IGNORECASE),        "use 'must' or 'must not' instead of 'aim for'"),
    (re.compile(r"\bavoid\s+where\s+possible\b", re.IGNORECASE), "state the concrete prohibition instead"),
    (re.compile(r"\bwhere\s+possible\b", re.IGNORECASE), "state the concrete prohibition instead"),
    (re.compile(r"\bwhenever\s+possible\b", re.IGNORECASE), "state the concrete rule instead"),
    (re.compile(r"\bgood\s+idea\b", re.IGNORECASE),      "name the specific code violation instead"),
    (re.compile(r"\bconsider\b", re.IGNORECASE),         "use 'must' or 'must not'; 'consider' is optional and not reviewable"),
    (re.compile(r"\bshould\s+be\s+easy\b", re.IGNORECASE), "name a measurable, code-visible property instead"),
    (re.compile(r"\bproper(?:ly)?\b", re.IGNORECASE),    "define 'proper' as a specific, code-checkable property"),
    (re.compile(r"\bappropriate(?:ly)?\b", re.IGNORECASE), "define 'appropriate' as a specific, code-checkable property"),
    (re.compile(r"\bclean\b", re.IGNORECASE),            "name the specific code violation ('clean' is subjective)"),
    (re.compile(r"\breadab(?:le|ility)\b", re.IGNORECASE), "name the specific code property instead of 'readable'"),
    (re.compile(r"\bmake\s+sure\b", re.IGNORECASE),      "state the concrete rule as a must/must-not"),
    (re.compile(r"\bensure\b", re.IGNORECASE),           "state the concrete rule as a must/must-not (avoid 'ensure')"),
    (re.compile(r"\btry\s+to\b", re.IGNORECASE),         "use 'must' or 'must not'; 'try to' is not reviewable"),
    (re.compile(r"\bfollow\s+solid\b", re.IGNORECASE),   "SOLID is generic; name the specific constraint for this mechanism"),
    (re.compile(r"\bfollow\s+best\s+practices\b", re.IGNORECASE), "name the specific constraint instead of 'best practices'"),
]

# A bullet line starts with optional whitespace then - or * or a number.
_BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.+)$")


class MechanismRulesCodeVerifiableScanner(Scanner):

    def scan_file_with_context(self, context: FileScanContext) -> List[dict]:
        if not context.exists:
            return []
        text = context.file_path.read_text(encoding="utf-8")
        if not is_mechanism_context(text):
            return []

        rules_section = extract_section(text, "Rules")
        if not rules_section:
            return []

        violations: List[dict] = []
        for line in rules_section.splitlines():
            m = _BULLET_RE.match(line)
            if not m:
                continue
            bullet_text = m.group(1)
            for pattern, hint in _SENTIMENT_PATTERNS:
                hit = pattern.search(bullet_text)
                if hit:
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f"Mechanism rule in '{context.file_path.parent.name}' "
                                f"uses sentiment language ('{hit.group(0)}'): {hint}. "
                                f"Rule: \"{bullet_text[:120]}\""
                            ),
                            location=str(context.file_path),
                            severity="warning",
                        ).to_dict()
                    )
                    break  # one report per bullet is enough
        return violations


if __name__ == "__main__":
    sys.exit(
        execute_scan_with_workspace(
            MechanismRulesCodeVerifiableScanner,
            "mechanism-rules-are-code-verifiable",
            build_arch_spec_context,
            skill_root=_ROOT,
        )
    )
