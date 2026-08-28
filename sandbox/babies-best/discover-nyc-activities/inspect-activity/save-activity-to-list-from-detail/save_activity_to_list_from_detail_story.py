# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/save-activity-to-list-from-detail.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Save Activity To List From Detail (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class SaveActivityToListFromDetailHelper(Protocol):
    def given_activity_detail_with_personal_list(self) -> None: ...
    def when_parent_saves_activity_to_list(self) -> None: ...
    def then_activity_appears_on_chosen_list(self) -> None: ...
    def given_activity_detail_with_no_personal_list(self) -> None: ...
    def when_parent_chooses_save_to_list(self) -> None: ...
    def then_app_prompts_to_create_list(self) -> None: ...


def create_save_activity_to_list_from_detail_story(h: "SaveActivityToListFromDetailHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_save_hands_off_to_list_picker() -> None:
        """SCENARIO: save hands off to list picker"""
        h.given_activity_detail_with_personal_list()
        h.when_parent_saves_activity_to_list()
        h.then_activity_appears_on_chosen_list()

    tests["test_save_hands_off_to_list_picker"] = test_save_hands_off_to_list_picker

    def test_no_list_yet_prompts_create() -> None:
        """SCENARIO: no list yet prompts create"""
        h.given_activity_detail_with_no_personal_list()
        h.when_parent_chooses_save_to_list()
        h.then_app_prompts_to_create_list()

    tests["test_no_list_yet_prompts_create"] = test_no_list_yet_prompts_create
    return tests
