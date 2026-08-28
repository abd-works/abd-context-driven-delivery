# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Runnable story (scenario fidelity - tier-neutral). Calls helper-protocol
# methods only - no assertions, no tier mechanism here.
#
#   Folder tree   -> discover-nyc-activities/browse-activities-catalog/browse-activities-for-age-and-place/
#   Story file    -> browse_activities_for_age_and_place_story.py
#   Tier files    -> browse_activities_for_age_and_place_test_helper.{tier}.py
#
# Sources / context: .context/discover-nyc-activities/scenarios/browse-activities-for-age-and-place.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Browse Activities For Age And Place (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class BrowseActivitiesForAgeAndPlaceHelper(Protocol):
    def given_parent_with_profile_and_remembered_park_slope(self) -> None: ...
    def when_parent_opens_things_to_do(self) -> None: ...
    def then_place_restored_and_age_matching_activities_listed(self) -> None: ...


def create_browse_activities_for_age_and_place_story(
    h: "BrowseActivitiesForAgeAndPlaceHelper",
) -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_catalog_opens_with_profile_age_and_last_remembered_place() -> None:
        """SCENARIO: catalog opens with profile age and last remembered place"""
        h.given_parent_with_profile_and_remembered_park_slope()
        h.when_parent_opens_things_to_do()
        h.then_place_restored_and_age_matching_activities_listed()

    tests["test_catalog_opens_with_profile_age_and_last_remembered_place"] = (
        test_catalog_opens_with_profile_age_and_last_remembered_place
    )
    return tests
