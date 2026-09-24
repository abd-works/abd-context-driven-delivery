"""
Story: Apply Critical Success on Natural 20 (scenario fidelity - tier-neutral).
Actor: System
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: apply_critical_success_on_natural_20_test_helper.{tier}.py implements ApplyCriticalSuccessOnNatural20Helper.
"""

from __future__ import annotations

from typing import Protocol


class ApplyCriticalSuccessOnNatural20Helper(Protocol):
    ...


def create_apply_critical_success_on_natural_20_story(h: "ApplyCriticalSuccessOnNatural20Helper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
