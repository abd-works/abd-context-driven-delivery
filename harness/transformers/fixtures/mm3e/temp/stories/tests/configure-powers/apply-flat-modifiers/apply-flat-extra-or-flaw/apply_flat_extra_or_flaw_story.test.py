"""
Story: Apply Flat Extra or Flaw (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_flat_extra_or_flaw_test_helper.{tier}.py implements ApplyFlatExtraOrFlawHelper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyFlatExtraOrFlawHelper(Protocol):
    ...


def create_apply_flat_extra_or_flaw_story(h: "ApplyFlatExtraOrFlawHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
