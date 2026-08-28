# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/filter-by-borough-then-neighborhood.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Filter By Borough Then Neighborhood (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class FilterByBoroughThenNeighborhoodHelper(Protocol):
    def given_brooklyn_results_with_park_slope_activities(self) -> None: ...
    def when_parent_selects_brooklyn_then_park_slope(self) -> None: ...
    def then_only_park_slope_activities_listed(self) -> None: ...


def create_filter_by_borough_then_neighborhood_story(h: "FilterByBoroughThenNeighborhoodHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_place_narrows_from_borough_to_neighborhood() -> None:
        """SCENARIO: place narrows from borough to neighborhood"""
        h.given_brooklyn_results_with_park_slope_activities()
        h.when_parent_selects_brooklyn_then_park_slope()
        h.then_only_park_slope_activities_listed()

    tests["test_place_narrows_from_borough_to_neighborhood"] = test_place_narrows_from_borough_to_neighborhood
    return tests
