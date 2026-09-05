# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Conceptual story reference. Refer to context_tools/language-tools.md for tooling.
#
#   Folder tree   -> {epic-verb-noun}/{sub-epic-verb-noun}/{story-verb-noun}/
#   Story file    -> {story_verb_noun}_story.py

"""Story: {Story Name} (conceptual reference)."""

from __future__ import annotations
from typing import Protocol


class {EpicVerbNoun}Helper(Protocol):
    def given_precondition(self) -> None: ...
    def when_action(self) -> None: ...
    def then_outcome(self) -> None: ...


def create_{story_verb_noun}_story(h: "{EpicVerbNoun}Helper") -> dict:
    """Build one pytest test function per scenario.
    """
    tests = {}

    def test_main_flow() -> None:
        """SCENARIO: {main-flow outcome}"""
        h.given_precondition()
        h.when_action()
        h.then_outcome()

    tests["test_main_flow"] = test_main_flow
    return tests
