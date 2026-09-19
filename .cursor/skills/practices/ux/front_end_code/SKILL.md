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

## front_end_code

# UX — Procedural Guidance (front_end_code fidelity)

## From mockup to production frontend

This fidelity is about real shipping UI, not enhanced greybox. The thinking shift:

1. **Replace stubs with real clients** — routing, state management, API calls, authentication. The mockup's faked behaviors become real service integrations.
2. **Wire to real backend** — CE code-fidelity backend with Production collaborators. Not Fake factory, not in-browser demo domain.
3. **Story Demo is now a companion, not the product** — the Story Demo shell may still exist for review/exploration, but it's not the shipping UI.
4. **Carry forward all IA decisions** — layout vocabulary, control decisions, screen decomposition from earlier fidelities are still authoritative. Don't re-decide screens under a new product name.

## What "real frontend" means

A vertical is NOT at code fidelity while it depends on:
- A mockup/Story Demo shell as the only UI
- In-memory or fake factories as the only "backend"

Code means real backend AND real frontend — not greybox + demo domain alone.

## Host framework awareness

At this fidelity, the host app's frontend stack takes over (React, Vue, Angular, vanilla). The IA and mockup decisions inform component structure and routing, but the implementation uses the real framework's patterns.


## ia

# UX — Procedural Guidance (ia fidelity)

## How to build the information architecture

IA answers: what screens exist, how users move between them, and what's on each screen (named regions only — no control detail yet).

1. **Start from user goals** — each distinct user goal gets a screen. "Sign up" is a screen. "Browse products" is a screen. "Manage subscription" is a screen.
2. **Map the transitions** — how does the user get from one screen to another? Click a button, select a tab, follow a wizard step? Each transition is an explicit arc.
3. **Name the regions** — each screen is divided into named slots: header, main content, sidebar, footer. At IA, these are just names — no control types yet.
4. **Group system stories with visible triggers** — a system story (background sync, notification push) groups with the closest user-visible screen that triggers or displays it.

## Screen decomposition thinking

When deciding whether something is one screen or many:

- **Different tab contents = different screens** — even if they share the same header/nav chrome. Use `chrome_of` to share the frame.
- **Different states of the same form = same screen** — editing vs viewing an order is one screen with states, not two screens.
- **Different user types seeing different things = different screens** — admin vs customer dashboard, even if the URL is the same.

## Layout pattern thinking

Before sketching a screen's regions from scratch, check `specifications/generic/` (or the brand-specific folder). There are 43 layout patterns with ready-to-adapt reference artifacts. Read the matching pattern's slots first, then alter for the real screen. Don't invent layouts when a pattern already covers the shape.

## No control detail at IA

At IA, regions are named slots only. Don't specify control types (dropdowns, radio buttons, text inputs). Don't add interaction JavaScript. Don't apply branding. Those come at mockup fidelity.


## mockup

# UX — Procedural Guidance (mockup fidelity)

## How to build mockups

Mockups deepen IA regions into typed controls with key interactions, running inside the Story Demo shell:

1. **Ensure story/domain JS exists** — if Stories or CE haven't emitted JavaScript modules yet, run `transform` first. The mockup imports real domain modules, not UX-only adapters.
2. **Deepen regions with controls** — each IA region slot gets concrete control types: text input, dropdown, button, list, tabs.
3. **Wire GWT-bound controls** — controls that participate in story Given/When/Then use `StoryDemoControl` with `bound_field` (the expose path) and `story_steps` (matching step text exactly). This generates `data-story-steps` attributes for the Story Demo explorer.
4. **One HTML per user goal** — not one file per screen, not one mega-file per epic. Each concrete user goal the user can demo gets its own HTML file.

## Interactive controls thinking

For controls that take user input or display dynamic data:

- **Number/quantity inputs** → `data-input-field`
- **Bound lists** → `data-bound-list` + `data-bound-field` (expose path) + optional `data-item-story-steps`
- **Don't bake product words into the template** — "catalog," "cart" are bound_field paths and story language, not template tokens.

## Branding is opt-in

Default output is greybox — functional, no branding. Add brand/CSS only when:
- The user explicitly asks for it, or
- Brand tokens already exist in the workspace

When branding is active, use the matching `specifications/` folder (e.g. `specifications/abd-works/`). Don't invent brand tokens.

## Stub catalogue honesty

Every faked behavior must be explicitly listed. No silent pretence of production services. If the mockup stubs a payment gateway, that's documented in the HTML or a companion note.

## Shell layout is fixed

Product mockup on the LEFT (`#story-demo-frame`). Explorer on the RIGHT (`#explorer-frame`). `data-goto` navigates between product screens. Don't rebuild the shell — use `mockup_shell.html` and fill screens/controls on the model.


## shared

# UX — Procedural Guidance (shared)

## Think in screens, not features

A screen is a coherent user goal — one thing the user is trying to accomplish. Not a feature list, not a component library, not a page in the app's routing table.

Key thinking:

1. **Each screen answers one question** — "What am I looking at?" "What can I do here?" If a screen tries to answer three different questions, it's probably three screens.
2. **~4 user stories per screen** — this is the budget. If a screen serves more stories than that, it needs decomposition. Fewer is fine.
3. **Tab states are separate screens** — if a tab shows fundamentally different content with different interactions, it's a separate screen that shares chrome with its siblings.

## Name screens in domain language

Screen labels come from the domain, not from technical or chapter labels. "Browse Catalog" not "ProductList." "Verify Identity" not "KYCForm." If domain language exists (from DDD or Stories), the screen name traces to it.

## Invariants and context notes

Things that aren't visible on screens but constrain the UX (business rules, interaction constraints, timing dependencies) go in `ux-context.md`. This is the same role as `story-context.md` or `module-context.md` — notes the visual artifact can't express.

## Shared rules

Use these rules when naming screens, attaching stories, or importing domain JS — not inventing a second vocabulary.

- **`tab-states-are-separate-screens`** — N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.
- **`screen-story-budget`** — ~4 user stories per screen; more signals missed decomposition.
- **`screen-names-use-domain-terms`** — Screen labels trace to domain language when it exists.
- **`ia-named-regions-only`** — At IA, regions are named slots; no control detail yet.
- **`story-domain-js-imported`** — At mockup+, when practices/stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

---

#### Overview


**Default format:** html (or the host app’s frontend stack)
**Stage:** implementation

**Goal:** Ship the product UI — production frontend talking to a real backend.

#### Guidance

- Replace mockup stubs with the real client (routing, state, API calls, auth as needed).
- Call CE **code**-fidelity backend / Production collaborators — not Fake factory or in-browser demo domain alone.
- Story Demo may still exist as a review/exploration shell; it is not the product UI at this fidelity.
- Carry IA vocabulary and control decisions forward; do not redecide screens under a new product name.

#### Rules

Use these rules when replacing greybox with shipping UI and real API calls.

- **`real-frontend-not-mockup`** — Shipping UI is production frontend code, not the greybox Story Demo frame.
- **`real-backend-wired`** — Client talks to real services/persistence (CE **code**); no silent Fake path as the only path.
- **`upstream-decisions-carried`** — Layout and domain terms from earlier fidelities stay authoritative.
