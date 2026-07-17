"""
# @toolset-manifest python -m tools manifest stories.stories:Stories
"""

"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


CREATE_CHARACTER: Final = {
    "story": "Create Character",
    "actor": "Player",
    "domain_terms": ("Character", "Abilities", "Ability", "Rank"),
    "evidence": (
        "sandbox/character/.context/module-context.md",
        "exploration example: all eight Abilities at rank 0",
    ),
    "main_flow": {
        "name": "new character has handbook abilities at rank zero",
        "given": ("no Character yet",),
        "interactions": (
            {
                "when": ("the Player creates a Character",),
                "then": (
                    "a Character exists with Abilities",
                    "And each of the eight Abilities has rank 0",
                ),
            },
        ),
    },
}
