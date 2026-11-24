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

## Also seen by
- Sparky, round 3 (build 4d47fdf8e): still fails, through the cdd server, on `C:\dev\_etound3\sparky\work\story_testsill-cartdd-books` (two scenarios files; results in `trip\py	ests\stories\scenarios_story.test.md`, the same bytes from TypeScript). Differs: the outline's rows were written under `#### Examples` as the template shows, and they still come back without their values, as a one-column table `| example |` with `example-1`, `example-2`, `example-3`, under a plain `#### Scenario:`. Also lost: the front matter, the `## Story:` layout, Story type, the story map link, the Domain terms list, every link from a term to `domain-model.md` (terms come back as `++Book++`), the realization block under the When (it is a comment in the Python and is not written back), and the sentence under Change Cart Line Quantity. Gained: the whole story map around the scenarios (16 stories and the Scope boundary), each examples table twice, the Background three times (once as `#### Story Background: background` and once inside each scenario), and a `group` column. The Python and TypeScript themselves do not parse (r3-sparky-06).

## Confirmation (Cog)
- Result: confirmed
- What I ran and saw: The Stories adapters called directly on a scenarios file of my own after the template (`C:\dev\_et\cog\place_order_story.test.md`, run by `w19.py` and `w19b.py`), not through the cdd server. Markdown read and written again is unchanged. The Python holds the outline as `scenario("Order total follows the lines")` with its two steps and no rows; read back, the scenario is no longer an outline. Front matter, the story map link, Domain terms, Story type and the sentence under Cancel Order are in neither code file.
- Cause: the story model does not hold an outline's rows. `ScenarioFileReading` (`stories/model/markdown/scenario_file.py`) reads a table into examples only under an Examples heading; the table under a Scenario Outline is kept as the lines the scenario was read with, which only the markdown writer writes back. `Scenario.examples` is empty for the outline, so no code format has rows to write, and `is_outline` is not written to code either.
- Fix: none yet. It needs the model to hold the outline's rows and each code format to write and read them, which is more than an adapter correction.

## Status: fixed (2026-11-23)
- Fixed before this pass (`7447a2040`, `66f410de3`): the outline's rows and names, the code named for its epic and sub-epic from the story map, the files that parse, the scenarios file written back as `## Story:` at its declared path.
- Fixed now: what a person wrote about the story comes through code and back. A story keeps its front matter and the notes under its heading (its kind, the story map link, the Domain terms list, the prose) as `Story.front_matter` and `Story.notes`, read by the scenarios file reading (`StorySection.give_notes`). Python and TypeScript write each line in the story's comment under `^` (front matter) or `|` (notes), and read them back (`CodeStory._marked_lines`). The scenarios file written back links each underlined domain term a step names as the notes link it (`DomainTermLinks`). The realization a story file writes as comments under a When is read back as the step's call graph (`StoryBlock.realization`, `Step.read_code`), so it returns as the ```realization block.
- Covered by `cdd_guidance/practices/stories/model/code_story_round_trip_spec.py` (Python and TypeScript, on the Bookshop's `add_book_to_cart_story.test.md`: front matter, story type, story map link, domain terms with links, linked terms in steps, the realization, each examples table once) and `code_outline_examples_spec.py` (the outline's rows).
- Left as it is: the trip does not give back the file byte for byte. Two trailing spaces at the end of a step line, and the indent before an And, are not kept; the Background comes back under `### Story Background: background`, which reads back to the same steps.

## Answer (2026-11-23)

Prose a drawing cannot hold is kept in the drawing's hidden metadata, so a trip through a drawing loses nothing. Built as one mechanism every practice's drawing formats share: `PracticeFormats.render` (`harness/guidance/practice_formats.py`) hands a drawing the document it is drawn from, in its format (*SourceDocument*, `harness/markdown/format.py`); a draw.io file keeps it on its page's root cell, inside the `UserObject` draw.io shows as the diagram's data (`DrawioFile.keep`, *KeepsDocumentInDrawing*, `harness/drawio/drawio.py`), and a whiteboard in its board meta (*KeepsDocumentOnBoard*, `harness/whiteboard/whiteboard.py`); a render of the drawing back into that format, with no file there, writes over the kept document as the file it replaces, so each practice's markdown adapter gives back the words the drawing does not show. Mixed into the draw.io and whiteboard formats of Stories, DDD, Clean Engineering and UX. For this defect: the story model already holds a scenario outline's examples and a story's front matter and notes (fixed before, see Status), and a scenarios file has no drawing format, so its trips are through Python, TypeScript and JavaScript, which `format_trip_spec.py` "the formats Stories declares" / "at scenarios" and "at acceptance tests" now show return what went in; the story map's own trip through drawio and whiteboard returns what went in with no story-map.md there to write over. Tested by `cdd_guidance/practices/format_trip_spec.py` (one shared behaviour for every practice and fidelity; the drawio and whiteboard `leaves_out` of the story map, bounded-context map, domain model, module cards and class model are removed, since those trips no longer lose anything), `format_trip_heavy_spec.py`, `code_outline_examples_spec.py`, `code_story_round_trip_spec.py`, `harness/drawio/drawio_spec.py` "a draw.io file that keeps the document it was drawn from", `harness/whiteboard/whiteboard_spec.py` "a whiteboard that keeps the document it was drawn from" and `harness/guidance/format_adapter_spec.py` "a drawing rendered from a document"; scenario "Keep the prose a drawing cannot show through a trip to draw.io and back" in `story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_artifact_to_another_format_and_back_story.test.md`. Still as the Status says: the code trip does not give the file back byte for byte (trailing spaces, the indent before an And, the Background heading).
