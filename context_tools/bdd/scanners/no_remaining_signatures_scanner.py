"""Scanner: `no-remaining-signatures` — development files finish every marker.

Rule: no-remaining-signatures

A completed development-fidelity spec must contain no `BDD: SIGNATURE` markers.
Pure signature files (marker only, no implementation) stay valid behavior
inputs and are skipped. Mixed files — some bodies implemented, some still
marked — fail.

Adapted from abd-skills abd-bdd-development for Python / JS / Java specs.
"""
from __future__ import annotations

import re
from pathlib import Path

from scan import Scanner, ScannerRunner

from bdd_scan_helpers import has_signature_marker, is_spec_file, read_text

RULE = "no-remaining-signatures"

_MARKER = re.compile(r"(?:#|//)\s*BDD:\s*SIGNATURE")
_IMPL_INDICATOR = re.compile(
    r"expect\s*\(|\.to\(|\.toBe\(|\.toEqual\(|assert\w*\s*\(|"
    r"await\s+|const\s+\w+\s*=|mocker\.|unittest\.mock",
    re.IGNORECASE,
)


def _is_pure_signature_file(content: str) -> bool:
    if not has_signature_marker(content):
        return False
    return not bool(_IMPL_INDICATOR.search(content))


class NoRemainingSignaturesScanner(Scanner):
    """Flag leftover signature markers in partially or fully implemented specs."""

    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if not is_spec_file(file_path):
            return []
        content = read_text(file_path)
        if not content or not has_signature_marker(content):
            return []
        if _is_pure_signature_file(content):
            return []

        violations = []
        for i, line in enumerate(content.splitlines(), 1):
            if _MARKER.search(line):
                violations.append(
                    self.violation(
                        '"BDD: SIGNATURE" marker found in what appears to be a '
                        "completed or mixed test file. Implement the test body and "
                        "remove the marker.",
                        location=str(file_path),
                        line=i,
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            NoRemainingSignaturesScanner,
            RULE,
            lambda root: sorted(p for p in root.rglob("*") if p.is_file()),
        )
    )
