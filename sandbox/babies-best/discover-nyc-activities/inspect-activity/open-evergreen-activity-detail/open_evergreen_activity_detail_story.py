# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Sources / context: .context/discover-nyc-activities/scenarios/open-evergreen-activity-detail.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Story: Open Evergreen Activity Detail (scenario fidelity - tier-neutral).
"""

from __future__ import annotations

from typing import Protocol


class OpenEvergreenActivityDetailHelper(Protocol):
    def given_evergreen_carroll_park(self) -> None: ...
    def when_parent_opens_that_activity(self) -> None: ...
    def then_detail_shows_evergreen_fields(self) -> None: ...


def create_open_evergreen_activity_detail_story(h: "OpenEvergreenActivityDetailHelper") -> dict:
    """Build one pytest test function per scenario."""
    tests = {}

    def test_standing_place_shows_hours_and_notes_not_a_single_date() -> None:
        """SCENARIO: standing place shows hours and notes, not a single date"""
        h.given_evergreen_carroll_park()
        h.when_parent_opens_that_activity()
        h.then_detail_shows_evergreen_fields()

    tests["test_standing_place_shows_hours_and_notes_not_a_single_date"] = test_standing_place_shows_hours_and_notes_not_a_single_date
    return tests
