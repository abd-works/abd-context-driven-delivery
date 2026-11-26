# Generate tells the agent to save thin-slice.md and thin-slice.drawio, but the thin slice cannot be chosen, has no template in the answer, and rendering thin-slice.md to drawio writes over story-map.drawio

- **Charter:** Round 3 - Stories (story_map, scenarios, acceptance_tests) in every format, checks 1, 2 and 4
- **Tester:** Sparky
- **Story:** epic "Deliver Work With Context Guidance"; no scenario covers the story map's thin slice output.
- **Module and class:** `cdd_guidance/practices/stories/stories.md` (story_map `outputs: thin_slice`), `cdd_guidance/actions/generate/generate.py` (the save line), `cdd_guidance/actions/render/rendered_file.py` `RenderedFile.save`, `cdd_guidance/practices/stories/model/drawio/nodes.py` `DrawIOStoryModel.save_thin_slice` (no caller outside the adapters).
- **Severity:** wrong result (a format the fidelity names is never written, and trying to write it replaces another file)

## Steps
Sandbox `C:\dev\_et\round3\sparky\work`, session `main`, throwaway cdd server (`C:\dev\_et\round3\sparky\drv\go.sh`, calls in `drv\a3.json` and `drv\b1.json`). `.context` holds `story-map.md` (4 epics, 16 stories), `story-map.drawio` rendered from it, and `thin-slice.md` written after `templates/md/thin-slice.md` (two increments naming nine of the map's stories).

1. `generate.generate {"guidance": "stories-story-map"}`
2. `fidelity-session-output.choose_format {"session": "main", "practice": "stories", "fidelity": "story_map", "format": "thin_slice", "is_chosen": true}`
3. `render.render {"guidance": "stories-story-map", "format": "drawio", "paths": [".context/thin-slice.md"], "source": "markdown"}`

## Expected
A format generate tells the agent to save is one the fidelity offers, with a template to follow, and a render of `thin-slice.md` to drawio writes `.context/thin-slice.drawio`, the name `stories.md` gives it (`thin_slice: [".context/thin-slice.md", ".context/thin-slice.drawio"]`), leaving `story-map.drawio` alone.

## Actual
1. The answer ends "Save each format you write at its path ...: markdown: .../.context/story-map.md; drawio: ...; whiteboard: ...; thin_slice: .../.context/thin-slice.md, .../.context/thin-slice.drawio". The only template in the answer is the story map's; the words "Thin slicing" are nowhere in it.
2. `FormatNotOffered: story_map does not write thin_slice; it writes markdown, drawio, whiteboard`.
3. `[{"format": "drawio", "path": "...\\.context\\story-map.drawio"}]`, no error. `story-map.drawio` now holds two epic cells, "Product / context" and "Increments" (the thin slice's `##` headings read as epics), and none of the map's 24 cells. No `thin-slice.drawio` exists. Nothing in `cdd_guidance/actions/render` calls `save_thin_slice`, so no call I found draws the increments.

The scenarios fidelity does the same with `realization`: generate's save line names `.context/{scope}-scenario-realization.md`, and `choose_format` with `realization` answers `FormatNotOffered: scenarios does not write realization; it writes python, typescript, markdown`.

Step 3's overwrite is the cause reported in widget-06 (the saved name comes from the fidelity, not the file rendered); what is new here is that the file is one the fidelity itself names as its output.

## Tier that should catch it
Heavy (`render_saves_beside_source_heavy_spec.py`): no example renders a thin slice beside its story map. Unit on generate's save line: no example checks that every format it names is one `offered_formats` holds.
