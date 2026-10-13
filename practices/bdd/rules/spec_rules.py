"""BDD spec rules ported from practices/bdd/scanners (repo history)."""

from __future__ import annotations

import re
from pathlib import Path

from harness.graph.practice_rule import PracticeGraphRule

from practices.bdd.rules._spec_helpers import (
    has_signature_marker,
    is_spec_file,
    plain_english_violations,
)
from practices.bdd.rules.observable_behavior import ObservableBehavior

_EXPECT_PRIVATE = re.compile(r"(?:expect\s*\([^)]*\._\w+|expect\([^)]*\)\.to\([^)]*\._\w+)")
_DIRECT_PRIVATE = re.compile(
    r"(?:result|output|instance|obj|subject|sut|actual|entity|self\.\w+)\s*\.\s*_\w+"
)


class PlainEnglishOnly(PracticeGraphRule):
    slug = "describe-is-plain-english"
    node_types = ("Description", "Context", "Spec")

    def check(self, node, context) -> list[str]:
        return _spec_file_check(node, context, plain_english_violations)


class SignatureMarkers(PracticeGraphRule):
    slug = "framework-syntax"
    node_types = ("Spec",)

    def check(self, node, context) -> list[str]:
        text = _read_spec(node, context)
        if not text:
            return []
        if has_signature_marker(text):
            return []
        return ["Spec file is missing a BDD: SIGNATURE marker."]


class BusinessReadableLanguage(PracticeGraphRule):
    slug = "observable-behavior"
    node_types = ("Description", "Context")

    def check(self, node, context) -> list[str]:
        text = _read_spec(node, context)
        if not text:
            return []
        for index, line in enumerate(text.splitlines(), 1):
            if _EXPECT_PRIVATE.search(line):
                return [f"Line {index}: assertion should target observable behavior, not private state."]
            if _DIRECT_PRIVATE.search(line):
                return [f"Line {index}: probe reads private state."]
        return []


def _read_spec(node, context) -> str:
    if not node.source.file or context.source_root is None:
        return context.span(node)
    path = context.source_root / node.source.file
    if path.is_file() and is_spec_file(path):
        return path.read_text(encoding="utf-8")
    return context.span(node)


def _spec_file_check(node, context, fn) -> list[str]:
    text = _read_spec(node, context)
    if not text.strip():
        return []
    return fn(text)


# observable-behavior on Spec nodes uses ObservableBehavior from sibling module

SPEC_RULES: tuple[PracticeGraphRule, ...] = (
    ObservableBehavior(),
    PlainEnglishOnly(),
    SignatureMarkers(),
    BusinessReadableLanguage(),
)
