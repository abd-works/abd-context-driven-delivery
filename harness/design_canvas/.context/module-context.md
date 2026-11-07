# harness/design_canvas
*DesignCanvas* is a Claude Design canvas written as files: its pages, the boards placed on them, and the artboard files they show, with the `canvas.json` that ties them together. A practice lays out its own artboards — the story map, the screens — with the helpers `artboard(...)`, `box(...)`, and `thumbnail(...)` and the shared look in `harness.design_canvas.look`, hands them to a *DesignCanvas*, and the canvas decides where every file goes and writes them.
*CanvasVersions* keeps numbered versions of a canvas (`version-1`, `version-2`, ...) under a release's `design-canvas` folder, because people edit a published canvas directly: generating again starts the next version instead of writing over one that is published, and writing into a published version fails with *PublishedVersion*.

- **Purpose:** Let a practice publish its views as a Claude Design canvas without knowing the canvas's file layout, and regenerate it without overwriting what people edited.
- **Seam (terms):** DesignCanvas, CanvasVersions, PublishedVersion; `artboard(...)`, `box(...)`, `thumbnail(...)`; the look `LOOK`, `FONTS`, `BACKGROUND`
- **Dependencies (one-way):** harness/name (*Name*), space/work_state (the release folder a canvas's versions are kept in). Nothing in harness imports it back; cdd_guidance/practices/stories (`model/claude_design`) uses it.

## Constraint

Lay out artboards in the practice that owns them and give the canvas only finished artboards, so the canvas stays the same for every practice. Write a canvas only through `DesignCanvas.write`, and regenerate a published canvas only by starting a new version through *CanvasVersions*, never by writing into the published one.
