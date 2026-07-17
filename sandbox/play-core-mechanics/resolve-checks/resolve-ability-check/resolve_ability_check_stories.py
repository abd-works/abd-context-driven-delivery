"""
# @toolset-manifest python -m tools manifest stories.stories:Stories
"""

"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


RESOLVE_ABILITY_CHECK: Final = {
    "story": "Resolve Ability Check",
    "actor": "Player",
    "domain_terms": (
        "Character",
        "Ability",
        "Trait",
        "Check",
        "DifficultyClass",
        "CheckResult",
    ),
    "evidence": (
        "sandbox/checks/.context/module-context.md",
        "sandbox/character/.context/module-context.md",
        "exploration example: strength rank=5, face=8, DC=10 -> total=13, succeeded, degree=1",
    ),
    "main_flow": {
        "name": "ability check reports die total degree and success",
        "given": (
            "a Character with Ability {ability_name} at rank {ability_rank} usable as a Trait",
            "And a DifficultyClass with target {difficulty_target}",
            "And dice that will roll face {die_face}",
        ),
        "interactions": (
            {
                "when": (
                    "the Player resolves a Check on that Ability",
                ),
                "then": (
                    "Check die_roll equals {die_face}",
                    "And CheckResult total equals {expected_total}",
                    "And CheckResult succeeded is {succeeded}",
                    "And CheckResult degree is {degree}",
                ),
            },
        ),
        "examples": (
            {
                "ability_name": "strength",
                "ability_rank": "5",
                "difficulty_target": "10",
                "die_face": "8",
                "expected_total": "13",
                "succeeded": "true",
                "degree": "1",
            },
        ),
    },
}
