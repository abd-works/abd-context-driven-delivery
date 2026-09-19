## Overview

UX maps how users see and act on the product: screens, regions, controls, and the transitions between them. Deepen from information architecture to a runnable greybox, then to the shipping frontend. Each fidelity adds artifacts; it does not invent detail from a later one.

## Guidance

**Canonical model.** Reuse `UxMap` → `Screen` → `Region` → `Control` → `Interaction`, plus `Transition`, `ContentType`, and `NavComponent` on the map. Optional `UxContext` holds notes and invariants that are not visible on screens. Do not invent a second page or control model in freehand HTML.

**Primary path.** Start from grill and sketch. Draw information architecture in drawio, deepen to html mockups, then ship real frontend at **front_end_code**. Markdown is optional context (thinking, invariants, interaction notes), not the main artifact. Channels are drawio, html, markdown, and json — peers at the same fidelity; `transform` moves sideways. The html channel deepens in place: interactions and optional brand at **mockup**, production UI at **front_end_code**. Templates for generate live under `templates/`. Scanners read the canonical model, never file syntax.

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

Sketch and context markdown stay in `.context/`. Story and object-model JS stay where Stories and Clean Engineering emit them; HTML imports those modules. `UxMap.story_references` and `object_references` store **paths** to those artifacts. If they are missing, run that generator's `transform` to `javascript`.

**Story Demo (mockup+).** Generated HTML uses `templates/html/mockup_shell.html` — product screens **LEFT**, story explorer **RIGHT**. `story-demo/mount-generated-mockup.js` loads `create{Story}Story` exports, runs `PlayDualRunner`, and paints the explorer. Serve from the **repo root** so `/practices/...` imports resolve. Worked example: `practices/ux/examples/manage-customer-orders/`.

**Controls.** `ux_model.Control` is vanilla. Controls that bind to GWT steps are `StoryDemoControl` (`bound_field` + `story_steps`); HTML emits `data-bound-field` / `data-story-steps`. Interactive extras (`set_input`, `item_story_steps`, `item_value`, `item_label`) emit `data-input-field` on number/quantity and `data-bound-list` on list hosts. Do not bake product words (catalog, cart) into the template — those are bound_field paths and story language only.

**Specifications (layouts).** `specifications/` holds ready-to-adapt screen templates, one sibling folder per style:

- `specifications/generic/` — **default.** One `.md` ASCII reference + one `.drawio` XML fragment per layout (43 patterns). No brand.
- `specifications/abd-works/` — the same layouts as brand-styled HTML sharing `abd-works-brand.css`. Use this folder when the screen needs the abd.works brand (`brand-is-opt-in`).
- Add further sibling folders for other brands the same way; each folder stays self-contained.

Before sketching ASCII, drawio regions, or brand-layer html, open the matching file in the folder that applies (`generic/` unless a brand is asked for or already established), read its slots, and adapt that file. Do not draw from scratch when a specification already covers the shape. `Screen.apply_layout(layout_id)` records the layout name; append real `Region`s from the slots you just read.

**Fidelities.**

| Fidelity | Default format | Output |
|---|---|---|
| **ia** | drawio | Site map + per-screen regions/nav (html optional via transform) |
| **mockup** | html | Wired greybox; one HTML per concrete user goal; drawio remains a peer channel |
| **front_end_code** | html (or host FE stack) | Production UI wired to a real backend |

## Shared rules

Whenever you name screens, attach stories, or import domain terms on the UX surface, or change later UI work that forces that vocabulary to move. Follow these rules.

- **`tab-states-are-separate-screens`** — N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.
- **`screen-story-budget`** — ~4 user stories per screen; more signals missed decomposition.
- **`screen-names-use-domain-terms`** — Screen labels trace to domain language when it exists.
- **`ia-named-regions-only`** — At IA, regions are named slots; no control detail yet.
- **`story-domain-js-imported`** — At mockup+, when practices/stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

---

## Fidelities

### ia


**Default format:** drawio
**Stage:** discovery

#### Overview

Decide what screens exist and how users move between them.

#### Guidance

Screens, layouts, named regions, transitions, nav components, content types. Story names and domain terms attach as traces. Optional `ux-context.md` for invariants not on the canvas. No control types, no interaction JS, no brand.

#### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates. **Stop reading this skill when scaffolding.**

Rough screen index for a **partition** pass or first cut — screen names in domain/user language plus interactions and transitions (**list only**). No drawio regions, no mockup controls, no brand.

Key rules: `tab-states-are-separate-screens` — each distinct tab or alternate state is its own screen entry; `screen-names-use-domain-terms` — name screens in user/domain language, never technical or chapter labels; `screen-story-budget` — one screen per coherent user goal.

