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
