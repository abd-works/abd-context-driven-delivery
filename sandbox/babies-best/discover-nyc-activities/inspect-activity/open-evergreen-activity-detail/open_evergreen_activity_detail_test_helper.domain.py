# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - OpenEvergreenActivityDetailHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/open-evergreen-activity-detail.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Open Evergreen Activity Detail`.
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

from open_evergreen_activity_detail_story import create_open_evergreen_activity_detail_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_evergreen_carroll_park(self) -> None:
        self.world = CatalogWorld()

    def when_parent_opens_that_activity(self) -> None:
        self.detail = self.world.open_activity("Carroll Park Playground")

    def then_detail_shows_evergreen_fields(self) -> None:
        assert self.detail.kind == "evergreen"
        assert self.detail.age_band == "6-12 months"
        assert self.detail.neighborhood.name == "Park Slope"
        assert self.detail.neighborhood.borough.name == "Brooklyn"
        assert self.detail.hours == "dawn–dusk"
        assert self.detail.notes


globals().update(create_open_evergreen_activity_detail_story(DomainHelper()))
