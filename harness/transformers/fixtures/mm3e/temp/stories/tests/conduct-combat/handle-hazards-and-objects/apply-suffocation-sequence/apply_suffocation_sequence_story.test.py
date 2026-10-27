"""
Story: Apply Suffocation Sequence (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_suffocation_sequence_test_helper.{tier}.py implements ApplySuffocationSequenceHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplySuffocationSequenceHelper(Protocol):
    ...


def create_apply_suffocation_sequence_story(h: "ApplySuffocationSequenceHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
