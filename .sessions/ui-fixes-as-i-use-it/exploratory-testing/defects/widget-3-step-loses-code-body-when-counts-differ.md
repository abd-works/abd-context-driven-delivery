# widget-3: A markdown step loses its story test's code body when the code scenario has one step more (an `.and`) and the step's words differ only by a term link

- **Charter:** C4
- **Tester:** Widget
- **Story:** Read Story And Spec Trees From Source, scenario "Keep a story test's code and examples when its story map is read with it" (each step keeps the code its story test gives it).
- **Module and class:** `cdd_guidance/practices/stories/model/story_map.py` `_paired_steps` (pairs by `_words_of(text)`, falls back to order only when both write as many steps); `Scenario.take_code_of`.
- **Severity:** wrong result (the step shows no code and no realization in the graph and explorer; nothing reports it)

## Steps

1. Copy `cdd_guidance/practices/stories/model/fixtures/bookshop` to a throwaway folder. Its `story_tests/browse-books/search-books/search_books_story.test.ts` has the scenario "Find nothing for an unknown word": given "the Bookshop sells [Book](…) Tiny Tales", when, then "…sees no [Book](…)" `.and(…)` (4 step lines).
2. Beside it write `search_books_story.test.md`, `## Story: Search Books`, with the scenarios "Find a book by a word of its title" and "Find nothing for an unknown word", steps written without the link: `*Given* the Bookshop sells Tiny Tales`, `*When* the Customer searches for Zebra`, `*Then* the Customer sees no Book` (3 lines).
3. Load the graph (`Graph().load_files(root, ["stories","ddd","clean_engineering"], [".context","story_tests","src","ordering"])`) and read the facts `body_text` and `written_in` of each step of the two scenarios.

## Expected

Each markdown step gets the body of the code step at its place (the Given gets `// domain state only`), as it does in the first scenario, or the drift is reported.

## Actual

First scenario (3 md lines, 3 code lines): all steps paired by order, Given body `// domain state only`, `written_in` the `.ts`.
Second scenario (3 md lines, 4 code lines): When and Then pair by words; the Given ("the bookshop sells tiny tales" vs "the bookshop sells book tiny tales") pairs with nothing, so it has `body_text` '' and no `written_in`, while the code's Given body and any realization it had are dropped silently. One extra `.and` in code thus decides whether the Given keeps its code.

## Tier that should catch it

Unit: a `_paired_steps` / story_tests_on_map example where code has an extra `.and` and one step differs by a link; expect the unmatched steps paired by keyword and order (or a violation naming the step).

## Also seen by

## Triage

- **Status:** confirmed
- **Severity:** wrong result (a markdown step silently loses its story test's body and realization)
- **Triaged by:** Prism
- **Why:** `_paired_steps` paired steps by their words, and fell back to order only when both sides wrote as many lines; a step whose words differ (a term link adds a word) and one `.and` more in code left the step with no code. Reproduced with a sub-epic markdown file beside a Python story test whose Given is worded otherwise and whose Then chains one line more.

## Fix

- **Test (unit):** `cdd_guidance/practices/stories/model/scenario_layouts_spec.py` "should give a markdown step the body of the code step of its kind at its place, when code words it otherwise and chains one line more", over the new layout `MARKDOWN_BESIDE_PYTHON_IN_OTHER_WORDS` in `fixtures/scenario_layouts.py`. Seen failing first.
- **Scenario:** "Give a markdown step its story test's code when the story test words it otherwise and writes one line more" in `story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/read-story-and-spec-trees-from-source/read_story_and_spec_trees_from_source_story.test.md`.
- **Fix:** `story_map.py` `_paired_steps`: after pairing by words (and the unchanged order fallback when both write as many lines), each step left unpaired takes the first unpaired code step of its kind (given, when or then), in order.
- **Commit:** 19af5c5c9
