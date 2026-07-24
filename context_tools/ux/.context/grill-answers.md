# UX migration — grill decisions (2026-07-17)

## Fidelities
- `ia → mockup → specification → code`.
- Drop impact-map from this generator (sketch covers shaping).
- **code** (added 2026-07-20): real frontend wired to real backend — not Story Demo / greybox alone. A vertical is not at code while CE is Fake/demo-only or UX is still mockup/spec.

## When wiring starts
- **Agreed:** wire at **mockup**. Mockup produces a runnable native web artifact (semantic HTML + stub interactions, greybox / no brand).
- **Specification** deepens: brand tokens, richer stubs, AC demo paths.
- **Code** replaces stubs with production UI + real service calls (CE **code** / Production collaborators).
- Host UI stacks (React/Vue/…) are optional peer channels via `transform` — not required to get the mid-fi loop; typical at **code**.

## Canonical model
- **Agreed:** `UxMap` → `Screen` → `Region` → `Control` (plus transitions, content types, story/domain traces as model fields).
- Markdown / drawio / html (and later host stacks) are peer channels that parse/render the model.
- Scanners read model fields only — never file syntax.
- **No ARIA pipeline** — drop `aria.yaml` as a deliverable and as an intermediate fidelity layer. Structure lives on the typed model; html/drawio render from controls/regions directly.

## Formats
- Same **model ↔ channel conversion architecture** as Clean Engineering / Stories: canonical `UxMap` model; peer channels parse/render; `transform` moves sideways at the same fidelity.
- Defaults:
  - **ia → drawio** (diagram stays primary). HTML optional via transform / channel.
  - **mockup → html+js** (default). Keep diagramming as peer drawio channel.
  - **specification → html+js+css**.
  - **code → production frontend** (host stack and/or html channel with real API wiring).
- Peer channels: markdown, json, drawio, html+js, html+js+css (and later host stacks).
- Review shell: **mockup on the left side of the screen** (interactive surface). Story Demo remains a review shell; at **code** it is not the shipping UI.

## Regeneratable / write-once
- Mockup/specification stay regeneratable from the model. **Code** may live in the host app stack; still no “don’t regen” trap on the UX model — production FE is the deepen, not a freeze of greybox HTML.
- Regeneration / `transform` is for **converting** between peer formats from the canonical model.

## Object model (language sketch)
- Saved: `context_tools/ux/.context/ux-model-sketch.md` (Clean Engineering sketch notation).
- Spine: `UxMap` → `Screen` → `Region` → `Control`.
- `Transition` / `ContentType` / `NavComponent` are **`UxComponent` subtypes**.
- Collections **`Transitions` / `ContentTypes` / `NavComponents`** (`UxComponentCollection`) own `append` / `remove` / `find` — not flat append ops on `UxMap`.
- **`story_references` / `object_references`** are properties on `UxMap` — each stores **paths** to JS artifacts (not module bodies). Bind/dedupe behind the property. Object = CE object-model JS; domain language not built yet.
- Conversion: `UxChannel.parse` / `render`; `Ux.transform` wires source→canonical→target.
- Interactions live on `Control` (trigger / effect / destination) — deepened at mockup with JS.

## Web channel
- **One `html` channel** — deepens by fidelity (mockup: html+js greybox; specification: css/brand; code: real frontend / host stack). Not two transform targets.
- Update sketch: collapse `HtmlJsUxChannel` / `HtmlJsCssUxChannel` → `HtmlUxChannel`.

## Stories + domain in the HTML surface
- **Not names-only.** When object models and stories exist, bring them into **JS** so screens can connect to domain models for enter/display.
- **Stories:** import the actual story file(s); read story names from the story code. For now, **render story names at the bottom of the page only**.
- **Later:** simple injection of example data onto the screen, and trace stories through mockup/spec.
- Domain JS + story JS are part of the wired mockup/spec loop — not just annotation strings on `Screen`.
- **JS production (agreed):** reuse Stories / Clean Engineering channels — **do not** invent a UX adapter shape.
  1. Check whether JS format already exists for the in-scope stories / domain model.
  2. If missing, run that generator’s existing **`transform`** (Stories and CE both already have `javascript` channels).
  3. HTML surface imports those JS modules.

