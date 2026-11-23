# A scenarios file rendered to Python or TypeScript and back loses its scenario outline's table, domain terms, story type, links and prose, and comes back with story-map headings

- **Charter:** Round 2 - the knowledge graph and the formats of the other practices, as an agent whose files move, rename and stop parsing between two calls
- **Tester:** Widget
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers a scenarios file's trip through its formats.
- **Module and class:** the Stories adapters `cdd_guidance/practices/stories/model/markdown`, `model/python`, `model/typescript`, called by `render.render` at `stories-scenarios`.
- **Severity:** wrong result (what a person wrote is lost)

## Steps
Sandbox `repo` (`C:\dev\_et\widget\work\repo`), session `main`, throwaway cdd server (`C:\dev\_et\widget\work\drv\run.py`, calls in `drv\d8.json`, `drv\d9.json`).

`story_tests/sell-books/take-orders/place_order_story.test.md` (kept as `repo\trip\orig\place_order_story.test.md`) follows `templates/md/scenarios.md`: two stories, Story type, a link to the story map, Domain terms, two examples tables, a Background, and

    #### Scenario Outline: Order total follows the lines

    *When* the Customer places an order of <quantity> copies of ++book++ ++cheap book++
    *Then* the total is <total>

    | quantity | total |
    | --- | --- |
    | 1 | 5 |
    | 3 | 15 |

1. `render.render {"guidance": "stories-scenarios", "format": "python", "paths": ["story_tests/sell-books/take-orders/place_order_story.test.md"], "source": "markdown"}`; save the returned content (it comes back under the name `tests/stories/scenarios_story.test.py`).
2. `render.render {"guidance": "stories-scenarios", "format": "markdown", "paths": ["<that file>"], "source": "python"}`
3. The same two steps with `typescript`.

## Expected
The scenarios, steps, examples and the outline's rows come back, in the scenarios layout (`## Story: ...`), with the terms and prose a person wrote.

## Actual
The Python and the TypeScript hold the outline as a plain `scenario("Order total follows the lines")` with its two steps; the rows `1 | 5` and `3 | 15` are in neither file. The returned file is named for no story (`tests/stories/scenarios_story.test.py`, with `# Epic: Scenarios`), though the source sits under sell-books/take-orders.

The markdown that comes back (`repo\trip\py\tests\stories\scenarios_story.test.md`; the same 2,011 bytes come back from TypeScript) starts

    # (E) Sell Books
    ## (E) Take Orders
    ### (S) Customer --> Place Order

    #### Examples

and has lost the front matter, `**Story type:** website`, the link to the story map, the Domain terms list, the outline's table, and the sentence under Cancel Order. The examples tables gained a `group` column and their first two columns changed places. The steps and the Background survived.

## Tier that should catch it
Unit (`code_story_round_trip_spec.py`): it covers a trip for steps; no example carries a scenario outline's table, domain terms or prose through and back.
