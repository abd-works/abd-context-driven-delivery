"""From practices/bdd/scanners/bdd_scan_helpers.py (in-repo history)."""

from __future__ import annotations

import re
from pathlib import Path

_SPEC_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".java")
_SIGNATURE_MARKERS = ("# BDD: SIGNATURE", "// BDD: SIGNATURE")


def is_spec_file(path: Path) -> bool:
    name = path.name.lower()
    if path.suffix.lower() not in _SPEC_SUFFIXES:
        return False
    return (
        name.endswith("_spec.py")
        or "_spec." in name
        or ".test." in name
        or ".spec." in name
        or name.endswith("test.java")
        or name.endswith("tests.java")
    )


def has_signature_marker(text: str) -> bool:
    return any(marker in text for marker in _SIGNATURE_MARKERS)


def plain_english_violations(text: str) -> list[str]:
    hits: list[str] = []
    for index, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if "describe(" in stripped or "context(" in stripped or "it(" in stripped:
            if re.search(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", stripped):
                hits.append(f"Line {index}: describe/it text looks like code, not plain English.")
    return hits[:1]
