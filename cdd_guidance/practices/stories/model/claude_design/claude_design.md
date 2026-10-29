## Overview

The Claude Design channel renders the story map, its scenarios, and the UX screens as one Claude Design canvas: a story map you can play, and a story explorer that runs real screens on the stories' own fixtures. Stakeholders walk the product story by story while the stories, the domain, and the screens stay one graph.

**Where things live.** In the workspace: each version of the canvas at `ux/design-canvas/version-N/project/` (artboards, `canvas.json`, `fixtures/`, `shots/`) and the UX map with its story → screen edges at `ux/ux.json`. In CDD: the generic canvas — `DesignCanvas` (pages, boards, `canvas.json`, writing to a folder), artboard and card helpers, the abd look, and the fixture bar — is `harness/design_canvas/`; this package lays out the story map and the explorer, and `ux/model/claude_design` lays out the Screens page.

Render it with the `claude_design` format: `ClaudeDesignStoryModel().render(story_map, workspace=..., screens=ux_map.screens)` returns every canvas file as JSON (path → text). The story map comes from the latest story map drawio; the screens come from the UX map (`ux.model.claude_design`). Do not hand-edit the rendered files: change the generator, re-render, and republish.

---

## Versions

- **`never-overwrite-a-published-canvas`** — People edit a published canvas directly in Claude Design. A regeneration never publishes over it: `CanvasVersions.working()` (`harness/design_canvas/versions.py`) starts `version-N+1` as a copy of the latest version, the generator renders into it, and that version is published as a new canvas titled `<name> — version-N`. `ux/design-canvas/versions.json` records each version's link. A version is regenerated in place only while it is unpublished, or when the user explicitly says to overwrite it.
- **`each-version-carries-its-files`** — Screens link stylesheets, fonts and images as relative files inside the version (`../styles/…`, `../assets/…`), never as `/_blob/…` uploads: an upload lives in one canvas's store, so a new version's canvas cannot see the uploads of the one before.
- **`generators-add-to-the-prepared-version`** — Screen generators write into `CanvasVersions.unpublished()`, which refuses a published version.

## Pages

- **`two-pages`** — `canvas.json` has two pages: **Story map** and **Screens**. The Story map page holds one artboard; the Screens page holds one board per prototype screen.
- **`one-map-artboard`** — The whole story map is one artboard (`Main.dc.html`) with one Play button. Do not split the map into an artboard per epic or story: many live artboards render hatched and slow.
- **`map-zooms`** — The map zooms with a trackpad pinch (ctrl + wheel) and its − / % / + buttons (`artboard(..., zoomable=True)`).

## Story map artboard

- **`map-mirrors-drawio`** — Lay the map out exactly as the story map drawio does: the same hierarchy, order, and scale. The latest drawio wins over older story code.
- **`epic-bars-span`** — An epic bar stretches across every sub-epic under it, drawn once. Sub-epic bars sit beneath, each spanning its stories. Never repeat an epic bar per sub-epic.
- **`abd-engineering-look`** — The map wears the abd engineering dark look (`LOOK` in `nodes.py`): `#0B0B0B` background, `#111113` cards, orange `#E5531A` for epic text, sub-epic fills, and the story card's inset rule; monospace labels. No white backgrounds or white buttons anywhere on the map or the explorer panel.
- **`one-thumbnail-per-story`** — Under each story, show one thumbnail: the story's main screen. Do not show the next story's screen, a thumbnail per transition, or a blank capture. No captions, no breadcrumbs.
- **`only-thumbnails-link`** — Story cards are not clickable. A thumbnail opens the story explorer deep-linked at that story, scenario, and step (`/screens/explorer.dc.html#story=…&scenario=…&step=…`).

## Story explorer

