# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - FilterActivitiesByKindHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/filter-activities-by-kind.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Filter Activities By Kind`.
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

from filter_activities_by_kind_story import create_filter_activities_by_kind_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_mixed_evergreen_and_dated_activities(self) -> None:
        self.world = CatalogWorld()
        self.world.age_filter = "0-24 months"
        self.world.choose_place(self.world.brooklyn, "Park Slope")

    def when_parent_filters_kind_events(self) -> None:
        self.world.filter_kind("Events")

    def then_only_dated_events_remain(self) -> None:
        assert self.world.listed
        assert all(a.kind == "event" for a in self.world.listed)


globals().update(create_filter_activities_by_kind_story(DomainHelper()))
