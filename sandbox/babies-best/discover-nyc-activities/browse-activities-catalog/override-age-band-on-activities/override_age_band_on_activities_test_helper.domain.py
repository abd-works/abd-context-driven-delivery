# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - OverrideAgeBandOnActivitiesHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/override-age-band-on-activities.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Override Age Band On Activities`.
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

from override_age_band_on_activities_story import create_override_age_band_on_activities_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_profile_age_following_filter(self) -> None:
        self.world = CatalogWorld()
        self.world.profile.age_band = "0-3 months"
        self.world.age_filter = "0-3 months"
        self.world.choose_place(self.world.brooklyn, "Park Slope")

    def when_parent_sets_age_filter_to_12_18(self) -> None:
        self.world.override_age("12-18 months")

    def then_listed_match_override_and_profile_unchanged(self) -> None:
        assert self.world.age_filter == "12-18 months"
        assert self.world.profile.age_band == "0-3 months"
        assert all(a.age_band == "12-18 months" for a in self.world.listed)


globals().update(create_override_age_band_on_activities_story(DomainHelper()))
