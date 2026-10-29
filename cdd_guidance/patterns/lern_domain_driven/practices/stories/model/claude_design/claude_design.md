## Overview

LERN's part of the Claude Design channel: the fixtures bundle a canvas screen runs. `LernCanvasFixtures(workspace).build(story_names, out_file)` bundles the shared stories (`*.story.shared.ts`), their example fixtures (`*.examples.ts`), the in-memory domain repositories, and dev mode's seed overlay (`test-utils/seed-overlay/seed-pastes.ts`) into one browser script, `CanvasFixtures`, written to `ux/design-canvas/project/fixtures/canvas-fixtures.js`. Node-only modules (`*-node`, lowdb, Node built-ins, vitest) are stubbed, so all generic TypeScript runs in the browser.

---

## What a screen gets

- **`load(story, scenario)`** — Empties every repository and replays that scenario's Givens through the real story runtime; resolves to the repositories they filled.
- **`scenarios(story)`** — The story's scenarios, for the standalone picker.
- **`examples`** — Every example fixture export by name: outline rows, entered and expected values, refusal messages.
- **`pasteFor(path)`** — Dev mode's seed paste for a screen path, its `{unique}` values filled.
- **`repositories()`** — The in-memory repositories, for a screen opened before any fixture loads.

## Rules

- **`signed-in-from-the-examples`** — A screen that needs the signed-in customer or their cart loads it with the identity the example fixtures sign in with (for example the example customer profile's id), through the repositories' own `load` operations. Do not read repository storage directly.
- **`rebuild-with-the-stories`** — Rebuild the bundle whenever stories, examples, or domain code change, and republish it with the canvas; a stale bundle replays old Givens.
- **`no-new-fixtures-for-the-canvas`** — The canvas uses the stories' fixtures only. When a screen needs data no scenario sets up, the story is missing a scenario: add it there.
