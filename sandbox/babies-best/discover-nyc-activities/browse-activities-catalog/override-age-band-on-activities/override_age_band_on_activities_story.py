# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/override-age-band-on-activities.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Override Age Band On Activities (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class OverrideAgeBandOnActivitiesHelper(Protocol):
    def given_profile_age_following_filter(self) -> None: ...
    def when_parent_sets_age_filter_to_12_18(self) -> None: ...
    def then_listed_match_override_and_profile_unchanged(self) -> None: ...


def create_override_age_band_on_activities_story(h: "OverrideAgeBandOnActivitiesHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_manual_age_filter_overrides_profile_default_for_this_browse() -> None:
        """SCENARIO: manual age filter overrides profile default for this browse"""
        h.given_profile_age_following_filter()
        h.when_parent_sets_age_filter_to_12_18()
        h.then_listed_match_override_and_profile_unchanged()

    tests["test_manual_age_filter_overrides_profile_default_for_this_browse"] = test_manual_age_filter_overrides_profile_default_for_this_browse
    return tests
