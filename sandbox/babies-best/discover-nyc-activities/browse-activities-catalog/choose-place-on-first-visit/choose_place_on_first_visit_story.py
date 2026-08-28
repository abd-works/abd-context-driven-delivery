# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/choose-place-on-first-visit.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Choose Place On First Visit (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class ChoosePlaceOnFirstVisitHelper(Protocol):
    def given_parent_with_no_remembered_place(self) -> None: ...
    def when_parent_opens_things_to_do(self) -> None: ...
    def then_prompts_for_place_and_lists_nothing(self) -> None: ...


def create_choose_place_on_first_visit_story(h: "ChoosePlaceOnFirstVisitHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_no_remembered_place_means_pick_borough_before_results() -> None:
        """SCENARIO: no remembered place means pick borough before results"""
        h.given_parent_with_no_remembered_place()
        h.when_parent_opens_things_to_do()
        h.then_prompts_for_place_and_lists_nothing()

    tests["test_no_remembered_place_means_pick_borough_before_results"] = test_no_remembered_place_means_pick_borough_before_results
    return tests