- **`screen-left-hierarchy-right`** — The explorer fills the frame (its board expands to fill): the live screen at browser size on the left, edge to edge, and the story hierarchy as a full-height panel on the right. Only the right panel wears the abd look; its styles are scoped (`sm-` prefixes) so they never reach the product screens, which keep their own stylesheets.
- **`collapsible-tree`** — The hierarchy is a collapsible tree — epic → sub-epic → story → scenario → step — with a small indent, plus *Collapse all*, *Reset*, *Play next*, and a button that hides the panel.
- **`back-to-story-map`** — The panel starts with a **← Story map** link back to `Main.dc.html`.
- **`outline-rows`** — An outline scenario (`Name: ${example}`) lists its example rows, read from the fixtures bundle's expanded scenarios; picking a row loads that row on the screen.
- **`selection-in-view`** — The selected row scrolls into view whenever the selection changes, including when a screen's button moves the explorer.
- **`group-steps-without-screens`** — A step with no screen of its own joins the next step that has one, so every row the reader picks shows a screen.
- **`screen-cascade`** — A step shows the screen it is `shownOn`; without one, its scenario's screen; without that, its story's screen. When no screen applies, show the step's screenshot, else *No screen for this step yet*.
- **`explorer-drives-the-screen`** — The explorer dc-imports each prototype screen with `story`, `scenario`, and `go` props. The screen loads the selected scenario's fixture itself, and `go(story)` moves the explorer to that story when a button on the screen leads there — the reader stays in the explorer.

## Prototype screens

A prototype screen is a real screen ported to a `.dc.html` artboard — the product's markup and stylesheets, not a sketch — that draws what the scenario's Givens stored. Build each one on the shared fixture bar in `harness/design_canvas/fixture_bar.py`:

- **`fixture-bar`** — Insert `BAR` at the screen's root and `methods(story, default_scenario, path)` into its `DCLogic` class; return `Object.assign(this.barVals(), {...})` from `renderVals`. Declare `story`, `scenario`, and `go` in `data-props`.
- **`no-auto-load-standalone`** — Opened on its own, a screen does not load a fixture: its list starts on *Load a scenario…*, so a reader can walk it by hand or pick a scenario to load. Inside the explorer the explorer's scenario loads automatically; picking another scenario there loads it and moves the explorer's tree to it.
- **`from-fixture`** — The screen implements `fromFixture(repositories, scenario, examples)`, returning the state the scenario shows. Read it from the repositories the Givens filled and from the example fixtures — never hard-code data the stories already hold.
- **`real-domain-logic`** — Buttons call the bundled domain objects (validate, verify, resend, select) and show their real messages; refusals come from the domain, not from copies in the screen.
- **`one-scenario-list`** — The bar holds one list, not a picker beside a paste box: every scenario of the story (an outline's example rows among them), then dev mode's seed paste for the screen's path. Picking a scenario does both jobs at once — it loads the scenario's fixture and types the values it enters (`fromFixture(...).entered` when the screen returns it, else its state) — so picking an invalid row shows the domain's refusal. Picking the dev seed types the seed paste through the screen's `paste(field)`, which maps each field (by the label it shows) into state.
- **`edit-from-the-explorer`** — Inside the explorer the bar ends with **Edit**, a link to the screen's own artboard. Each screen sits alone on its own canvas page as a plain frame (not a full-window page), so Edit moves Play to it and leaving Play (‹) lands on that page in the editor. A link cannot switch pages or open the editor itself; editing inside the explorer would change the explorer, which draws the screen through `dc-import`.
- **`story-panel-beside-the-screen`** — Each screen's page also holds a separate, read-only **Stories** board to the right of the screen: the whole hierarchy with the screen's own stories opened to their scenarios and steps, and every other epic, sub-epic and story collapsed and greyed out. Nothing in it links or edits; it only shows where the screen sits in the story map.
- **`follow-to-next-story`** — Links to the next screen call `follow(event, nextStory)`: inside the explorer it moves to that story and loads its fixture; standalone the link opens the next screen, which has its own picker.

The fixtures bundle — `CanvasFixtures` with `load(story, scenario)`, `scenarios(story)`, `examples`, `pasteFor(path)` — comes from the active pattern (`patterns/lern_domain_driven/practices/stories/model/claude_design/`).

## Steps

1. Load the story map from its drawio and the UX map (`ux/ux.json`, with its `shownOn` edges) into the graph.
2. Build the pattern's fixtures bundle into `project/fixtures/canvas-fixtures.js`.
3. Render with the `claude_design` format into the working version (`CanvasVersions.working()`), and pass `sources` (each story's and scenario's `path:line` from the practice graph) so the explorer can copy an open-in-file-viewer request.
4. Publish the version as a new canvas and record its link; port further screens into the next version the same way.
