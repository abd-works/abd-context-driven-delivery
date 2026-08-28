# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/show-empty-place-results.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Show Empty Place Results (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class ShowEmptyPlaceResultsHelper(Protocol):
    def given_tottenville_with_no_matching_activities(self) -> None: ...
    def when_parent_views_activities_catalog(self) -> None: ...
    def then_no_rows_and_empty_place_message(self) -> None: ...


def create_show_empty_place_results_story(h: "ShowEmptyPlaceResultsHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_no_matches_message_when_place_and_filters_yield_nothing() -> None:
        """SCENARIO: no matches message when place and filters yield nothing"""
        h.given_tottenville_with_no_matching_activities()
        h.when_parent_views_activities_catalog()
        h.then_no_rows_and_empty_place_message()

    tests["test_no_matches_message_when_place_and_filters_yield_nothing"] = test_no_matches_message_when_place_and_filters_yield_nothing
    return tests
