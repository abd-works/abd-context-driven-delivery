## Overview

LERN's part of the Claude Design channel: the fixtures bundle a canvas screen runs. `LernCanvasFixtures(workspace).build(story_names, out_file)` bundles the shared stories (`*.story.shared.ts`), their example fixtures (`*.examples.ts`), the in-memory domain repositories, and dev mode's seed overlay (`test-utils/seed-overlay/seed-pastes.ts`) into one browser script, `CanvasFixtures`, written to the version's `project/fixtures/canvas-fixtures.js` under the UX practice's root, `<ux root>/design-canvas/`. Node-only modules (`*-node`, lowdb, Node built-ins, vitest) are stubbed, so all generic TypeScript runs in the browser.

---

## The story runtime it needs

The bundle replays each scenario through the project's own step library, `test-utils/story-test/`, by installing a story host that records each scenario's Givens and Whens instead of running them. The LERN pattern ships that runtime as `templates/test-utils/story-test/story-test.ts`; copy it into the step library folder when the project has none. `build` checks the contract first (`StoryRuntimeContract` in `story_runtime.py`) and stops with `StoryRuntimeMissing`, naming each missing piece, before it writes anything:

- `story-test.ts` exports `installStoryHost`, `withStory`, and `storyBindings`.
- The host's `it(name, fn, steps)` is given `{ whens }`, the When steps that Then runs before its body. Without them a screen past an action would show the Givens alone.
- `repositories.ts` beside it exports `domainRepositories()`, the in-memory repositories the bundle resets and replays onto.

A bundle built without any of these still loads, but its fixtures skip every action and hand the screens nothing, and nobody can tell from the canvas; stopping names what to fix.

## What a screen gets

- **`load(story, scenario)`** — Empties every repository and replays that scenario's Givens through the real story runtime; resolves to the repositories they filled.
- **`scenarios(story)`** — The story's scenarios, for the standalone picker.
- **`examples`** — Every example fixture export by name: outline rows, entered and expected values, refusal messages.
- **`pasteFor(path)`** — Dev mode's seed paste for a screen path, its `{unique}` values filled.
- **`repositories()`** — The in-memory repositories, for a screen opened before any fixture loads.

## Rules

- **`runtime-before-fixtures`** — Give the project the LERN story runtime before building the bundle: when `build` stops with `StoryRuntimeMissing`, copy or merge the pattern's `templates/test-utils/story-test/story-test.ts` into the step library and export `domainRepositories()` from `repositories.ts`, then build again. Never edit the generated entry to get past the check; the screens would draw fixtures without the scenario's actions.

- **`signed-in-from-the-examples`** — A screen that needs the signed-in customer or their cart loads it with the identity the example fixtures sign in with (for example the example customer profile's id), through the repositories' own `load` operations. Do not read repository storage directly.
- **`rebuild-with-the-stories`** — Rebuild the bundle whenever stories, examples, or domain code change, and republish it with the canvas; a stale bundle replays old Givens.
- **`no-new-fixtures-for-the-canvas`** — The canvas uses the stories' fixtures only. When a screen needs data no scenario sets up, the story is missing a scenario: add it there.