## Artifact layout (mirror Stories — colocated)
```
sandbox/<epic>/
  ux-map.json
  <user-goal>.html
  <sub-epic>/…stories…
  .context/
    information-architecture.drawio
    ux-sketch.md
    ux-context.md
```
- **ia:** `.context/information-architecture.drawio` (drawio-ux CLI, two pages).
- **mockup+:** one HTML per concrete user goal at epic/sub-epic (beside stories).
- **sketch/context:** `.context/` (same as other generators).
- Story/object JS stay where Stories / CE emit them; HTML imports them.
- Not: a separate `context_tools/ux/` package folder; not one file per individual screen.

## Markdown role
- MD is a good scratch pad for **stories / specs / OO language** — it **sucks as primary UX surface**.
- UX flow: **drawio (IA) → html (mockup/spec)**. MD is **not mandatory** and not the authoring path for screens.
- Keep optional MD only for info **not easily accessible on screens** — same idea as story-context / module-context: thinking, interactions to capture, invariants, notes. Not a full IA/mockup document.

## Scaffold
- **Agreed to scaffold** (2026-07-17): `context_tools/ux/` package like stories — `ux.py`, `ux.md`, sketch-template, `ux_model/`, channels (drawio/html/md/json), scanners, templates.
- Leave `abd-skills/context_tools/user-experience-design` in place (do not delete).
- Cursor skill: `.cursor/skills/context_tools/ux/SKILL.md`.
- Drawio channel: vendored **drawio-ux CLI** (`context_tools/ux/diagram/drawio/drawio_ux.mjs`) — same engine as abd-skills IA. `render` writes Detailed IA + Site Map (not stuffed blue boxes).
- Next: richer html DOM parse; more abd-skills rules as scanners.

## Sketch annotations
- **No margin fidelity tags** (`<-i` / `<-m` / `<-s`). Declare fidelity once at the top. Do not annotate sketch lines.

## Layout catalog
- **Thin registry only** (`ux_model/layouts.py`): layout id → slots (+ aliases). Seed via `Screen.apply_layout`.
- Source: abd-skills `screen-templates` vocabulary — **do not** bulk-import ASCII/drawio fragments.
- HTML uses `data-layout` for a few structural grids (sidebar, split-screen, holy-grail, tabbed).

## Deferred
- Review shell right-side contents (annotations vs demo controls) — revisit later.
- Example-data injection + story-through-mockup/spec tracing (explicitly later).
- Expanding layout catalog beyond core IA patterns when mockup needs them.

### Story demo ? Play runs story GWT; interactive shares same UI and helpers

Play path: run the story's given/when/then functions (not a parallel UI-only path). UX is bound to stories as explicitly as possible ? the same step bodies that prove the story drive the mockup.

Interactive mode: same HTML/UX shell. Prefer the same helpers/functions used by the story tests (helpers ? ExampleFactory). Navigation and clicks use basic HTML/JS on top of that shared surface; they do not invent a second domain API.

### Story demo ? story owns domain; paint layer reflects

How a Play step reaches the mockup: A ? story owns domain only.

Story given/when/then mutate domain via helpers/factories (same as tests). A small paint/reflect layer reads domain state and updates the mockup DOM. Play does not rely on steps returning view DTOs, and does not use a per-step paint map as the primary binding.

Interactive mode benefits: same domain objects; clicks can keep mutating via the same helpers after Given has loaded the world.

### Story demo ? dual runner for Play

Play seam: dual runner (not named step exports).

story-test collects given/when/then closures into an ordered steps[] and exposes play/playNext for the demo shell. Node test path still wraps the same steps with describe/it/before. Story files keep inline GWT bodies; they return runnables so Play can step them.

Browser needs a play-safe entry that does not load node:test at import time (core collect+play vs node wrapper). Then asserts soft-fail via try/catch (or a small assert shim). Paint/reflect runs after each playNext from domain state the closures mutate.

