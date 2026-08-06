# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Runnable story (scenario fidelity - tier-neutral). Calls helper-protocol
# methods only - no assertions, no tier mechanism here.
#
#   Folder tree   -> {epic-verb-noun}/{sub-epic-verb-noun}/{story-verb-noun}/
#   Story file    -> {story_verb_noun}_story.py
#   Tier files    -> {story_verb_noun}_test_helper.{tier}.py
#                    (tier in domain | client | server | e2e | project-specific)

"""Story: {Story Name} (scenario fidelity - tier-neutral)."""

from __future__ import annotations

from typing import Protocol


class {EpicVerbNoun}Helper(Protocol):
    def given_precondition(self) -> None: ...
    def when_action(self) -> None: ...
    def then_outcome(self) -> None: ...


def create_{story_verb_noun}_story(h: "{EpicVerbNoun}Helper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn}
    for the tier file to bind at module scope.
    """
    tests = {}

    def test_main_flow_observable_outcome() -> None:
        """SCENARIO: {main-flow outcome}"""
        h.given_precondition()
        h.when_action()
        h.then_outcome()

    tests["test_main_flow_observable_outcome"] = test_main_flow_observable_outcome
    return tests
