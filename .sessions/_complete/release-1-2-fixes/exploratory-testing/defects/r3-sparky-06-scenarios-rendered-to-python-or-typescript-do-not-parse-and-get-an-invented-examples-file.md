# Scenarios with an outline's examples table, rendered to Python or TypeScript, do not parse (`import example-1, example-2`), the TypeScript calls a `background` it does not import, and its examples file holds invented data

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a scenarios file's render to code.
- **Module and class:** the Stories code adapters `cdd_guidance/practices/stories/model/python/python_story_model.py`, `model/typescript/typescript_story_model.py` and their shared `model/code_story_model.py` (the examples import line and the examples seed file).
- **Severity:** wrong result (the file render writes for the fidelity's default format is not Python, and the TypeScript is not TypeScript)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh s1.json`, `s2.json`). `story_tests/fill-cart/add-books/change_cart_line_quantity_story.test.md` holds a Scenario Outline with its rows under `#### Examples`, as `templates/md/scenarios.md` writes them:

    #### Examples

    | scenario | quantity | total |
    | --- | --- | --- |
    | one copy | 1 | 5 |
    | two copies | 2 | 10 |
    | three copies | 3 | 15 |

`add_book_to_cart_story.test.md` beside it holds a Background and two example tables (book, cart).

1. `render.render {"guidance": "stories-scenarios", "format": "python", "paths": ["story_tests/fill-cart/add-books"], "source": "markdown"}`; save the returned content.
2. The same with `"format": "typescript"`.
3. Parse the Python with `ast.parse`.

## Expected
Code that parses and that holds what the scenarios hold: the outline's three rows with their values, and the examples the tables name (Tiny Tales, Grand Atlas, empty cart, cart with Tiny Tales).

## Actual
Python (`trip\py\tests\stories\scenarios_story.test.py`), line 4:

    from examples import example-1, example-2, example-3
    SyntaxError: invalid syntax

The outline is written as a plain `scenario("Cart total follows the quantity")` with the comment `# examples: example-1, example-2, example-3`; the names one copy, two copies, three copies and the values 1/5, 2/10, 3/15 are nowhere in the file.

TypeScript (`trip\ts\tests\stories\scenarios_story.test.ts`):

    import { scenario, story } from "tests/story-test";
    import { example-1, example-2, example-3 } from "./examples";

`example-1` is no identifier, and the file calls `background('background', ...)` five times without importing it. The Background's two steps are written once under the story and again inside each of its scenarios. The examples file written beside it, `tests/stories/examples/stories.examples.ts`, exports none of the three names and none of the Bookshop's examples; it holds `export interface Stories { id; status; email; planName }` with `activeStoriesExample` (`email: 'active-user@example.com'`, `planName: 'Premium Plan'`), `pendingStoriesExample` and `suspendedStoriesExample`, data no source names. A render from Python to TypeScript writes the same placeholder as `fill-cart/examples/fillcart.examples.ts` (`interface FillCart`) and `check-out/examples/out.examples.ts` (`interface Out`).

The story with no Background, Change Cart Line Quantity, gets `# background: background` on both its scenarios (the cause r3-sparky-03 reports in the graph).

## Tier that should catch it
Unit (`code_story_round_trip_spec.py`, `story_code_render_spec.py`): no example renders an outline with an examples table and then parses the Python or checks the TypeScript's imports.
