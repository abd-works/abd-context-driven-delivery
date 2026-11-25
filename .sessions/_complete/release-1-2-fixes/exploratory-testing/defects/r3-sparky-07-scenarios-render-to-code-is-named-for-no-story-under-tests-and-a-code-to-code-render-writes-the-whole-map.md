# A scenarios render to Python or TypeScript is not written where the fidelity says: markdown to code comes back as one `tests/stories/scenarios_story.test.py` for every story, and code to code comes back as a file for every sub-epic of the map

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers where a scenarios render to code is written.
- **Module and class:** `cdd_guidance/practices/stories/stories_formats.py` `StoriesFormats.read`, the code adapters under `cdd_guidance/practices/stories/model/` (`tests_root`, `default_workspace_folder = "tests"`), and `cdd_guidance/actions/render/render.py` (a code render returns content and saves nothing).
- **Severity:** wrong result (no file at the place the fidelity names; the agent has to guess where each file goes)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh s1.json`, `s2.json`). The map has 4 epics, 4 sub-epics and 16 stories; `story_tests/fill-cart/add-books/` holds markdown scenarios for the two stories of sub-epic Add Books.

1. `generate.generate {"guidance": "stories-scenarios"}` and read its save line.
2. `render.render {"guidance": "stories-scenarios", "format": "python", "paths": ["story_tests/fill-cart/add-books"], "source": "markdown"}`
3. Save that content under `trip/py`, then `render.render {"guidance": "stories-scenarios", "format": "typescript", "paths": ["trip/py/tests/stories/scenarios_story.test.py"], "source": "python"}`, and the same from the TypeScript to Python.

## Expected
Step 1 says: `python: .../story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.py; typescript: .../story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.ts`. So the render answers `story_tests/fill-cart/add-books/add-book-to-cart/add_book_to_cart_story.test.py` and `.../change-cart-line-quantity/change_cart_line_quantity_story.test.py`, one file a story, and a render of one story test answers that one story test in the other language.

## Actual
- Step 2 answers content only, nothing saved, under one name: `tests/stories/scenarios_story.test.py`, headed `# Epic: Scenarios` and `# Orders: 0.0.0`, holding both stories. Neither the epic Fill Cart, the sub-epic Add Books nor a story's name is in the path. TypeScript the same (`tests/stories/scenarios_story.test.ts`, with `tests/story-test.ts`).
- Step 3 answers a file for every sub-epic and flat epic of the map, though one file was named: `tests/browse-books/browse_books_story.test.ts`, `tests/fill-cart/add_books_story.test.ts`, `tests/fill-cart/review_cart_story.test.ts`, `tests/check-out/place_order_story.test.ts`, `tests/check-out/confirm_order_story.test.ts`, `tests/fulfil-order/fulfil_order_story.test.ts`. Fourteen stories that have no scenarios come back as empty `with story("Pack Order"): pass` blocks. The paths follow the story map template's comment (`tests/{epic}/{sub_epic}_story.test.{ext}`), a third layout beside the fidelity's `outputs` and the scenarios template's own comment (`{epic}/{sub-epic}/{story}/{story_snake}_story.test.md`, where `outputs` has no `{story}` folder for markdown).
- generate's own answer adds to it: "Where each listed practice writes: stories: C:/dev/_et/round3/sparky/work/tests", while every path in its save line is under `.context` or `story_tests`.

A render of the code back to markdown is saved beside the code as `scenarios_story.test.md` and holds the whole story map with the scenarios inside it (see the round 3 line under "Also seen by" in widget-19).

## Tier that should catch it
Heavy (`render_saves_beside_source_heavy_spec.py`): no example renders a scenarios file to code and compares the answered paths with the fidelity's `outputs`.

## Added later the same run (drv\t1.json)
- `render.render {"guidance": "stories-scenarios", "format": "markdown", "paths": ["story_tests/check-out/place-order/submit-order/submit_order_story.test.py"], "source": "python"}` saves `submit_order_story.test.md` beside the Python file, in the story's folder, where the fidelity's markdown path has no story folder. Its headings hold the epic twice, `# (E) Check Out`, `## (E) Place Order`, `### (E) Check Out`, `#### (S) Customer --> Submit Order` (kept as `trip\sub-md.submit_order_story.test.md`): an epic Check Out is written again inside its own sub-epic, and the story sits one level too deep. The steps and their links to `domain-model.md` are kept; the call graph written as comments under the When (`# Order.submit(cart)`, `#   -> Cart.total`, `#   <- Order`) is not written back as a realization block.
- A TypeScript story test under `story_tests/check-out/confirm-order/view-order-confirmation/` rendered to Python comes back as `tests/check-out/confirm-order/check_out_story.test.py`, named for the epic, and `fulfil-order.story.shared.py` rendered to TypeScript comes back as a plain `fulfil_order_story.test.ts`, not a shared file. Step bodies cross as comments (`// python body to translate:`), which is as the adapters say.
