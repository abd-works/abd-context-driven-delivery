# Rivet - theme 6, story canvas and story explorer

Sandbox `C:\dev\_et\after-1-2-1\rivet` (notes in `notes.md`, scripts in `scripts\`, screenshots in `shots\`). Data: `work/lern` (45-story LERN project: Story 02 without a shared story, Story 03 without a screen, Story 04's screen linked to one scenario only), `work/lern-noux`, `work/lern-odd` (odd names), `work/self` (this repository's story map, 600 stories). Port 8951-8952 for the static server Playwright opened. Nothing published.

## Defects

| File | Severity | Gist |
|---|---|---|
| rivet-01-walk-finds-value-in-scenario-list.md | wrong result | The walk reads the fixture bar's scenario list, so a value in a scenario's name counts as shown: the publish gate passes screens that never draw it. Worst one. |
| rivet-04-rerender-drops-canvas-json-edits.md | wrong result | Every render rewrites canvas.json: moved boards, added boards and notes people made are lost, even after merging them into the version as the guidance says. |
| rivet-02-story-without-fixture-renders-silently.md | misleading / question | A story with no shared story renders an empty screen; only the console says the story was not loaded. |
| rivet-03-scenario-screen-has-no-story-panel.md | wrong result | A screen linked by scenario (or step) only gets no Stories panel and no thumbnail on the map. |
| rivet-05-no-ux-folder-raw-file-not-found.md | misleading / question | No UX folder: raw FileNotFoundError; empty ux.json: bare JSONDecodeError; `{}` renders a map with no screens and no warning. |
| rivet-06-relative-project-root-doubles-fixtures-path.md | misleading | A relative project root doubles the fixtures build script's path. |
| rivet-07-double-braces-in-names-vanish-from-map.md | cosmetic | `{{...}}` in a name is evaluated by the x-dc template on the map and panels. |

## What held

- More than 40 pages: 44 screens share one Screens page in rows, each with its panel (`screens-within-the-page-limit`).
- A story with no screen and a scenario with no screen: the explorer shows "No screen for this step yet" (explorer logic run in Node).
- Screen artboards people edited survive a re-render; two identical renders give byte-identical files.
- This repository's map: 600 stories and 1,059 scenarios render in under a second.
- `&`, quotes, `<`, `›` in names are escaped and play in the explorer.
- Whiteboard class cards: ops-only, props-only, empty and unicode classes round-trip.

## Confusing

- Opening a canvas "in a browser through Playwright" shows little: `.dc.html` needs Claude Design's `support.js`, which is not in the repository, so pages show raw `{{...}}` templates. The only local renderer is the walk's `screen_render.cjs`, which I used to read what screens, map and panels show.
- With `keep_one`, the title becomes `ux-mockup` instead of `ux-mockup.version-N`, so the first render after turning it on lists canvas.json as changed. Probably intended.

## Not reached

- The Files app's linked-file pane (needs the cdd server and a Files app build) and `render_story_canvas` called through the cdd server.
- Real browser play of the explorer and screens with the Claude Design runtime: for the person, in Claude Design.

## Where the risk still is

The walk is the only gate before publishing, and rivet-01 shows it reads text that is not the product's screen; anything else the fixture bar draws (story name, "Load a scenario...") can leak in the same way. The merge of people's edits (rivet-04) is promised in guidance but nothing in code keeps them, so the first real re-render after a person reorganises a published canvas will undo their work.
