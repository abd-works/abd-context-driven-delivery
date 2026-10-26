"""What a BDD spec file's source says about itself — read by the BDD model when it loads facts."""

from __future__ import annotations

import re
from pathlib import Path

_SPEC_SUFFIXES = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".java")
_SIGNATURE_MARKERS = ("# BDD: SIGNATURE", "// BDD: SIGNATURE")
_CODE_LIKE_NAME = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b")
_BLOCK_CALL = re.compile(r"\b(?:describe|description|context|it)\(")


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


def code_like_describe_lines(text: str) -> list[int]:
    """Lines whose describe / context / it text reads like a CamelCase identifier, not plain English."""
    return [
        line_number
        for line_number, line in enumerate(text.splitlines(), 1)
        if _BLOCK_CALL.search(line) and _CODE_LIKE_NAME.search(line)
    ]
