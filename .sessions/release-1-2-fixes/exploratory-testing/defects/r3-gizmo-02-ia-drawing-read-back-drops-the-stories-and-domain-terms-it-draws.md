# The IA drawing shows each screen's stories and domain terms, but reading the drawing drops them, with the layouts, nav components, content types and the map's name

- **Charter:** Round 3 - UX (ia, mockup, front_end_code) in every format: generate, render, graph
- **Tester:** Gizmo
- **Story:** no scenario covers a UX map's trip through its drawing.
- **Module and class:** `cdd_guidance/practices/ux/model/drawio/nodes.py` `DrawioUxMap.read_pages`, `DrawioScreen.from_cell` and `_is_annotation` (a cell starting `Stories:` or holding `Domain terms:` is skipped, not read into the screen above it).
- **Severity:** wrong result (the links from a screen to its stories and to domain things do not survive the fidelity's default format)

## Steps
Sandbox `C:\dev\_et\round3\gizmo\work`, session `main` (`drv\a3.json`, `drv\a7.json`). `bookshop/ux-map.json` holds the Bookshop map: 6 screens, 13 regions with areas, 7 transitions (one `top nav`), 11 story names, 10 domain terms, 6 layouts, 6 descriptions, 1 content type, 1 nav component with 2 destinations, scope, 2 notes, 2 invariants.

1. `render.render {"guidance": "ux-ia", "format": "drawio", "paths": ["bookshop/ux-map.json"], "source": "json"}`, and move the drawing to `bookshop/.context/information-architecture.drawio`.
2. Open the drawing: on the Detailed IA page each screen has a cell such as `Stories: Browse Book List · Search Books  Domain terms: Book`.
3. `render.render {"guidance": "ux-ia", "format": "json", "paths": ["bookshop/.context/information-architecture.drawio"], "source": "drawio"}`

## Expected
`ux.md`, ia: "Screens, layouts, named regions, transitions, nav components, content types. Story names and domain terms attach as traces." The drawing is ia's default format, so what ia holds is read back from it; at the least the stories and terms the drawing itself shows.

## Actual
Step 3's map, against step 1's source:

| Held | Before | After |
|---|---|---|
| screens / regions / transitions | 6 / 13 / 7 | 6 / 13 / 7 |
| story names on screens | 11 | 0 |
| domain terms on screens | 10 | 0 |
| screen layouts, descriptions | 6, 6 | 0, 0 |
| region areas | 13 | 0 |
| transition `View cart` nav type | top nav | action |
| content types, nav components | 1, 1 | 0, 0 |
| scope, notes, invariants | 1, 2, 2 | 0, 0, 0 |
| map name | Bookshop | UxMap |

The module's own docstring says "layouts, story names, and controls stay in the JSON and HTML formats", but no fidelity offers JSON (ia offers drawio and markdown), so at ia nothing a person is offered keeps them.

## Tier that should catch it
Heavy: `drawio_ux_map_heavy_spec.py` checks screens, regions and transitions after a trip; no example checks the stories and terms the drawing shows.

## Status: fixed (2026-11-23)
- Already fixed before this pass (`b874f21ab`, `5c3b22e83`): the IA drawing read back keeps each screen's stories, scenarios, steps and domain terms (read from the callout under the screen), its layout (`uxLayout`), each region's area (`uxArea`) and each transition's kind of navigation (`uxNav`). Covered by `cdd_guidance/practices/ux/model/drawio/drawio_ux_map_heavy_spec.py`, "a UX map drawn as a draw.io information architecture" / "that is read back" (a real render through `drawio_ux.mjs` and back), and the same subject in `drawio_ux_map_spec.py` on a drawing as the command line writes it.
- Checked again now on the Bookshop map of the steps (`ux-map.json` -> drawio -> map): 19 of 137 values differ, and every one is something the drawing does not show: the map's name, scope, notes and invariants, the screens' descriptions, the content type and the nav component. A drawing round trip keeps what the drawing shows.
- Fixed now: the map's name was the one thing lost that the fidelity did not say it leaves out. `ux.md`'s `leaves_out` for drawio at ia and mockup now names it, so the render and the format trip say the drawing does not hold it.
- Left as declared, not drawn: content types and navigation components are ia content (`ux.md`, ia Guidance), but the drawio-ux command line has no shape for them, and the fidelity's `leaves_out` says they stay in `ux-map.json`. Drawing them is new work on `drawio_ux.mjs` (a shape for each, and a reader for it), not a fix of what the drawing already shows.
