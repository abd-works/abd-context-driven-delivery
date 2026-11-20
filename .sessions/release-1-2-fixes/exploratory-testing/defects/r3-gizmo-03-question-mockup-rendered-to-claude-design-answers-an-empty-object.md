# Question: a mockup rendered to claude_design, the second format the fidelity offers, answers `{}`, writes no canvas.json, and cannot be rendered back

- **Charter:** Round 3 - UX (ia, mockup, front_end_code) in every format: generate, render, graph
- **Tester:** Gizmo
- **Story:** no scenario covers a mockup's trip between html and claude_design.
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/nodes.py` `ClaudeDesignUxMap.save` / `boards` / `parse`.
- **Severity:** question (is claude_design a format a mockup can be rendered to, or only one an agent builds by hand on a canvas?)

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
