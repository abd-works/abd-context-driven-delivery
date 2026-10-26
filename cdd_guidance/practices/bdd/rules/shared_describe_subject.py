"""shared-describe-subject — one outermost describe per domain subject."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_MIN_SHARED_WORDS = 2
_BRANCH_SUFFIX = re.compile(r"^(registered|with|that)\b", re.I)


def _longest_shared_word_prefix(left: str, right: str) -> tuple[str, str, str] | None:
    left_words = left.split()
    right_words = right.split()
    shared: list[str] = []
    for left_word, right_word in zip(left_words, right_words):
        if left_word != right_word:
            break
        shared.append(left_word)
    if len(shared) < _MIN_SHARED_WORDS:
        return None
    suffix_left = " ".join(left_words[len(shared) :])
    suffix_right = " ".join(right_words[len(shared) :])
    if not suffix_left or not suffix_right:
        return None
    if not (
        _BRANCH_SUFFIX.match(suffix_left)
        or _BRANCH_SUFFIX.match(suffix_right)
    ):
        return None
    return (" ".join(shared), suffix_left, suffix_right)


def branched_top_level_describes(names: list[str]) -> list[str]:
    messages: list[str] = []
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            split = _longest_shared_word_prefix(left, right)
            if split is None:
                continue
            subject, suffix_left, suffix_right = split
            messages.append(
                "Top-level describes "
                f"{left!r} and {right!r} share subject {subject!r}; "
                "use one describe and nest "
                f"with {suffix_left!r} and with {suffix_right!r} as sibling contexts."
            )
    return messages


class SharedDescribeSubject(PracticeGraphRule):
    slug = "shared-describe-subject"
    node_types = ("Spec",)

    def check(self, node, context) -> list[str]:
        return branched_top_level_describes(node.get_fact("top_level_describes", []))[:5]
