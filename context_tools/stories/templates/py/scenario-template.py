# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ```
# # Artifact layout (artifacts-mirror-story-hierarchy)
# tests/
#   {epic-verb-noun}/
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story_snake_slug}.py            # one GWT file per story
#
# # Machinery — copy once per tests/ tree if missing (do not inline in skills):
#   context_tools/stories/templates/py/story_test.py → tests/story_test.py
# story_test: tests/story_test.py
# ```
#
# Pattern: GWT structure only — replace pass with real code under each with.

from __future__ import annotations

from mamba import after, before

from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        pass  # boot — test code goes here

    with after.all:
        pass  # teardown — test code goes here

    with background.each:
        with given("{background given step}"):
            pass  # test code goes here

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with then("{observable surface outcome}"):
                pass  # test code goes here

        with scenario("{validation branch while typing}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with and_("{follow-on when step}"):
                pass  # test code goes here

            with then("{validation message on domain object}"):
                pass  # test code goes here

        with scenario("{validation clears when input conforms}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with and_("{prior invalid state}"):
                pass  # test code goes here

            with when("{corrective action}"):
                pass  # test code goes here

            with then("{error cleared on domain object}"):
                pass  # test code goes here

        with scenario("{main-flow outcome}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with when("{submit operation on domain object}"):
                pass  # test code goes here

            with then("{post-condition on loaded aggregate}"):
                pass  # test code goes here
