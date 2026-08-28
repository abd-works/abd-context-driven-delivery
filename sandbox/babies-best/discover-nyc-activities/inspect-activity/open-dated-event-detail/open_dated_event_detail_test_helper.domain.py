# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - OpenDatedEventDetailHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/open-dated-event-detail.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Open Dated Event Detail`.
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

from open_dated_event_detail_story import create_open_dated_event_detail_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_dated_library_story_time(self) -> None:
        self.world = CatalogWorld()

    def when_parent_opens_that_activity(self) -> None:
        self.detail = self.world.open_activity("Library Story Time")

    def then_detail_shows_event_when(self) -> None:
        assert self.detail.kind == "event"
        assert self.detail.event_date == "this Saturday"
        assert self.detail.event_time == "10:00 am"
        assert self.detail.place_label() == "Brooklyn / Park Slope"


globals().update(create_open_dated_event_detail_story(DomainHelper()))
