## Overview

The UX side of the Claude Design channel: the **Screens** page of the canvas, and the screens the story explorer shows. `ClaudeDesignUxMap` lays one board per prototype screen each on its own canvas page (1600×1100 plain frames rather than full-window pages, so the editor stays around them and leaving Play lands on the screen to edit it); the story explorer keeps the `screens` page. The story canvas beside it (`story_canvas.md`, `story_canvas.py`) lays out the story map and the explorer and holds the prototype-screen contract.

---

## Screens on the UX map

- **`screen-per-page`** — One `Screen` per product page the stories visit. Do not keep blank captures, landing steps ("is on", "returns to"), or the next story's page as a screen of this story; remove them from the graph, not only from the canvas.
- **`prototype-is-a-file`** — A screen ported to the canvas records its artboard in `Screen.prototype` (for example `select-sim.dc.html`); a screen known only from a capture records `Screen.image`. A prototype wins over an image wherever both exist.

## Story → screen edges

The UX map, edges included, is `ux/ux.json` in the workspace; each release's canvas is in the UX practice's root, `<ux root>/design-canvas/`.

- **`shown-on-edges`** — Link stories to screens with the cross-tree `shownOn` edge (`schema_edges.py`). An edge may sit on a step (`Screen.show_step`, key `Story › Scenario › Step`), a scenario (`Screen.show_scenario`, key `Story › Scenario`), or a story (`Screen.show_story`). The screen holds each one as a `StoryLink`, which holds the Stories node once it is on the screen's graph.
- **`edge-at-the-highest-true-level`** — Put the edge on the story when every scenario shows that screen; on a scenario when only some do; on a step only when a scenario moves across screens. The explorer cascades step → scenario → story, so a story-level edge covers every scenario without listing them.
- **`ux-ia-creates-edges`** — `/practices-ux` at **ia** creates and maintains these edges from the stories and the captures (for example a compare run's screenshots by story and step). Re-run it when the story map changes so the map's one thumbnail per story stays right.
