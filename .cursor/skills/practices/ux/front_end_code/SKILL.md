**Default format:** drawio

**Goal:** What screens exist and how users move between them — missing coverage shows as absent nodes.

### Guidance

Screens, layouts, named regions, transitions, nav components, content types. Story names and domain terms attach as traces. Optional `ux-context.md` for invariants not on the canvas. No control types, no interaction JS, no brand.

### Scaffold

**When scaffolding only** (`/partition` or a names-only first cut — not full generate at this fidelity): follow this subsection. Do not use ### Rules below, ## Sketching, or ## Templates. **Stop reading this skill when scaffolding.**

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

**Default format:** html

**Goal:** Lock controls and key interactions as runnable html+js (greybox) inside the **Story Demo shell**. Drawio peer channel still available.

### Guidance

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

### Rules

- **`controls-match-interaction-decisions`** — Exact control types; no invented affordances.
- **`story-domain-js-imported`** — Import real modules; do not invent a UX-only adapter shape.
- **`key-interactions-wired`** — Nav/tabs via `data-goto` / interactions; story tracing via Story Demo mount (not bespoke product stubs).
- **`story-demo-control-for-gwt`** — GWT-bound controls are `StoryDemoControl` in the model so HTML gets `data-story-steps`.
- **`shell-from-template`** — Use `mockup_shell.html` / render channel; do not drop the explorer when generating screens.
- **`brand-is-opt-in`** — Do not add css / design tokens / brand unless asked or pre-existing. Greybox is the default output.
- **`stub-catalogue-honest`** — Every faked behaviour is listed in the html or a companion context note.

---

### Guidance

- Replace mockup stubs with the real client (routing, state, API calls, auth as needed).
- Call CE **code**-fidelity backend / Production collaborators — not Fake factory or in-browser demo domain alone.
- Story Demo may still exist as a review/exploration shell; it is not the product UI at this fidelity.
- Carry IA vocabulary and control decisions forward; do not redecide screens under a new product name.

### Rules

- **real-frontend-not-mockup** — Shipping UI is production frontend code, not the greybox Story Demo frame.
- **real-backend-wired** — Client talks to real services/persistence (CE **code**); no silent Fake path as the only path.
- **upstream-decisions-carried** — Layout and domain terms from earlier fidelities stay authoritative.
