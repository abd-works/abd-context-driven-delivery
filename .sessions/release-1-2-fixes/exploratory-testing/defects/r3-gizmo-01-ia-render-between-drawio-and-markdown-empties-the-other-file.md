# At UX ia, rendering the drawing to markdown empties ux-context.md, and rendering ux-context.md to drawio empties the drawing

- **Charter:** Round 3 - UX (ia, mockup, front_end_code) in every format: generate, render, graph
- **Tester:** Gizmo
- **Story:** no scenario covers a UX file's trip between the formats its fidelity offers.
- **Module and class:** `cdd_guidance/practices/ux/model/markdown/nodes.py` `MarkdownUxMap` (holds only scope, invariants, notes) and `model/drawio/nodes.py` `DrawioUxMap` (holds only screens, regions, transitions), written over the other format's file by `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.save`.
- **Severity:** wrong result (each render replaces a person's file with an empty one; after one trip both files are empty)

## Steps
Sandbox `C:\dev\_et\round3\gizmo\work`, session `main`, driver `C:\dev\_et\round3\gizmo\drv\run.py` (batches `a5.json`, `a6.json`). The two files of the ia fidelity, at the places `generate` names:

- `bookshop/.context/information-architecture.drawio`: 6 screens, 14 regions, 7 transitions (copy in `C:\dev\_et\round3\gizmo\orig\ia`).
- `bookshop/.context/ux-context.md`:

      # UX context

      Scope: Browse Books, Fill Cart, Check Out, Fulfil Order

      ## Invariants
      - A Cart Line shows one Book and its quantity.
      - An Order is shown as confirmed only after its Payment is taken.

      ## Notes
      - A Customer reaches the Cart from every screen through the Main Nav.
      - Deferred epic: Review Books stays off the screens.

1. `render.render {"guidance": "ux-ia", "format": "markdown", "paths": ["bookshop/.context/information-architecture.drawio"], "source": "drawio"}`
2. Put ux-context.md back, then `render.render {"guidance": "ux-ia", "format": "drawio", "paths": ["bookshop/.context/ux-context.md"], "source": "markdown"}`
3. Step 1 again on the drawing step 2 wrote.

## Expected
Check 2 of the round: a render turns the file into the other format the fidelity offers, and back, without losing what it holds. `ux.md` calls the channels "peers at the same fidelity; `transform` moves sideways". Where one format cannot hold what the other does, the render keeps what the file already there holds, or refuses.

## Actual
- Step 1 answers `bookshop\.context\ux-context.md`, which now reads, in full, `# UX context`. The scope, both invariants and both notes are gone; nothing of the drawing's screens is written either.
- Step 2 answers `bookshop\.context\information-architecture.drawio`, which now holds two pages, Detailed IA and Site Map, with 2 cells each and no screen, region or transition.
- Step 3 leaves both files empty of content.

No answer says anything was dropped.

## Tier that should catch it
Heavy (the drawing is written by `drawio_ux.mjs`): `drawio_ux_map_heavy_spec.py` and `markdown_ux_map_spec.py` each check their own format alone; none renders one fidelity's file to the other format over a file that is already there.

## Shares its cause with
widget-04, widget-08, widget-20 (the save writes the poorer text over the richer file).
