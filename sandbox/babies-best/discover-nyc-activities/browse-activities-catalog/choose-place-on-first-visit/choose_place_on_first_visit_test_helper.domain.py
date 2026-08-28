# ---
# fidelity: [engineering]
# artifact: [test-helper]
# format: py
# ---
#
# Tier: domain - ChoosePlaceOnFirstVisitHelper backed by ActivityCatalog / Place / RememberedPlace.
# Sources / context: .context/discover-nyc-activities/scenarios/choose-place-on-first-visit.md

"""
# @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
# invoke-check: action validate | toolset: context_tools.stories.stories:Stories

Domain tier test-helper for `Choose Place On First Visit`.
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

from choose_place_on_first_visit_story import create_choose_place_on_first_visit_story  # noqa: E402
from activities.catalog_world import CatalogWorld  # noqa: E402


class DomainHelper:

    def given_parent_with_no_remembered_place(self) -> None:
        self.world = CatalogWorld()
        assert self.world.remembered.restore() is None

    def when_parent_opens_things_to_do(self) -> None:
        self.world.open_things_to_do()

    def then_prompts_for_place_and_lists_nothing(self) -> None:
        assert self.world.prompt_choose_place is True
        assert self.world.listed == []


globals().update(create_choose_place_on_first_visit_story(DomainHelper()))
