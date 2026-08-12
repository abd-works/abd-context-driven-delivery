# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - FilterByBoroughThenNeighborhoodHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/filter-by-borough-then-neighborhood.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Filter By Borough Then Neighborhood`.
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

from filter_by_borough_then_neighborhood_story import create_filter_by_borough_then_neighborhood_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402
from place.place import PlaceFilter  # noqa: E402


class DomainHelper:

    def given_brooklyn_results_with_park_slope_activities(self) -> None:
        self.world = CatalogWorld()
        self.world.age_filter = "6-12 months"
        self.world.place_filter = PlaceFilter(
            borough=self.world.brooklyn, neighborhood=None, include_citywide=False
        )
        self.world.refresh()

    def when_parent_selects_brooklyn_then_park_slope(self) -> None:
        self.world.choose_place(self.world.brooklyn, "Park Slope")

    def then_only_park_slope_activities_listed(self) -> None:
        assert self.world.place_filter.borough.name == "Brooklyn"
        assert self.world.place_filter.neighborhood.name == "Park Slope"
        assert all(
            a.neighborhood is not None and a.neighborhood.name == "Park Slope"
            for a in self.world.listed
        )


globals().update(create_filter_by_borough_then_neighborhood_story(DomainHelper()))
