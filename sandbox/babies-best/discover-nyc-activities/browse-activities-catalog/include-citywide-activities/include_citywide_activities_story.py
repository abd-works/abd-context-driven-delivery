# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/include-citywide-activities.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Include Citywide Activities (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class IncludeCitywideActivitiesHelper(Protocol):
    def given_park_slope_filter_and_citywide_festival(self) -> None: ...
    def when_parent_turns_citywide_on(self) -> None: ...
    def then_park_slope_and_citywide_appear_together(self) -> None: ...


def create_include_citywide_activities_story(h: "IncludeCitywideActivitiesHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_citywide_sits_beside_neighborhood_results_when_toggled_on() -> None:
        """SCENARIO: citywide sits beside neighborhood results when toggled on"""
        h.given_park_slope_filter_and_citywide_festival()
        h.when_parent_turns_citywide_on()
        h.then_park_slope_and_citywide_appear_together()

    tests["test_citywide_sits_beside_neighborhood_results_when_toggled_on"] = test_citywide_sits_beside_neighborhood_results_when_toggled_on
    return tests
