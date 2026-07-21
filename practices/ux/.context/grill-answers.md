# UX migration — grill decisions (2026-07-17)

## Fidelities
- `ia → mockup → specification` only.
- Drop impact-map and ui-implementation from this generator (sketch covers shaping; production UI stays elsewhere).

## When wiring starts
- **Agreed:** wire at **mockup**. Mockup produces a runnable native web artifact (semantic HTML + stub interactions, greybox / no brand).
- **Specification** deepens: brand tokens, richer stubs, AC demo paths.
- Host UI stacks (React/Vue/…) are optional peer channels via `transform` — not required to get the mid-fi loop.

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
- Peer channels: markdown, json, drawio, html+js, html+js+css (and later host stacks).
- Review shell: **mockup on the left side of the screen** (interactive surface).

## Regeneratable / write-once
- **No write-once tier** in UX. There is no engineering fidelity and no “don’t regen” trap.
- Regeneration / `transform` is for **converting** between peer formats from the canonical model.

## Object model (language sketch)
- Saved: `ux/.context/ux-model-sketch.md` (Clean Engineering sketch notation).
- Spine: `UxMap` → `Screen` → `Region` → `Control`.
- `Transition` / `ContentType` / `NavComponent` are **`UxComponent` subtypes**.
- Collections **`Transitions` / `ContentTypes` / `NavComponents`** (`UxComponentCollection`) own `append` / `remove` / `find` — not flat append ops on `UxMap`.
- **`story_references` / `object_references`** are properties on `UxMap` — each stores **paths** to JS artifacts (not module bodies). Bind/dedupe behind the property. Object = CE object-model JS; domain language not built yet.
- Conversion: `UxChannel.parse` / `render`; `Ux.transform` wires source→canonical→target.
- Interactions live on `Control` (trigger / effect / destination) — deepened at mockup with JS.

## Web channel
- **One `html` channel** — deepens by fidelity (mockup: html+js greybox interactions; specification: adds css/brand). Not two transform targets.
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
- Not: a separate `ux/` package folder; not one file per individual screen.

## Markdown role
- MD is a good scratch pad for **stories / specs / OO language** — it **sucks as primary UX surface**.
- UX flow: **drawio (IA) → html (mockup/spec)**. MD is **not mandatory** and not the authoring path for screens.
- Keep optional MD only for info **not easily accessible on screens** — same idea as story-context / module-context: thinking, interactions to capture, invariants, notes. Not a full IA/mockup document.

## Scaffold
- **Agreed to scaffold** (2026-07-17): `ux/` package like stories — `ux.py`, `ux.md`, sketch-template, `ux_model/`, channels (drawio/html/md/json), scanners, templates.
- Leave `abd-skills/practices/user-experience-design` in place (do not delete).
- Cursor skill: `.cursor/skills/ux/SKILL.md`.
- Drawio channel: vendored **drawio-ux CLI** (`ux/diagram/drawio/drawio_ux.mjs`) — same engine as abd-skills IA. `render` writes Detailed IA + Site Map (not stuffed blue boxes).
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