### Story demo ? world bag + step-to-control highlight

Chosen (agent) so dual-runner Play is implementable without named step exports or view DTOs.

World / paint: each scenario play session owns an explicit world bag. Story steps mutate world (character, bundle, ?) instead of bare lets only. playNext runs the step fn; paint/reflect reads session.world into the mockup. Closures may close over the same world object the session exposes ? one bag, two readers.

Highlight: UX model annotates controls (or regions) with story step labels they participate in. After playNext, shell looks up current step.label ? control ids and highlights those. No NLP on step prose; no ?control runs the step.? Interactive mode can ignore highlight or show last Play step?s controls.

### Story demo ? expose() for paint (not world bag)

Supersedes world bag as the preferred paint handle.

Steps keep domain variables (e.g. character / bundle) — tests stay unpolluted by an explicit world object. scenario API provides expose(() => ({ character, bundle })) (or equivalent). Dual-runner session stores that getter; after playNext, paint calls expose() and reflects the snapshot into the mockup.

Same object identity as the domain variables (not a copy unless paint chooses to clone). Interactive mode can use the same expose snapshot plus helpers to mutate domain, then paint again.

### Story demo ? highlight via UX annotation (B)

Highlight mapping: B ? UX annotation on controls (control ? steps), not story-side highlight lists and not a Play-shell label map as the source of truth.

Controls (or regions) declare which story steps they participate in, keyed by step label (the given/when/then sentence). After playNext, the shell reads current step.kind + step.label, finds controls annotated for that step, and highlights them.

Stories stay pure GWT (no control ids in when/then). Trade-off accepted: renaming a step label requires updating UX annotations. Stable step ids (D) deferred unless label churn becomes painful.

### Story demo ? ThenFeedback peer to PaintReflect

PaintReflect applies expose() domain snapshot only ? does not take Then statements or asserts.

After playNext on a Then step, ThenFeedback.apply(result) from soft-fail assert outcome (ok, expected/actual/message). Fail: message + explorer step red; tint failed values when path known. Pass: clear/mark step passed.

Interactive: on{WhenStatement} + PaintReflect only ? no ThenFeedback.

### Story demo ? Play does not invoke product controls

Clarified from grill: Play next is explorer chrome only. Product mockup controls are not invoked during Play ? step.fn() runs the GWT body; bind uses bound_field from expose(); emphasize uses story_steps match. Interactive is where Control.Interaction (any trigger) runs the When path. story_steps is a binding (not a mere annotation). Control model sketch gains story_steps alongside bound_field.

### Story demo UX submodule naming

Locked: UX Story Demo owns shell + PlayDualRunner (`story-demo/play-dual-runner/`). StoryDemoPage, StoryDemoFrame, ExplorerFrame, StoryDemoControl : Control. Vanilla Page/Control keep no bound_field / story_steps. pass #story-demo-ux-submodule-naming

### Story demo module homes

PlayDualRunner + story-test-* live under `context_tools/ux/story-demo/play-dual-runner/`. StoryDemo* shell beside it in `context_tools/ux/story-demo/`. Sandbox keeps only engagement wire.

### ux_model + story-demo integration

One model: `ux_model.Control` base; `StoryDemoControl` subtype adds `story_steps` (keeps `bound_field`). JSON round-trips `kind` + `story_steps`. HTML emit writes `data-bound-field` / `data-story-steps`. JS runtime hydrates via `StoryDemoControl.fromElement` — not a second object model.

### AI-generated screens use Story Demo shell

`templates/html/mockup_shell.html` is the default mockup page (left product / right explorer). `mount-generated-mockup.js` attaches PlayDualRunner. AI creates screens via the model + render — not bespoke character stubs in the template. pass #impl-ux-generated-playable

### Browser-safe create{Story}Story

Story files import `story-test-core` + `soft-assert` (no `node:test` / `node:assert`). Node tests import `story-test-node` first to register the describe/it backend. Play/HTML can `collect(createCharacterStory)` in the browser. pass #impl-browser-story-exports

