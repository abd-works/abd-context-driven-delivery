"""
# @toolset-manifest python -m tools manifest stories.stories:Stories
"""

"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


UPDATE_ABILITY_RANK: Final = {
    "story": "Update Ability Rank",
    "actor": "Player",
    "domain_terms": ("Character", "Ability", "Rank"),
    "evidence": (
        "sandbox/character/.context/module-context.md",
        "exploration example: strength 0 -> 5; PointTotals not asserted",
    ),
    "main_flow": {
        "name": "ability rank changes on the sheet",
        "given": (
            "a Character with Ability {ability_name}",
            "And that Ability has rank {starting_rank}",
        ),
        "interactions": (
            {
                "when": (
                    "the Player updates that Ability rank to {new_rank}",
                ),
                "then": (
                    "that Ability rank equals {new_rank}",
                ),
            },
        ),
        "examples": (
            {
                "ability_name": "strength",
                "starting_rank": "0",
                "new_rank": "5",
            },
        ),
    },
}
