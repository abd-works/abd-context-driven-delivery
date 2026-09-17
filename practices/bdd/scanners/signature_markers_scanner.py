"""Scanner: `signature-markers` — behavior-fidelity it bodies are marker-only.

Rule: signature-markers

A signature file (any file containing `BDD: SIGNATURE`) must keep every `it`
body as exactly that marker — no assertions, no setup, no production imports.
Supports Mamba (`# BDD: SIGNATURE`), Jest (`// BDD: SIGNATURE`), and JUnit.

Adapted from abd-skills abd-bdd-specification (JS-only) to the multi-language
context-tool templates.
"""
from __future__ import annotations

import re
from pathlib import Path

from scan import Scanner, ScannerRunner

from bdd_scan_helpers import (
    extract_it_blocks,
    has_signature_marker,
    is_spec_file,
    read_text,
)

RULE = "signature-markers"

_MARKER_RE = re.compile(r"(?:#|//)\s*BDD:\s*SIGNATURE")
_IMPL_PATTERNS = re.compile(
    r"expect\s*\(|\.to\(|\.toBe\(|\.toEqual\(|\.toHaveBeenCalled|"
    r"assert\w*\s*\(|await\s+|const\s+\w+\s*=|let\s+\w+\s*=|"
    r"^\s*(?:self\.)?\w+\s*=|return\s+\w|mocker\.|unittest\.mock|"
    r"jest\.|vi\.|sinon\.",
    re.IGNORECASE | re.MULTILINE,
)


class SignatureMarkersScanner(Scanner):
    """Flag signature-file it bodies that lack the marker or add implementation."""

    RULE = RULE

    def scan_file(self, root: Path, file_path: Path) -> list:
        if not is_spec_file(file_path):
            return []
        content = read_text(file_path)
        if not content or not has_signature_marker(content):
            return []

        violations = []
        for lineno, label, body in extract_it_blocks(file_path, content):
            has_marker = bool(_MARKER_RE.search(body))
            stripped = "\n".join(
                line
                for line in body.splitlines()
                if line.strip() and not _MARKER_RE.search(line)
            )
            has_impl = bool(_IMPL_PATTERNS.search(stripped)) if stripped.strip() else False

            if not has_marker:
                violations.append(
                    self.violation(
                        f'it("{label}") body missing "BDD: SIGNATURE" marker. '
                        f"Signature files must contain only the marker — no implementation.",
                        location=str(file_path),
                        line=lineno,
                    )
                )
            elif has_impl:
                violations.append(
                    self.violation(
                        f'it("{label}") body has implementation beyond the marker. '
                        f'Remove all logic — keep only the BDD: SIGNATURE marker.',
                        location=str(file_path),
                        line=lineno,
                    )
                )
        return violations


if __name__ == "__main__":
    raise SystemExit(
        ScannerRunner.run_scanner_main(
            SignatureMarkersScanner,
            RULE,
            lambda root: sorted(p for p in root.rglob("*") if p.is_file()),
        )
    )
