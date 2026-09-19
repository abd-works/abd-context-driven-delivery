## Overview

UX looks at the product through user navigation and information architecture, from layout and transitions to more formal screens, regions, and controls — how users see and act on the solution — mapped at increasing fidelity.

**Canonical model** (reuse, do not reinvent): `UxMap` → `Screen` → `Region` → `Control` → `Interaction`, plus `Transition`, `ContentType`, `NavComponent` on the map. Optional `UxContext` holds notes/invariants not visible on screens.

**Layout (mirror Stories; colocated):**

```
sandbox/<epic>/
  ux-map.json                              <- canonical model (optional peer)
  <user-goal>.html                        <- mockup+ (one file per concrete user goal)
  <sub-epic>/…_stories.py|.js
  .context/
    information-architecture.drawio        <- ia (drawio-ux CLI: Detailed IA + Site Map)
    ux-sketch.md                           <- scratch sketch
    ux-context.md                          <- optional notes/invariants
```

Sketch/context MD stay in `.context/` (same pattern as other generators). Story / object-model JS stay where Stories / CE emit them; HTML imports those modules.

**Stories + object model:** `UxMap.story_references` / `object_references` store **paths** to Stories / Clean Engineering JS artifacts. If missing, run that generator’s `transform` to `javascript`. Mockup/spec HTML imports those paths.

**Story Demo shell (mockup+):** Generated HTML uses `templates/html/mockup_shell.html` — product screens **LEFT**, story explorer **RIGHT**. `story-demo/mount-generated-mockup.js` loads `create{Story}Story` exports, runs `PlayDualRunner`, and paints the explorer. Serve from **repo root** so `/practices/...` imports resolve.

**Worked example:** `practices/ux/examples/manage-customer-orders/` (Place New Order mockup + stories + shopping_cart domain) — general UX output sample that happens to run in the Story Demo shell.

**One control model:** `ux_model.Control` is vanilla. Controls that bind to GWT steps are `StoryDemoControl` (`bound_field` + `story_steps`) — HTML emits `data-bound-field` / `data-story-steps`. Do **not** invent a second page/control model in freehand HTML.

**Interactive (domain-agnostic):** `StoryDemoControl` may also carry `set_input`, `item_story_steps`, `item_value`, `item_label`. Emit:
- `number` / `quantity` → `data-input-field`
- `bound-list` / `list-host` → `data-bound-list` + `data-bound-field` (expose path) + optional `data-item-story-steps` / `data-set-input`  
Do **not** bake product words (catalog, cart) into the template — those are bound_field paths / story language only.

**Markdown:** optional context only (thinking, invariants, interaction notes). Primary path is **drawio (IA) → html (mockup/spec)**.

**Specifications (layouts):** `specifications/` holds the full IA screen-template set as ready-to-adapt reference artifacts, one sibling folder per style:

- `specifications/generic/` — **default.** One `.md` ASCII reference + one `.drawio` XML fragment per layout (accordion, breadcrumb, kanban-board, sidebar, tabbed, wizard-stepper, … 43 patterns), mirrored verbatim from abd-skills. No brand.
- `specifications/abd-works/` — the same 43 layouts as real, brand-styled HTML (`<id>.html` + `index.html`), all sharing `abd-works-brand.css` (tokens/type/components copied from the `abd-visual-branding` SKILL.md: colors, Inter/JetBrains Mono type scale, buttons, cards, dual Executive/Engineering mode). Use this folder instead of `generic/` whenever the screen needs the abd.works brand (see `brand-is-opt-in` below).
- Add further sibling folders under `specifications/` for other brands/styles the same way; each folder's own files stay self-contained (own stylesheet, own copies).

Before sketching a screen's ASCII box, drawio region cells, or brand-layer html, open the matching file(s) in the specification folder that applies — `generic/` unless a specific brand is asked for or already established for this work — read its slots, and alter that file for the real screen. Do not draw box art, drawio cells, or brand markup from scratch when one of these already covers the shape. `Screen.apply_layout(layout_id)` just records that choice as the layout name; append the real `Region`s yourself from the slots you just read.

**Channels:** drawio, html, markdown, json — peer parse/render; `transform` moves sideways at the same fidelity. One `html` channel deepens by fidelity (js interactions → optional brand layer + honest stubs at **mockup** → real frontend at **front_end_code**; host FE stacks welcome at **front_end_code**).

---

This skill operates at **multiple levels of fidelity**. Start from grill + sketch and deepen. Each level **adds** artifacts — do not invent detail from a deeper fidelity.

| Fidelity | Default format | Output |
|---|---|---|
| **ia** | drawio | Site map + per-screen regions/nav (html optional via transform) |
| **mockup** | html | Wired greybox screens (html+js); one HTML per concrete user goal (not one file per screen, not one mega-file per epic); drawio remains a peer channel; optional brand layer; honest stub catalogue |
| **front_end_code** | html (or host FE stack) | Real frontend — production UI wired to real backend; not Story Demo / greybox alone |

**Templates (AI generate):** drawio + html under `templates/`. Markdown context template optional. Other formats via channels / `transform`.

**Cross-format scanners:** channels parse into the canonical model; scanners read model fields only — never file syntax.

---

ia — Decide what screens exist and how users move between them.

Use MCP tool: `ux-ia()`

mockup — Lock screens as runnable greybox — typed controls and key interactions.

Use MCP tool: `ux-mockup()`

front_end_code — Ship the product UI — production frontend talking to a real backend.

Use MCP tool: `ux-front-end-code()`
