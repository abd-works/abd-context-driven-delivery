# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to cdd_guidance/references/language-tools.md for tooling.
#
# ## Artifact layout (`artifacts-mirror-story-hierarchy`)
#
# Mirror Epic → Epic → Story on disk:
#
# ```
# {epic-verb-noun}/                         # kebab-case folder
#   {sub-epic-verb-noun}/
#     {story-kebab-slug}/
#       {story_snake}_story.test.md         # scenarios fidelity
#       {story_snake}_story.test.py         # acceptance_tests — not _spec.py
#
# # Machinery — copy once per tests/ tree if missing (do not inline in skills):
#   practices/stories/templates/py/story_test.py → tests/story_test.py
# ```
#
# ## Path naming (`kebab-case-paths`)
#
# Epic, sub-epic, and story **folders**: lowercase kebab-case. The test file is `{story_snake}_story.test.py`.
# No `snake_case` folders or `PascalCase` paths.
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
# Named domain fixtures live beside the code they build, in a package Python can import: a story folder's name
# holds hyphens, which no Python import can name. One file per domain concept
# (`{module}/account_credentials_examples.py`). Import in the story file; never repeat literals across scenarios.
#
# from shop.accounts.account_credentials_examples import valid_account_credentials
#
# Scenario realizations (default on unless the user says "no realizations"):
# After GWT is agreed, add a ```realization``` block after each Given group and each When group (see
# templates/md/scenarios.md): code-like statements, such as `# cart = Cart(customer_profile)` then
# `# CartRepository.create(cart)`, which the stories model reads from the comments at the top of the step.
#
# Pattern: GWT structure only — replace pass with real code under each with.
#
# ## The sample below (`edge-and-error-cases-have-scenarios`)
#
# A sample story placing an order, written out so you can see a filled-in file: replace each part with your own.
#   {Story Verb–Noun}                     → the story's name, as the story map names it
#   the background's given                → the domain state every scenario starts from
#   "customer places an order ..."        → the main flow: one scenario, its outcome, `and_` for each further outcome
#   "customer places an order ... empty"  → one scenario for each edge or error case that applies, written like any
#                                           other scenario; keep no table or list of cases beside them
# Add as many edge and error scenarios as the story has cases; write none for a case that does not apply.

from __future__ import annotations

from mamba import after, before

from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb–Noun}"):
    with before.all:
        pass  # infrastructure — boot / wiring (not domain Given)

    with after.all:
        pass  # infrastructure — teardown

    with background.each:
        with given("a customer has a cart"):
            pass  # domain state only

        with scenario("customer places an order for the books in the cart"):
            with given("the cart holds one book"):
                pass  # test code goes here

            with when("the Actor places the order"):
                pass  # test code goes here

            with then("an order holds the book"):
                pass  # test code goes here

            with and_("the cart is empty"):
                pass  # chain with and_, not a second then()

        with scenario("customer places an order for an empty cart"):
            with given("the cart holds no book"):
                pass  # test code goes here

            with when("the Actor places the order"):
                pass  # test code goes here

            with then("the order is refused because the cart is empty"):
                pass  # test code goes here

            with and_("no order is created"):
                pass  # test code goes here
