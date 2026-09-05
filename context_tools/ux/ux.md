# Contexts

UX looks at the product through user navigatin and information architecture, from layout and transitions to more formal screens, regions, and controls — how users see and act on the solution — mapped at increasing fidelity.

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

**Story Demo shell (mockup+):** Generated HTML uses `templates/html/mockup_shell.html` — product screens **LEFT**, story explorer **RIGHT**. `story-demo/mount-generated-mockup.js` loads `create{Story}Story` exports, runs `PlayDualRunner`, and paints the explorer. Serve from **repo root** so `/context_tools/...` imports resolve.

**Worked example:** `context_tools/ux/examples/manage-customer-orders/` (Place New Order mockup + stories + shopping_cart domain) — general UX output sample that happens to run in the Story Demo shell.

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

## Shared rules

- **`tab-states-are-separate-screens`** — N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.
- **`screen-story-budget`** — ~4 user stories per screen; more signals missed decomposition.
- **`screen-names-use-domain-terms`** — Screen labels trace to domain language when it exists.
- **`ia-named-regions-only`** — At IA, regions are named slots; no control detail yet.
- **`story-domain-js-imported`** — At mockup+, when context_tools/stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

---


## ia

**Default format:** drawio

**Goal:** What screens exist and how users move between them — missing coverage shows as absent nodes.

### Scaffold

Rough screen index for a **partition** pass or first cut — screen names in domain/user language plus interactions and transitions (**list only**). No drawio regions, no mockup controls, no brand.

Key rules: `tab-states-are-separate-screens` — each distinct tab or alternate state is its own screen entry; `screen-names-use-domain-terms` — name screens in user/domain language, never technical or chapter labels; `screen-story-budget` — one screen per coherent user goal.

- Screens, layouts, named regions, transitions, nav components, content types.
- Story names and domain terms attached as traces (from story/domain JS or sources).
- Optional `ux-context.md` for invariants / notes not on the canvas.
- No control types, no interaction JS, no brand.

### Rules

- **`tab-states-are-separate-screens`** / **`screen-story-budget`** / **`ia-named-regions-only`** — as above.
- **`system-stories-group-with-visible-trigger`** — System stories group with the closest user-visible screen.

---

## mockup

**Default format:** html

**Goal:** Lock controls and key interactions as runnable html+js (greybox) inside the **Story Demo shell**. Drawio peer channel still available.

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

### Rules

- **`controls-match-interaction-decisions`** — Exact control types; no invented affordances.
- **`story-domain-js-imported`** — Import real modules; do not invent a UX-only adapter shape.
- **`key-interactions-wired`** — Nav/tabs via `data-goto` / interactions; story tracing via Story Demo mount (not bespoke product stubs).
- **`story-demo-control-for-gwt`** — GWT-bound controls are `StoryDemoControl` in the model so HTML gets `data-story-steps`.
- **`shell-from-template`** — Use `mockup_shell.html` / render channel; do not drop the explorer when generating screens.
- **`brand-is-opt-in`** — Do not add css / design tokens / brand unless asked or pre-existing. Greybox is the default output.
9. Document every faked behaviour explicitly — list all stubs; no silent pretence of production services.
- **`stub-catalogue-honest`** — Every faked behaviour is listed in the html or a companion context note.

---

## front_end_code

**Default format:** html (or the host app’s frontend stack)

**Goal:** Real frontend for the product — production UI and client wiring to a real backend. Not greybox, not Story Demo as the shipping surface, not stub-only services.

- Replace mockup stubs with the real client (routing, state, API calls, auth as needed).
- Call CE **code**-fidelity backend / Production collaborators — not Fake factory or in-browser demo domain alone.
- Story Demo may still exist as a review/exploration shell; it is not the product UI at this fidelity.
- Carry IA vocabulary and control decisions forward; do not redecide screens under a new product name.

### Rules

- **`real-frontend-not-mockup`** — Shipping UI is production frontend code, not the greybox Story Demo frame.
- **`real-backend-wired`** — Client talks to real services/persistence (CE **code**); no silent Fake path as the only path.
- **`upstream-decisions-carried`** — Layout and domain terms from earlier fidelities stay authoritative.
