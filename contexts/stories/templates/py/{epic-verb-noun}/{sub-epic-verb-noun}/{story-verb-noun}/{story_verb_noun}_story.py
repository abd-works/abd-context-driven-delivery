# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Runnable story (explore/spec). Wired to ExampleFactory fakes.
# Assert the public interface of I{Type} only.
#
#   Folder tree      -> {epic-verb-noun}/{sub-epic-verb-noun}/{story-verb-noun}/
#   Story file       -> {story_verb_noun}_story.py
#   Isolated spec    -> {story_verb_noun}_spec.py          (engineering)
#   Tier spec        -> {story_verb_noun}_spec.{tier}.py   (engineering)
#
# Concrete values live in {Type}ExampleFactory — do not invent example tables here.

"""Story tests for `{Story Name}` — fake mode when collected as the entry module."""

from __future__ import annotations

from {epic_verb_noun}_helper import {EpicVerbNoun}Helper

helper = {EpicVerbNoun}Helper()


def create_{story_verb_noun}_story(mode: str = "fake") -> None:
    """Register scenarios. Story entry uses fake; tier specs pass isolated|production."""

    def test_main_flow_observable_outcome() -> None:
        # given — helper.given_…(mode=mode) → fake I{Type} from ExampleFactory
        bundle = helper  # replace with real given_* call
        _ = bundle

        # when — exercise public operations on I{Type}
        ...

        # then — assert public interface only (no private fields)
        assert True  # replace with public-seam assertion


# Collect when this module is the pytest entry (not when a tier imports the function)
create_{story_verb_noun}_story("fake")
