# Concepts

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

| Fidelity | Artifact |
|---|---|
| **ia** | One drawio under `.context/` — built via the **drawio-ux CLI**. |
| **mockup → specification** | One HTML per concrete user goal at the epic or sub-epic folder (tight-knit screen set — not one file per screen, not one mega-file for a whole epic unless that *is* the goal). |

Sketch/context MD stay in `.context/` (same pattern as other generators). Story / object-model JS stay where Stories / CE emit them; HTML imports those modules.

**Stories + object model:** `UxMap.story_references` / `object_references` store **paths** to Stories / Clean Engineering JS artifacts. If missing, run that generator’s `transform` to `javascript`. Mockup/spec HTML imports those paths. For now, render story names at the bottom of the page. Example-data injection and story tracing come later.

**Markdown:** optional context only (thinking, invariants, interaction notes). Primary path is **drawio (IA) → html (mockup/spec)**.


**Layouts:**  catalog in `ux_model/layouts.py` (layout id → named slots). Use `Screen.apply_layout` to set layout and seed empty regions. 

**Channels:** drawio, html, markdown, json — peer parse/render; `transform` moves sideways at the same fidelity. One `html` channel deepens by fidelity (js interactions → +css/brand).

---

This skill operates at **multiple levels of fidelity**. Start from grill + sketch and deepen. Each level **adds** artifacts — do not invent detail from a deeper fidelity.

| Fidelity | Default format | Output |
|---|---|---|
| **ia** | drawio | Site map + per-screen regions/nav (html optional via transform) |
| **mockup** | html | Wired greybox screens (html+js); drawio remains a peer channel |
| **specification** | html | Same html channel deepened — css/brand, richer stubs |

**Templates (AI generate):** drawio + html under `templates/`. Markdown context template optional. Other formats via channels / `transform`.

**Cross-format scanners:** channels parse into the canonical model; scanners read model fields only — never file syntax.

---

## Shared rules

- **`tab-states-are-separate-screens`** — N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.
- **`screen-story-budget`** — ~4 user stories per screen; more signals missed decomposition.
- **`screen-names-use-domain-terms`** — Screen labels trace to domain language when it exists.
- **`ia-named-regions-only`** — At IA, regions are named slots; no control detail yet.
- **`story-domain-js-imported`** — At mockup+, when stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

---

## ia

**Default format:** drawio

**Goal:** What screens exist and how users move between them — missing coverage shows as absent nodes.

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

**Goal:** Lock controls and key interactions as runnable html+js (greybox). Drawio peer channel still available.

1. Ensure story/domain JS via Stories / CE `transform` when missing (`ensure_javascript`).
2. Deepen regions with typed controls, states, and interactions.
3. Wire JS sufficient for key interactions (nav, tabs, open/close, state toggles).
4. Review shell: interactive mockup on the **left**; story names from imported story modules at the **bottom** for now.
5. Optional context md for notes not visible on screen.

### Rules

- **`controls-match-interaction-decisions`** — Exact control types; no invented affordances.
- **`story-domain-js-imported`** — Import real modules; do not invent a UX-only adapter shape.
- **`key-interactions-wired`** — JS covers the interactions decided at this fidelity.

---

## specification

**Default format:** html

**Goal:** Deepen the same html channel — brand/css, richer stubs, honest stub catalogue. Still not production.

- Carry over regions, controls, labels from mockup.
- Add css / design tokens / brand; document stubs.
- Domain enter/display through imported domain JS; stories still listed (tracing/example injection later).

### Rules

- **`stub-catalogue-honest`** — Every faked behaviour is listed; no silent pretence of production services.
- **`upstream-decisions-carried`** — Do not redecide layout or vocabulary at this fidelity.

---

# Generate

1. Confirm fidelity (`ia` → `specification`) and format (defaults above).
2. Read § Concepts — shared rules and the active fidelity (including its Rules).
3. Grill and sketch when useful (`@grill_with_context`, `sketch-template.md`):
   - **Site map on top** (connection tree).
   - **Screen boxes** show controls/states as glyphs — not `type=` / `state=` labels.
   - **Key under each screen** for glyph meanings and interactions.
   - **No margin fidelity tags** (`<-i` / `<-m` / `<-s`) — declare fidelity once at the top.
4. Ensure story/domain JS when mockup+ needs them (`ensure_javascript` / Stories·CE `transform`).
5. Fill templates for the active fidelity:
   - **ia** — `.context/information-architecture.drawio` (drawio-ux CLI).
   - **sketch / context** — `.context/ux-sketch.md`, optional `.context/ux-context.md`.
   - **mockup+** — `<user-goal>.html` colocated at epic/sub-epic; keep `ux-map.json` beside it when useful.
6. Run **validate**.