- Screens, layouts, named regions, transitions, nav components, content types.
- Story names and domain terms attached as traces (from story/domain JS or sources).
- Optional `ux-context.md` for invariants / notes not on the canvas.
- No control types, no interaction JS, no brand.

#### Rules

Whenever you decide which screens exist and how users move between them, or change mockups or shipping UI that forces that structure to move. Follow these rules.

If this change will not stay here, follow `practices/ux.mdc`.

- **`tab-states-are-separate-screens`** / **`screen-story-budget`** / **`ia-named-regions-only`** — as above.
- **`system-stories-group-with-visible-trigger`** — System stories group with the closest user-visible screen.

---

### mockup


**Default format:** html
**Stage:** specification

#### Overview

Lock screens as runnable greybox — typed controls and key interactions.

#### Guidance

1. Ensure story/domain JS via Stories / CE `transform` when missing (`ensure_javascript`).
2. Deepen regions with typed controls, states, and interactions.
3. For each control that participates in a story Given/When/Then (emphasize in Play, or run When in Interactive), use **`StoryDemoControl`** with:
   - `bound_field` — expose() path to display (or list array path on `bound-list`)
   - `story_steps` — `[{ kind, label }, …]` matching story step text exactly
   - Interactive lists: `control_type: bound-list`, shared `item_story_steps` When (not per-row labels), `set_input` for the pick key; stories use `input(...)` / `session(...)`
4. Prefer **model → `HtmlUxMap.render`** (fills `mockup_shell.html`). AI should not rebuild a one-off shell; fill screens/controls on the model.
5. Shell layout is fixed: product mockup **LEFT** (`#story-demo-frame`); explorer **RIGHT** (`#explorer-frame` — Play next / Reset / step tree). `data-goto` still navigates between product screens.
6. Story modules must export `create{Story}Story(mode)` loadable in the browser for Play (no `node:test` import on that path — use story-test-core / a demo export if needed).
7. Optional context md for notes not visible on screen.
8. **Optional — branding (off by default).** Apply a css / design-tokens / brand layer only when **one of these is true**:
   - The user explicitly asks for brand at this step, or
   - Brand/css tokens already exist somewhere in the workspace (check before deciding).
   Do not invent brand. When active, pick the sibling folder under `specifications/` for the brand that applies (e.g. `specifications/abd-works/`) and start from its matching page rather than inventing tokens; if no named brand applies, `specifications/generic/` (no brand layer) is the default. Fall back to whatever brand/css tokens already exist in the workspace when neither covers it. Add a thin css layer to the greybox html; keep the Story Demo shell fully functional. Brand applied here carries forward to **front_end_code** automatically — do not re-apply.
9. Document every faked behaviour explicitly — list all stubs; no silent pretence of production services.

#### Rules

Whenever you place controls and wire story steps on a greybox, or change shipping UI that those mockups support. Follow these rules.

If this change will not stay here, follow `practices/ux/ia.mdc`.

- **`controls-match-interaction-decisions`** — Exact control types; no invented affordances.
- **`story-domain-js-imported`** — Import real modules; do not invent a UX-only adapter shape.
- **`key-interactions-wired`** — Nav/tabs via `data-goto` / interactions; story tracing via Story Demo mount (not bespoke product stubs).
- **`story-demo-control-for-gwt`** — GWT-bound controls are `StoryDemoControl` in the model so HTML gets `data-story-steps`.
- **`shell-from-template`** — Use `mockup_shell.html` / render channel; do not drop the explorer when generating screens.
- **`brand-is-opt-in`** — Do not add css / design tokens / brand unless asked or pre-existing. Greybox is the default output.
- **`stub-catalogue-honest`** — Every faked behaviour is listed in the html or a companion context note.

---

### front_end_code


**Default format:** html (or the host app’s frontend stack)
**Stage:** implementation

#### Overview

Ship the product UI — production frontend talking to a real backend.

#### Guidance

- Replace mockup stubs with the real client (routing, state, API calls, auth as needed).
- Call CE **code**-fidelity backend / Production collaborators — not Fake factory or in-browser demo domain alone.
- Story Demo may still exist as a review/exploration shell; it is not the product UI at this fidelity.
- Carry IA vocabulary and control decisions forward; do not redecide screens under a new product name.

#### Rules

Whenever you create, alter, or delete shipping UI or how it talks to the backend. Follow these rules.

If this change will not stay here, follow `practices/ux/mockup.mdc`.

- **`real-frontend-not-mockup`** — Shipping UI is production frontend code, not the greybox Story Demo frame.
- **`real-backend-wired`** — Client talks to real services/persistence (CE **code**); no silent Fake path as the only path.
- **`upstream-decisions-carried`** — Layout and domain terms from earlier fidelities stay authoritative.
