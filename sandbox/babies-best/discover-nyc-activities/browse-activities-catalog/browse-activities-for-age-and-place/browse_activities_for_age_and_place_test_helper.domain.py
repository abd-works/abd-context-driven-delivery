# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - BrowseActivitiesForAgeAndPlaceHelper backed by ActivityCatalog + RememberedPlace.
# Real: activities.Activity, place.PlaceFilter, place.RememberedPlace. Stubbed: nothing.
#
# Sources / context: .context/discover-nyc-activities/scenarios/browse-activities-for-age-and-place.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Browse Activities For Age And Place`.
"""

from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_BABIES = Path(__file__).resolve().parents[3]
if str(_BABIES) not in sys.path:
    sys.path.insert(0, str(_BABIES))

from browse_activities_for_age_and_place_story import (  # noqa: E402
    create_browse_activities_for_age_and_place_story,
)
from activities.catalog_world import CatalogWorld  # noqa: E402
from place.place import PlaceFilter  # noqa: E402


class DomainHelper:
    def __init__(self) -> None:
        self.world = CatalogWorld()

    def given_parent_with_profile_and_remembered_park_slope(self) -> None:
        self.world.profile.age_band = "6-12 months"
        self.world.age_filter = "6-12 months"
        self.world.remembered.remember(
            PlaceFilter(
                borough=self.world.brooklyn,
                neighborhood=self.world.park_slope,
                include_citywide=False,
            )
        )

    def when_parent_opens_things_to_do(self) -> None:
        self.world.open_things_to_do()

    def then_place_restored_and_age_matching_activities_listed(self) -> None:
        assert self.world.place_filter is not None
        assert self.world.place_filter.neighborhood.name == "Park Slope"
        assert self.world.prompt_choose_place is False
        names = [a.name for a in self.world.listed]
        assert "Carroll Park Playground" in names
        assert all(a.age_band == "6-12 months" for a in self.world.listed)
        for activity in self.world.listed:
            assert activity.name
            assert activity.kind in ("evergreen", "event")
            assert activity.place_label()
            assert activity.age_band


globals().update(create_browse_activities_for_age_and_place_story(DomainHelper()))
