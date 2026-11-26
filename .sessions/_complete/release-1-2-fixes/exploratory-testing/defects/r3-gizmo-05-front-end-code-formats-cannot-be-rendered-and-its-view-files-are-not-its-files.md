# UX front_end_code: neither format it offers can be rendered to or from, its default format is one it does not write, and the View.tsx files written for it are not listed as its files

- **Charter:** Round 3 - UX (ia, mockup, front_end_code) in every format: generate, render, graph
- **Tester:** Gizmo
- **Story:** no scenario covers the front_end_code fidelity's formats.
- **Module and class:** `cdd_guidance/practices/ux/ux.md` (`front_end_code`: `default_format: html`, `outputs: typescript, javascript`), `cdd_guidance/practices/ux/ux.py` `Ux.format_adapters` (no typescript or javascript), `space/session/practice_session_output.py` (the fidelity's files), `space/kanban/ticket_choices.py` `format_choices`.
- **Severity:** wrong result (three faults with one root: the fidelity's formats are declared but nothing reads or writes them)

## Steps
Sandbox `C:\dev\_et\round3\gizmo\work`, session `main` (`drv\c1.json`, `drv\c2.json`).

1. `generate.generate {"guidance": "ux-front-end-code"}` ends: "Save each format you write at its path ...: typescript: .../work/**/*View.tsx; javascript: .../work/**/*View.jsx".
2. Write six views there: `bookshop/src/BookListView.tsx`, `BookDetailsView.tsx`, `CartView.tsx`, `CheckoutView.tsx`, `OrderConfirmationView.tsx`, `OrdersToFulfilView.tsx`.
3. `ticket.format_choices {"ticket": "main", "fidelities": ["ux-front-end-code"]}`
4. `ticket.fidelity_files {"ticket": "main", "fidelities": ["ux-front-end-code"]}`
5. `fidelity-session-output.choose_format {"session": "main", "practice": "ux", "fidelity": "front_end_code", "format": "javascript", "is_chosen": true}`, then the same with `"format": "html"`, then steps 3 and 4 again.
6. `render.render {"guidance": "ux-front-end-code", "format": "javascript", "paths": ["bookshop/src/CheckoutView.tsx"], "source": "typescript"}`; the same with `source` left out; `"format": "typescript"` from `bookshop/buy-a-book.html` with `"source": "html"`.

## Expected
Check 1 and 2 of the round: a file is written in each format the fidelity offers, it is seen as that fidelity's file, and it renders to the other offered format and back. The practice builder's guidance says a practice without its own adapter "defers to the active fidelity's Clean Engineering companion".

## Actual
- Step 3: `[{"label": "code", "formats": ["typescript"], "offered": 1, "made": 0, "is_chosen": false}]`. javascript is not on the chip, nothing is chosen, and `made` is 0 with six `*View.tsx` files on disk.
- Step 4: the fidelity's files are listed under `markdown`, `html`, `drawio`, `claude_design` (the ia and mockup files it reviews); there is no `typescript` or `javascript` entry, and no `.tsx` file.
- Step 5: choosing javascript answers `"offered_formats": ["typescript", "javascript"], "chosen_formats": ["html", "javascript"]`; choosing html answers `FormatNotOffered: front_end_code does not write html; it writes typescript, javascript`. So html, the default, is among the chosen formats and is refused as a choice. Afterwards the chip reads `["javascript", "typescript"] ... "made": 0`, and step 4 is unchanged.
- Step 6: `ValueError: Unsupported format 'typescript'. Choose from: ['claude_design', 'drawio', 'html', 'json', 'markdown']` for both directions (to drawio the same text inside `RenderFailed: the render's worker process exited with 1`). With `source` left out the .tsx is read as html: `UxMapNotEmbedded: This HTML has no ux-map-json comment; render the map to HTML to read it back.`

`validate.validate {"guidance": "ux-front-end-code", "paths": ["bookshop/src"]}` does answer, with "No graph rule violations" and 8 AI rules.

## Tier that should catch it
Unit: `fidelity_outputs_spec.py` reads the declared outputs; no example checks that a fidelity's default format is one of its outputs, that each output's format has an adapter, or that a file matching `**/*View.tsx` is listed for the fidelity.

## Status: fixed (2026-11-23), one part kept as the person decided
- Already fixed before this pass (`b874f21ab`, `5c3b22e83`): front_end_code's default format is typescript, one of its outputs; UX has a `typescript` and a `javascript` adapter (*TypeScriptView*, *JavaScriptView*), which render a view into the other; a render between a view and a format of the UX map is refused as *ViewNotRendered* before a `.tsx` is read as a mockup page.
- Fixed now: the code chip of front_end_code said `made: 0` with views on disk, because `ticket.format_choices` counted the files a person reviews for the fidelity (its IA's and mockup's) rather than its own. It now counts each fidelity's own written files (`space/kanban/ticket_choices.py`).
- Covered by `space/kanban/kanban_tools_spec.py`, "with an action bar opened on its UX front-end code, a view written in the UX root": the code chip alone, the view counted as made (failed before the fix), and `ticket.root_files` naming `ux-front-end-code` among the fidelities whose file `CheckoutView.tsx` is. `harness/guidance/fidelity_outputs_spec.py` now checks, for every practice, that each fidelity's default format is one of its outputs and that each format it writes has an adapter that reads and writes it (both pass, since the earlier commits fixed them; they keep it so).
- Kept as the person decided on 2026-11-15 (`7af78a7cd`, "UX front-end code is reviewed through its IA and mockup, not its view code"): `ticket.fidelity_files` for front_end_code lists the IA's and the mockup's files, and the views are listed with Clean Engineering's code; `space/session/session_spec.py` "should leave its view code to Clean Engineering's review" holds that. Listing the views there too reverses that decision, so it waits on the person.
