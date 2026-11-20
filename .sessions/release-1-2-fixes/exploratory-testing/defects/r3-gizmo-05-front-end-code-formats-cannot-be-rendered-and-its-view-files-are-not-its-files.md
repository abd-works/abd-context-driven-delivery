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
