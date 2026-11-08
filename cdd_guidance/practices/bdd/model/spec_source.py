"""What a BDD spec file's source says about itself — read by the BDD model when it loads facts."""

from __future__ import annotations

import re
from pathlib import Path

from cdd_guidance.practices.clean_engineering.model.code_body import PYTHON, TYPESCRIPT

# The comment a signature-only test body carries, spelt in each language's own comment.
SIGNATURE = "BDD: SIGNATURE"
_CODE_LIKE_NAME = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b")
_BLOCK_CALL = re.compile(r"\b(?:describe|description|context|it)\(")
_SPEC_NAME_PARTS = ("_spec.", ".test.", ".spec.", ".e2e.")
_JAVA_TEST_ENDINGS = ("test.java", "tests.java")


def is_spec_file(path: Path) -> bool:
    """A file named as a spec or a test. Which extensions are read at all is the practice's formats' to say."""
    name = path.name.lower()
    return any(part in name for part in _SPEC_NAME_PARTS) or name.endswith(_JAVA_TEST_ENDINGS)


def has_signature_marker(text: str) -> bool:
    return any(language.comment(SIGNATURE) in text for language in (PYTHON, TYPESCRIPT))


def code_like_describe_lines(text: str) -> list[int]:
    """Lines whose describe / context / it text reads like a CamelCase identifier, not plain English."""
    return [
        line_number
        for line_number, line in enumerate(text.splitlines(), 1)
        if _BLOCK_CALL.search(line) and _CODE_LIKE_NAME.search(line)
    ]
