# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/open-dated-event-detail.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Open Dated Event Detail (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class OpenDatedEventDetailHelper(Protocol):
    def given_dated_library_story_time(self) -> None: ...
    def when_parent_opens_that_activity(self) -> None: ...
    def then_detail_shows_event_when(self) -> None: ...


def create_open_dated_event_detail_story(h: "OpenDatedEventDetailHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_event_shows_when_it_happens() -> None:
        """SCENARIO: event shows when it happens"""
        h.given_dated_library_story_time()
        h.when_parent_opens_that_activity()
        h.then_detail_shows_event_when()

    tests["test_event_shows_when_it_happens"] = test_event_shows_when_it_happens
    return tests
