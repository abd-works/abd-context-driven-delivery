"""What a BDD spec file's source says about itself — read by the BDD model when it loads facts."""

from __future__ import annotations

import re

from cdd_guidance.practices.clean_engineering.model.code_body import PYTHON, TYPESCRIPT

# The comment a signature-only test body carries, spelt in each language's own comment.
SIGNATURE = "BDD: SIGNATURE"
_CODE_LIKE_NAME = re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b")
_ASSERTION = re.compile(r"\bexpect\s*\(|\bassert\b")


def has_signature_marker(text: str) -> bool:
    return any(language.comment(SIGNATURE) in text for language in (PYTHON, TYPESCRIPT))


def is_developed(text: str) -> bool:
    """Whether a spec is past behavior and realization fidelity: no `it` still carries a signature marker, and the
    spec asserts. Development replaces each marker with a test body, so a spec with none left and real assertions is a
    finished test, and the rules that keep a behavior sketch free of test bodies no longer apply to it."""
    return not has_signature_marker(text) and _ASSERTION.search(text) is not None


def reads_like_code(label: str) -> bool:
    """Whether a describe's or context's text names a CamelCase identifier rather than reading as plain English."""
    return bool(_CODE_LIKE_NAME.search(label))
