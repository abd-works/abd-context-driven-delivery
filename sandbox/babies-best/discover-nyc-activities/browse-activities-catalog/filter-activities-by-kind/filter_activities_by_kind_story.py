# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/filter-activities-by-kind.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Filter Activities By Kind (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class FilterActivitiesByKindHelper(Protocol):
    def given_mixed_evergreen_and_dated_activities(self) -> None: ...
    def when_parent_filters_kind_events(self) -> None: ...
    def then_only_dated_events_remain(self) -> None: ...


def create_filter_activities_by_kind_story(h: "FilterActivitiesByKindHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_evergreen_vs_dated_event_can_be_narrowed() -> None:
        """SCENARIO: evergreen vs dated event can be narrowed"""
        h.given_mixed_evergreen_and_dated_activities()
        h.when_parent_filters_kind_events()
        h.then_only_dated_events_remain()

    tests["test_evergreen_vs_dated_event_can_be_narrowed"] = test_evergreen_vs_dated_event_can_be_narrowed
    return tests
