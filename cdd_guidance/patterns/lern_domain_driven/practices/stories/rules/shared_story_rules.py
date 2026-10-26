"""LERN shared-story rules that read the `*.story.shared.ts` text."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_CTX_CAST = re.compile(r"\bctx\.(\w+)\s+as\s+\w+")
_GIVEN_START = re.compile(r"\bgiven\s*\(\s*(['\"`])(.*?)\1\s*,")
_EXPECT = re.compile(r"\b(?:expect|assert)\s*\(")
_TOP_LEVEL_HELPER = re.compile(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)|^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\(", re.M)
_TOP_LEVEL_END = re.compile(r"^\};?\s*$", re.M)
_DOMAIN_CALL = re.compile(r"\brepositories\.\w+(?:\.\w+)?")
_HAND_WRITTEN_ROW = re.compile(r"\bscenario\(\s*(['\"])(?P<outline>[^'\"]+?):\s+(?P<row>[^'\"]+)\1")


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


class DomainOperationsInlineInSteps(PracticeGraphRule):
    """A story-file helper that reaches the repositories hides the domain operation its steps run."""

    slug = "domain-operations-inline-in-steps"
    node_types = ("StoryShared", "DomainSpec", "ServerSpec", "PlaywrightSpec")

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        messages: list[str] = []
        for match in _TOP_LEVEL_HELPER.finditer(text):
            end = _TOP_LEVEL_END.search(text, match.end())
            body = text[match.end():end.start() if end else len(text)]
            calls = sorted(set(_DOMAIN_CALL.findall(body)))
            if not calls:
                continue
            messages.append(
                f"{node.source.file}:{_line_of(text, match.start())}: `{match.group(1) or match.group(2)}` wraps "
                f"domain operations ({', '.join(calls)}); call them in the step that relies on them, or seed the "
                f"state with a fixture in the examples file."
            )
        return messages


class OutlineRowsLoopOverExamples(PracticeGraphRule):
    """`scenario('Outline: row', …)` with a fixed string is one outline row written by hand."""

    slug = "outline-rows-loop-over-examples"
    node_types = ("StoryShared", "PlaywrightSpec")

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        return [
            f"{node.source.file}:{_line_of(text, match.start())}: scenario {match.group('outline')!r} row "
            f"{match.group('row')!r} is written by hand; loop over the outline's examples export instead."
            for match in _HAND_WRITTEN_ROW.finditer(text)
        ]


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
