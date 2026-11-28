# rivet-04 - A re-render rewrites canvas.json from scratch, dropping the boards people moved, the boards they added, and their notes

- **Title:** Re-rendering a story canvas (into the same unpublished version, or into the next version copied from a published one) throws away every edit people made to `canvas.json`: moved boards go back, an artboard they added is copied but no longer placed, and notes are emptied.
- **Charter:** 6. **Tester:** Rivet
- **Story:** breaks `update-the-existing-canvas` ("change its artboards there, and keep its pages, boards, and names") and `never-overwrite-a-published-canvas` ("merge their edits into the version's folder") in `cdd_guidance/practices/ux/model/claude_design/story_canvas.md`; the merged edits do not survive the next render. Story test `story_tests/build-design-canvas-screens/publish-and-release-a-canvas-version/` has no scenario for edits in canvas.json.
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/story_canvas.py` `ClaudeDesignStoryMap.drawn` (places every board afresh), `harness/design_canvas/canvas.py` `DesignCanvas._canvas_json` / `place` (ignores the project's existing canvas.json), written by `ProjectStoryCanvas.render` in `project_story_canvas.py`.
- **Severity:** wrong result - a person's layout and notes are lost without a word.

## Steps

1. Build and render `work/lern` (`C:\dev\_et\after-1-2-1\rivet\scripts\make_lern.py`, then `render_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern`), with `CDD_HOME` set to the sandbox.
2. Merge a person's edits into `version-1/project/canvas.json`: set `boards["screens/story-number-06.dc.html"].x = 55555`; add board `person-note.dc.html` (`{"x":1,"y":1,"w":100,"h":100,"page":"story-map","title":"My note"}`) and write that file; set `notes = {"n1":{"text":"person note"}}`.
3. Record a publish: `python C:\dev\_et\after-1-2-1\rivet\scripts\publish_local.py work/lern/ux https://example.invalid/fake-canvas-v1` (calls `CanvasVersion.publish_at` with an empty walk; nothing leaves the machine).
4. Re-render with no new screens, as the UX practice's `render_story_canvas` does: `python scripts\render_lern.py C:/dev/_et/after-1-2-1/rivet/work/lern noscreens`.
5. Read `version-2/project/canvas.json`.

The same loss happens without step 3, re-rendering into the unpublished version-1.

## Expected

version-2's canvas.json keeps story-number-06 at x 55555, keeps the `person-note.dc.html` board, and keeps the note, as the guidance tells agents to merge such edits into the folder before the next render.

## Actual

```
screens/story-number-06.dc.html -> {'x': 0, 'y': 1260, ...}   (moved back)
person-note.dc.html board       -> None                      (file copied into version-2, but placed on no page)
notes                           -> {}
```

Screen artboard files people edited (`screens/story-number-05.dc.html`) do survive, so only canvas.json is affected.

## Tier that should catch it

Unit (`story_canvas_spec.py` / `design_canvas_spec.py`): a render over a project folder whose canvas.json already holds moved boards, an extra board and notes. No spec gives `DesignCanvas` a project with an existing canvas.json.

## Also seen by
