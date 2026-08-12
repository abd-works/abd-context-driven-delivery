# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - SaveActivityToListFromDetailHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/save-activity-to-list-from-detail.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Save Activity To List From Detail`.
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

from save_activity_to_list_from_detail_story import create_save_activity_to_list_from_detail_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_activity_detail_with_personal_list(self) -> None:
        self.world = CatalogWorld()
        self.world.personal_lists = ["Weekend outings"]
        self.world.open_activity("Carroll Park Playground")

    def when_parent_saves_activity_to_list(self) -> None:
        self.world.save_to_list("Weekend outings")

    def then_activity_appears_on_chosen_list(self) -> None:
        assert any(self.world.detail.id in row for row in self.world.saved)

    def given_activity_detail_with_no_personal_list(self) -> None:
        self.world = CatalogWorld()
        self.world.personal_lists = []
        self.world.open_activity("Carroll Park Playground")

    def when_parent_chooses_save_to_list(self) -> None:
        self.world.save_to_list("Weekend outings")

    def then_app_prompts_to_create_list(self) -> None:
        assert self.world.prompt_create_list is True
        assert self.world.saved == []


globals().update(create_save_activity_to_list_from_detail_story(DomainHelper()))
