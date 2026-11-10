"""
Story: Designate Power as Removable Device (scenario fidelity - tier-neutral).
Actor: Player
Calls helper-protocol methods only - no assertions, no tier mechanism here.
Tiers: designate_power_as_removable_device_test_helper.{tier}.py implements DesignatePowerAsRemovableDeviceHelper.
"""

from __future__ import annotations

from typing import Protocol


class DesignatePowerAsRemovableDeviceHelper(Protocol):
    ...


def create_designate_power_as_removable_device_story(h: "DesignatePowerAsRemovableDeviceHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn} for the tier file to bind at module scope.
    """
    tests = {}
    # TODO: add main-flow scenario
    return tests
