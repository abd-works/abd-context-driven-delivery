# A mockup rendered to drawio and read back has none of its 12 controls, states, interactions or story steps, and has a region nobody wrote, named after two buttons

- **Charter:** Round 3 - UX (ia, mockup, front_end_code) in every format: generate, render, graph
- **Tester:** Gizmo
- **Story:** no scenario covers a mockup's trip through its drawing.
- **Module and class:** `cdd_guidance/practices/ux/model/drawio/nodes.py` `DrawioRegion.cli_record` (writes a region's controls as field and action cells) and `DrawioScreen.read_regions` / `DrawioRegion.from_cell` (reads every framed cell in a screen's box as a region).
- **Severity:** wrong result

## Steps
Sandbox `C:\dev\_et\round3\gizmo\work`, session `main` (`drv\b2.json`, `drv\c1.json`). `bookshop/buy-a-book.html` is the mockup of `ux/ux.json`: 6 screens, 13 regions, 12 controls (button, number, text, dropdown, checkbox, list, bound-list; 3 Story Demo controls with story steps), 9 states, 4 interactions with a destination screen, 7 transitions. Screen Book Details has the regions Book Summary and Add To Cart; Add To Cart holds Quantity (number) and the buttons Add to cart and Back to list.

1. `render.render {"guidance": "ux-mockup", "format": "drawio", "paths": ["bookshop/buy-a-book.html"], "source": "html"}` -> saved `bookshop\buy-a-book.drawio`.
2. `render.render {"guidance": "ux-mockup", "format": "json", "paths": ["bookshop/buy-a-book.drawio"], "source": "drawio"}` (the same map `html` would carry; saved as `C:\dev\_et\round3\gizmo\trip\mockup\drawio-back.json`).

## Expected
`ux.md`, mockup: "drawio remains a peer channel". The drawing shows the controls (cells `Quantity`, `Add to cart · Back to list`, `Street`, `[Pay]`), so reading it gives them back as controls of their regions, or the read says what it leaves out.

## Actual
After step 2: 6 screens, 7 transitions, 0 controls, 0 states, 0 interactions, 0 story steps, and 14 regions. Book Details now has three regions: `Book Summary`, `Add To Cart`, and `Add to cart · Back to list`, the cell that drew the two buttons. The other control cells (`Book title · Price`, `Quantity`, `Street`, `City`, `Country`, `Card number`, `Save this card`, `[Pay]`) are dropped; the first two are drawn twice in the drawing. Story names, domain terms, layouts, descriptions, areas, the content type, the nav component, scope and notes are lost as in r3-gizmo-02. The compare of the map before and after lists 163 differing values of 204.

## Tier that should catch it
Heavy: `drawio_ux_map_heavy_spec.py` draws regions without controls; no example reads back a drawing of regions that hold controls.

## Status: fixed (2026-11-23)
- Already fixed before this pass (`b874f21ab`, `5c3b22e83`): a cell that shows controls (`uxControls`, an unframed row, or the grey action strip) is read as controls of the region above it, never as a region, each with its type; a list's row drawn twice is read once; what each control serves is read from the callout's `Region › Control serves …` lines.
- Fixed now, found by running the steps' mockup (`buy-a-book.html`) through the drawing again: the render failed outright (`AttributeError: 'StoryDemoControl' object has no attribute 'row_label'`) on any mockup holding a Story Demo control, since a draw.io map copied a Story Demo control as the plain model class. *DrawioUxMap* now makes it a *DrawioStoryDemoControl* (`model/drawio/nodes.py`), drawn as any other control.
- Fixed now: a control whose name is not its label (`Add To Cart Button` shown as `Add to cart`) came back named by its label, so the callout line naming it by its name found no control and what it serves was dropped. The drawing keeps, beside each row's and action strip's labels, the name of each control named otherwise (`uxNames`, written by `drawio_ux.mjs`), and reads it back; a control named as it is labelled keeps no name, so relabelling it in draw.io renames it.
- After the fix the steps' trip differs in 67 of 222 values, each one the drawing does not show and the fidelity's `leaves_out` names: a control's states, interactions, bound field and story steps (a Story Demo control reads back as a plain control), descriptions, content types, nav components, references, scope, notes and the map's name. `ux.md`'s `leaves_out` for drawio now names the bound field, the Story Demo control and the map's name, which it did not.
- Covered by `drawio_ux_map_spec.py`: "of a mockup whose controls are named otherwise than they are labelled, that is read back", and "a region of a UX map drawn as draw.io" / "that holds a form whose button runs story steps"; and by `drawio_ux_map_heavy_spec.py`: "of a mockup whose controls are named otherwise than they are labelled, one a Story Demo control, that is read back" (a real render through the command line and back; it failed before the fix).
