# Draw Linked Models On The Canvas

Session `claud_design_enhancements`. Analysis and planning only: nothing here is implemented. This increment is one of the design canvas increments in the thin slice, which sets their order, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epics, features and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to; approaches, options and recommendations sit on the feature they decide.

| Increment | Epic → feature on the story map | Depends on | First slice |
|---|---|---|---|
| **13: Draw Linked Models On The Canvas** | Build Design Canvas Screens → Draw Linked Models On The Canvas | Nothing; can run beside 11 and 12 | Bounded context map as linked artboard |

The other design canvas increments: [Sync Design Canvas With Production](sync-design-canvas-with-production.md), [Integrate Stories With The Canvas Explorer](integrate-stories-with-the-canvas-explorer.md).

**Outcome:** from any story a person reaches its screen, its classes and its bounded context by clicking, and back, and every diagram matches its drawio layout.

## Epic: Build Design Canvas Screens

### Feature: Draw Linked Models On The Canvas

**Goal.** Domain model, class model and bounded context map sit beside the story map, linked to each other, so the canvas is a navigable surface over the whole model.

**Done means.** From any story you can reach its screen, its classes and its bounded context by clicking, and back. Every diagram matches its drawio layout, and a changed drawio shows on the next generation.

#### What exists

| Asset | Detail |
|---|---|
| Diagrams | pml-web has `src/.context/bounded-context-map.drawio` (85 cells), `domain-model.drawio` (125), and 11 module diagrams such as `subscription.drawio` (46) |
| Parsers and renderers | `DrawIOBoundedContextMap`, `drawio_aggregate_model`, `DrawIOCleanEngineeringModel`, `MiroCleanEngineeringModel`. There is **no `claude_design` format** for ddd or clean_engineering; only stories and ux have one |
| Links between practices | `harness/graph/schema_edges.py` lists `shownOn`, `specifiedBy`, `specifies`, `demonstrates`, `invokes`, `uses`, `dependsOn` and others. pml-web's `.context/graph.json` is 19.7 MB across 5 practices |
| Canvas parts | `box()` for cards, `artboard(zoomable=True)`, `LINK_KEY` keeps link hashes the canvas drops |
| Graph app | `harness/graph/app` is a React 18 Vite explorer with a `GraphView`. It depends on a Python server and Monaco, so it will not mount on a canvas as it is. Parts such as `kind-mark.tsx` may |

Related stories already on the map: Display Drawio File As Diagram (Graph app) and Trace Story Through Artifacts (Chat Bar) reach the same models from other surfaces.

#### Canvas rules that shape this

- A diagram is built from separate placed elements, not one `<svg>`, so each box can be selected.
- One small `<svg>` per straight arrow segment, with exact formulas in `diagrams.md`.
- **Arrows do not follow cards.** A person who moves a box must redo its arrows, so these diagrams are for reading and linking, not rearranging.
- `one-map-artboard` warns that many live artboards render hatched and slow. Mark diagrams `is_interactive` only if they need it.

#### Options

| Option | Strength | Weakness |
|---|---|---|
| **A. Literal elements from drawio geometry** | Selectable, linkable, same layout as the source, reuses parsers | Needs an arrow renderer and routing from drawio waypoints |
| **B. Export drawio to SVG** | Exact picture | One block in the editor; needs the draw.io CLI; links harder |
| **C. Embed a drawio viewer** | Native | No `<iframe>`, no network; would need a bundled viewer |
| **D. Auto-layout from the graph** | No drawio needed | Throws away human layout, contrary to `map-mirrors-drawio` |

**Recommendation: A.** It follows the rule that made the story map work: mirror the drawio exactly. Diagrams are derived from models, not production assets, so generating them does not conflict with Sync Design Canvas With Production.

#### Unknowns

- How many artboards before the canvas slows. Test with the 13 pml-web diagrams at slice 3.
- Whether drawio waypoints are clean enough to reuse, or whether some edges need rerouting.
- Whether the file limit stays comfortable. It should once Sync Design Canvas With Production removes duplicate shots.

#### Story: Draw Arrows From Drawio Waypoints

Slice 1.
- Add `arrow()` to `harness/design_canvas/canvas.py` from the `diagrams.md` formulas, splitting drawio waypoints into straight segments, one small `<svg>` per segment.
- Spec it on one card pair.

#### Story: Draw Bounded Context Map As An Artboard

Slice 2. The smallest diagram with the highest orientation value.
- Add a `claude_design` format to the ddd practice (`ddd.py` formats, `model/claude_design/`).

#### Story: Draw Domain Model As An Artboard

Slice 3.
- One artboard per diagram on a new `Models` page.

#### Story: Draw Module Class Models As Artboards

Slice 3.
- One artboard per module class model on the `Models` page.
- Add clean_engineering's `claude_design` format, sharing the layout code with the ddd format.

#### Story: Follow Links From A Context To Its Models

Slice 4.
- Context → its domain model → module class model, using `<a href>` with `LINK_KEY`.
- Hashes select the target node on arrival.

#### Story: See The Classes A Scenario Touches

Slice 5.
- From a scenario in the explorer, show the classes it touches, using `specifiedBy` and `invokes` from the graph.
- Export only the edges needed, since the full graph is 19.7 MB.
- Check which edges are actually populated; I read the edge names, not their contents.

#### Story: See The Stories That Exercise A Class

Slice 5.
- From a class, list the stories that exercise it, from the same exported edges.

#### Story: Mark Model Nodes That Fail Rules

Slice 6, optional.
- Badge nodes that fail rules, using the graph's `violations: true` filter.
