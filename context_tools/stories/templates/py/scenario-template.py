# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ## Artifact layout (`artifacts-mirror-story-hierarchy`)
#
# Mirror Epic → SubEpic → Story on disk:
#
# ```
# tests/
#   {epic-verb-noun}/                    # kebab-case folder
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story-kebab-slug}.py            # one GWT file per story — no {story}/ folder
#
# # Machinery — copy once per tests/ tree if missing (do not inline in skills):
#   context_tools/stories/templates/py/story_test.py → tests/story_test.py
# ```
#
# ## Path naming (`kebab-case-paths`)
#
# Epic and SubEpic **folders**, story **file** stems, and tier segments: lowercase kebab-case
# (`sign-up`, `front-end`). No `snake_case` folders or `PascalCase` paths.
# **Exception:** Python epic helper only — `{epic_slug}_helper.py` at the epic folder root.
#
# ## Outcome chaining (`then-and-chaining`)
#
# First outcome: `then(...)`. Every later outcome on the same interaction: `.and_(...)`.
# Do not repeat `then()` for the same When. Markdown *And* stays *And*.
#
# ## Lifecycle hooks (`infrastructure-in-lifecycle-hooks`)
#
# Browser boot, app wiring, and `initialize` live in `before.all` / `after.all` — not in `given()`.
#
# ## Assertion helpers (`extract-assertion-helper`)
#
# The same assertion shape more than twice → named helper that takes a data bag; call sites pass values only.
#
# ## Example fixtures (`shared-example-fixtures`)
#
# Named domain fixtures live under `examples/` at the lowest **shared** folder:
#   `{epic}/examples/` — seeds shared across the epic
#   `{epic}/{sub-epic}/examples/` — catalog / givens shared by stories in the sub-epic
#   `{epic}/{sub-epic}/{story}/examples/` — fixtures unique to this story
# One file per domain concept (`account-credentials.examples.py`). Import in the story file;
# never repeat literals across scenarios. Golden layout: `context_tools/stories/examples/telco-website/`.
#
# from .examples.account_credentials_examples import valid_account_credentials
#
# Pattern: GWT structure only — replace pass with real code under each with.

from __future__ import annotations

from mamba import after, before

from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        pass  # infrastructure — boot / wiring (not domain Given)

    with after.all:
        pass  # infrastructure — teardown

    with background.each:
        with given("{background given step}"):
            pass  # domain state only

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                pass  # test code goes here

            with then("{observable surface outcome}"):
                pass  # test code goes here

            with and_("{further outcome on same interaction}"):
                pass  # chain with and_, not a second then()

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
