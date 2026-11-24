# Question: a mockup rendered to claude_design, the second format the fidelity offers, answers `{}`, writes no canvas.json, and cannot be rendered back

- **Charter:** Round 3 - UX (ia, mockup, front_end_code) in every format: generate, render, graph
- **Tester:** Gizmo
- **Story:** no scenario covers a mockup's trip between html and claude_design.
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/nodes.py` `ClaudeDesignUxMap.save` / `boards` / `parse`.
- **Severity:** answered question

## Steps
Sandbox `C:\dev\_et\round3\gizmo\work`, session `main` (`drv\b1.json`, `drv\b2.json`, `drv\c1.json`). `bookshop/buy-a-book.html` is the mockup `HtmlUxMap` rendered from `ux/ux.json`: 6 screens, 13 regions, 12 controls (3 of them Story Demo controls), 4 interactions, 7 transitions.

1. `ticket.format_choices {"ticket": "main", "fidelities": ["ux-mockup"]}` -> chips `code [html]` and `canvas [claude_design]`.
2. `render.render {"guidance": "ux-mockup", "format": "claude_design", "paths": ["bookshop/buy-a-book.html"], "source": "html"}`
3. The same from a map whose six screens each name a prototype (`trip/ux-proto.json`, `"prototype": "<slug>.dc.html"`).
4. Put `{}` in `design-canvas/v1/project/canvas.json`, the place `generate` names for claude_design, and `render.render {"guidance": "ux-mockup", "format": "html", "paths": ["design-canvas/v1/project/canvas.json"], "source": "claude_design"}`
5. `ticket.format_choices` again.

## Expected
Check 2 of the round: the file renders to every other format the fidelity offers, and back, keeping what it holds. `ux.md` mockup outputs: `claude_design: "design-canvas/{version}/project/canvas.json"`.

## Actual
- Step 2: `[{"format": "claude_design", "content": "{}"}]`. No screen, region or control, no file written, and no word that the screens name no prototype.
- Step 3: six board entries (`screens/book-list.dc.html`: x, y, w, h, page, title), each naming a `.dc.html` file that does not exist. Still no regions, controls, transitions or stories, and nothing saved at `design-canvas/{version}/project/canvas.json`.
- Step 4: `ClaudeDesignScreensNotReadable: Claude Design screens are placed from the UX map; they are not read back.` A clear refusal, so there is no trip back.
- Step 5: the canvas chip says `"made": 1` for the hand-written `{}`.

So of the mockup's two offered formats only html holds the mockup; html to json and back is whole (checked: no difference but empty fields added).

## Tier that should catch it
Unit: `claude_design_ux_map_spec.py` checks the boards of screens that name prototypes; none renders a mockup whose screens name none, or checks where the result is saved.

## Answer (2026-11-23)

A mockup render to claude_design works and renders back. Built in `cdd_guidance/practices/ux/model/claude_design/nodes.py` (`ClaudeDesignUxMap.render` writes one prototype page per screen, `screens/<slug>.dc.html`, each an HTML mockup page of that screen, and `canvas.json` placing a board for each; `parse` joins the pages back into one map, refusing a missing page as `ClaudeDesignScreenMissing` and JSON that places no boards as `NotAClaudeDesignCanvas`), `cdd_guidance/actions/render/rendered_canvas.py` (`RenderedCanvas` saves the render into the canvas version being prepared, `design-canvas/version-N/project/`: the latest while unpublished, the first when there is none; a published version is refused with `PublishedVersion`, and a file there the format did not write, such as a ported screen, with `CanvasFileNotRendered`), `render.py`, `ux.py` (`UxFormats.read` reads the pages beside a canvas.json), `json/nodes.py` (`JsonUxMap.from_document`, `document`), `html/nodes.py` (`HtmlUxMap.carried_document`), `ux_map.py` (`content_beside`) and `harness/guidance/practice_formats.py` (`FormatAdapter.reads_file`); `ux.md` no longer says claude_design leaves out everything. Tested by `claude_design_ux_map_spec.py` ("a UX mockup rendered to a Claude Design canvas", html to claude_design to html answers the same mockup), `render_spec.py` ("that is a mockup in html, rendered to claude_design"), `render_saves_beside_source_heavy_spec.py` (the same trip through a real cdd server) and `format_trip_spec.py` (the mockup's example returns whole through claude_design); scenarios "Take a mockup to a Claude Design canvas and back", "Refuse to read a canvas that is missing a screen's prototype page" and "Leave a published canvas and a screen people ported as they are" in `story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md`.
