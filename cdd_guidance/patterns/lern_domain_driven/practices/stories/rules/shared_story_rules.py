"""LERN shared-story rules that read the `*.story.shared.ts` text."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_CTX_CAST = re.compile(r"\bctx\.(\w+)\s+as\s+\w+")
_GIVEN_START = re.compile(r"\bgiven\s*\(\s*(['\"`])(.*?)\1\s*,")
_EXPECT = re.compile(r"\b(?:expect|assert)\s*\(")


def _line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


class TierBoundRepositoryAccessor(PracticeGraphRule):
    """Shared stories reach repositories through the accessor each tier binds, not by casting `ctx`."""

    slug = "tier-bound-repository-accessor"
    node_types = ("StoryShared",)

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        return [
            f"{node.source.file}:{_line_of(text, match.start())}: `{match.group(0)}` casts the story context; "
            f"read the repository through the tier-bound `repositories` accessor."
            for match in _CTX_CAST.finditer(text)
        ]


class NoExpectInGiven(PracticeGraphRule):
    """A Given sets up state; checking it is a Then's job."""

    slug = "no-expect-in-given"
    node_types = ("StoryShared",)

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        messages: list[str] = []
        for match in _GIVEN_START.finditer(text):
            body = _callback_body(text, match.end())
            if body is not None and _EXPECT.search(body):
                messages.append(
                    f"{node.source.file}:{_line_of(text, match.start())}: Given {match.group(2)!r} asserts; "
                    f"move the check to a Then or drop it."
                )
        return messages


def _callback_body(text: str, start: int) -> str | None:
    """The `{ … }` body of the arrow function that starts at or after ``start``."""
    open_brace = text.find("{", start)
    arrow = text.find("=>", start)
    if open_brace == -1 or arrow == -1 or arrow > open_brace:
        return None
    depth = 0
    for index in range(open_brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace + 1:index]
    return None
