# cog-04 Rendering UX IA from its own ux/ux.json to drawio or whiteboard fails: the json map is read as a saved graph

**Title** - `render.render` of `ux-ia` with `paths: ["ux/ux.json"]` and `format: drawio` (or `whiteboard`) fails with `SavedGraphOutdated: ...\ux\ux.json is in shape None, not 7; load the working copy again.`, whether UX is on or off.

**Charter** - theme 7. **Tester** - Cog.

**Story** - Deliver Work With Context Guidance / Produce Formal Artifacts / Render Artifacts Into Other Formats. The UX ia fidelity declares `json: ["{epic}/ux-map.json", "ux/ux.json"]` and `drawio: "{epic}/.context/information-architecture.drawio"` (`cdd_guidance/practices/ux/ux.md` lines 72-76).

**Module and class** - `cdd_guidance/actions/render/render.py` *Render._saved_by_declared_paths* line 138: `if first.suffix == SAVED_GRAPH_SUFFIX and isinstance(worked, FidelityGuidance)` treats any `.json` source as a saved graph, then `rendered_file.py` *RenderedFile.from_graph* calls `SavedGraph.from_file`, which raises.

**Severity** - blocks work (the IA map in its own json format cannot be drawn; the error tells the person to reload the working copy, which does not help).

## Steps

Sandbox and server as in cog-01. `ux/ux.json` is a copy of `cdd_guidance/practices/ux/model/_examples/trip/ordering-ux-map.json`.

1. `render.render {"guidance":"ux-ia session=.sessions/checkout-flow/session.json","format":"drawio","paths":["ux/ux.json"]}`
2. The same with `"format":"whiteboard"`.
3. For comparison: `render.render {"guidance":"ddd-bounded-context session=.sessions/checkout-flow/session.json","format":"drawio","paths":[".context/bounded-context-map.md"]}`

## Expected

The IA drawn into a drawio file (and a whiteboard), saved at a declared place or beside the source, as the render docstring says: "A drawio, whiteboard, or markdown render is saved beside the first path ... under the path's own name" when the declared name cannot place it.

## Actual

Steps 1 and 2: `ERROR SavedGraphOutdated: C:\dev\_et\after-1-2-1\cog\work\repo\ux\ux.json is in shape None, not 7; load the working copy again.` Traceback in `work/repo/.sessions/main/session.err` ends in `render.py line 139 -> rendered_file.py line 163 SavedGraph.from_file -> saved_graph.py line 287`. Same answer with UX switched off (version 21) and on (version 22).

Step 3 saves `.context/bounded-context-map.drawio`, so render itself works.

## Tier that should catch it

Heavy (a real render of a UX json map through the cdd server). The render specs cover a saved `graph.json` as a source, and nothing renders a fidelity whose own declared format is json.
