# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - ShowEmptyPlaceResultsHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/show-empty-place-results.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Show Empty Place Results`.
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

from show_empty_place_results_story import create_show_empty_place_results_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_tottenville_with_no_matching_activities(self) -> None:
        self.world = CatalogWorld()
        self.world.age_filter = "6-12 months"
        self.world.choose_place(self.world.staten_island, "Tottenville")

    def when_parent_views_activities_catalog(self) -> None:
        self.world.refresh()

    def then_no_rows_and_empty_place_message(self) -> None:
        assert self.world.listed == []
        assert self.world.empty_message is True


globals().update(create_show_empty_place_results_story(DomainHelper()))
