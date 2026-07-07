# ---
# fidelity: [exploration, specification]
# artifact: [story-data]
# format: py
# section: leaf-spec-file
# ---
#
# Pure data only. Regeneratable, bidirectional. The adapter renders freely
# on every run and can parse this file back into the domain StoryMap.
#
# File-naming convention (Python-only exception to kebab folders):
#   Folder tree      -> {epic-verb-noun}/{sub-epic-verb-noun}/{lowest-sub-epic}/
#   Leaf spec file   -> {lowest_sub_epic}_stories.py       (snake — module import)
#   Tier file        -> {lowest_sub_epic}_<tier>.py        (snake — module import)
#   Tier test file   -> test_{lowest_sub_epic}_<tier>.py   (snake — pytest discovery)
#
# Contents rules:
#   - Module-level constant, one per Story, keyed by SCREAMING_SNAKE.
#   - Story is a plain dict; keys `story`, `actor`, `domain_terms`, `evidence`,
#     then one Scenario per additional key.
#   - Every Scenario has `name`, `given: tuple[str, ...]`, and
#     `interactions: tuple[Interaction, ...]`. Each Interaction has `when` and
#     `then`, both `tuple[str, ...]`.
#   - Step strings are plain prose. First step of each phase is unprefixed;
#     continuations start with `"And "` or `"But "` inside the string.
#   - No imports of test framework, helpers, or production code.
#   - No function definitions, no assertions.

"""Story data for the `{Sub-Epic Name}` sub-epic."""

from __future__ import annotations

from typing import Final


STORY_ONE: Final = {
    "story": "<Story Verb-Noun>",
    "actor": "<Actor>",
    "domain_terms": ("<term>", "<term>"),
    "evidence": ("<source ref>",),

    "main_flow": {
        "name": "<outcome-oriented scenario name>",
        "given": (
            "<precondition>",
            "And <continuation precondition>",
        ),
        "interactions": (
            {
                "when": ("<action>",),
                "then": (
                    "<observable outcome>",
                    "And <continuation outcome>",
                ),
            },
        ),
    },
}
