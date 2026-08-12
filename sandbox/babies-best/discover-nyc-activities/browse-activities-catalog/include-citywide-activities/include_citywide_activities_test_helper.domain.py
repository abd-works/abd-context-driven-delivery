# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - IncludeCitywideActivitiesHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/include-citywide-activities.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Include Citywide Activities`.
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

from include_citywide_activities_story import create_include_citywide_activities_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_park_slope_filter_and_citywide_festival(self) -> None:
        self.world = CatalogWorld()
        self.world.age_filter = "6-12 months"
        self.world.choose_place(self.world.brooklyn, "Park Slope")

    def when_parent_turns_citywide_on(self) -> None:
        self.world.include_citywide(True)

    def then_park_slope_and_citywide_appear_together(self) -> None:
        names = [a.name for a in self.world.listed]
        assert "Carroll Park Playground" in names
        assert "Baby Music Festival" in names
        assert any(a.neighborhood is None for a in self.world.listed)
        assert any(
            a.neighborhood is not None and a.neighborhood.name == "Park Slope"
            for a in self.world.listed
        )


globals().update(create_include_citywide_activities_story(DomainHelper()))
