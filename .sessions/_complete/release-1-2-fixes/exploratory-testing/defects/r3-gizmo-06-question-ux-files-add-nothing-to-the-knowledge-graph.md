# Question: no UX file in any format adds a node or an edge to the knowledge graph, while 31 UX graph rules are listed and validate reports that they all passed

- **Charter:** Round 3 - UX (ia, mockup, front_end_code) in every format: generate, render, graph
- **Tester:** Gizmo
- **Story:** no scenario covers UX in the knowledge graph.
- **Module and class:** `cdd_guidance/practices/ux/ux.py` `UxReading` ("A working-copy load reads no UX files yet."), `harness/graph/graph.py` `Graph.load_files` / `inventory`, `cdd_guidance/actions/validate`.
- **Severity:** question (is UX meant to be in the graph in 1.2? If not, the inventory and the validation report should say that nothing was read)

## Steps
Sandbox `C:\dev\_et\round3\gizmo\work`, session `main` (`drv\a5.json`, `drv\c2.json`). The project holds the UX map in every form UX has: `bookshop/.context/information-architecture.drawio`, `bookshop/.context/ux-context.md`, `bookshop/buy-a-book.html` (carries the whole map), `ux/ux.json` and `bookshop/ux-map.json` (the map itself), `design-canvas/v1/project/canvas.json`, six `bookshop/src/*View.tsx`; and `.context/story-map.md` with the 11 stories the screens name.

1. `graph.load_files {"folder": "C:/dev/_et/round3/gizmo/work", "practices": ["ux", "stories", "clean_engineering"], "files": ["bookshop", ".context", "ux", "design-canvas"]}` -> "Loaded 16 edited files."
2. `graph.inventory {}`
3. `graph.return_nodes {"filter": {"practices": ["ux"]}}`
4. `graph.load_practice_roots {}`, then `graph.inventory {}` and `graph.explorer_trees {}`
5. `validate.validate {"guidance": "ux-ia", "paths": ["bookshop/.context/information-architecture.drawio"], "graph": true}`

## Expected
Check 4 of the round: a node for each thing in the file and an edge for each relationship. From `ux/ux.json`:

| Nodes | Expected | Found |
|---|---|---|
| UxMap / UxContext | 1 / 1 | 0 / 0 |
| Screen | 6 | 0 |
| Region | 13 | 0 |
| Control (3 of them StoryDemoControl) | 12 | 0 |
| Interaction | 4 | 0 |
| Transition | 7 | 0 |
| ContentType / NavComponent | 1 / 1 | 0 / 0 |

| Edges | Expected | Found |
|---|---|---|
| containment (map to screens, regions, controls, interactions, transitions, content type, nav, context) | 45 | 0 |
| transition from / to a screen | 14 | 0 |
| interaction and nav destinations | 6 | 0 |
| screen shows story, story shownOn screen | 11 + 11 | 0 |
| screen domain term to a class | 10 | 0 |

## Actual
- Step 2: `"ux": {"node_counts": {}, "edge_count": 0, "node_types": [], "edge_types": [], "rules": [31 names, ux.ContentType.conforms-to-schema ... ux.UxMap.story-domain-js-imported]}`. Stories: Epic 4, Story 11, 15 edges, none to a screen. Clean Engineering reads the views as 7 classes all named `_module` with 10 operations.
- Step 3: `[]`.
- Step 4: inventory `{"ux": {}}`; the explorer tree is one `ux` Practice node with no children.
- Step 5: "**No graph rule violations.** All scanned graph rules passed." although no UX rule had a node to run on (a screen named `Home` cannot be caught by `screen-names-use-domain-terms`).

Checks 5 and 6 of the round (the Files app's graph tree, a node's files) therefore have nothing to show for UX.

## Tier that should catch it
Heavy: no spec loads a UX file through `graph.load_files`; `ux_map_spec.py` puts a map on a graph in memory only.

## Also seen by
- Cog, round 3 second pass: the combined project: `ux` holds 0 nodes and 0 edges with `bookshop/` and `ux/` loaded, so the 11 story names and 10 domain terms on the six screens and the 12 controls' fields have no edge.
- Lens, round 3 second pass: in the Files app graph view the `ux` practice row has no twist and nothing under it with the 9 UX files listed (`bookshop/.context/ux-context.md`, `information-architecture.drawio`, `buy-a-book.html`, six `.tsx` views); selecting it answers no ranges and does nothing. The six views show under clean_engineering instead, as `_module` rows of a package `src`. Screenshot `C:\dev\_et\round3\lens\shots\20-u-practice-ux.png`.
