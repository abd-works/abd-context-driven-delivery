# Session: comic-story-line-tracker

## Start

- **date:** 2026-08-08
- **path:** sandbox/comic-tracker
- **goal:** Interactive Comic Story Line Tracker — subway-map timeline where each
  series is one unbroken line with issues as stops, and cross-series continuations
  are transfer lines bundled into per-event toggles. Makes it easy to start reading
  from any stop and transfer across lines at the crossovers.
  (Metaphor swap 2026-08-08: was segmented / constellation-style; see
  `grill-answers.md` § "Visual metaphor swap".)
- **I1 tech stack (2026-08-13):** Node.js + Express (server) + Angular
  (web); TypeScript across; npm-workspaces monorepo under
  `sandbox/comic-tracker/` with `server/` + `web/` workspaces and a
  shared `catalog/fixtures/` directory. Existing `sandbox/tests/` and
  `sandbox/src/*` coexist unchanged.
- **increment plan (2026-08-10 redirect):**
  · I1 (current front of work) — Load a small sample of catalog data from
    public sources (Metron baseline + Marvel API mirror for `digitalId`);
    provide a Query capability + Results view + Browse Imported view.
    Fixture JSON is the runtime source (per Q2). No subway-map UI yet.
  · I2 — AI scanner as a new CDD context tool that extends the ABD-CDD
    framework. Peers with `cdd`, `stories`, `ux`, `bdd`,
    `clean_engineering`, `ddd` under `context_tools/`. Actions:
    `research`, `review`, `extract`. Closes the editorial-layer gap that
    public APIs don't cover (readingOrder, TeamMembership spans,
    continuesIn, protagonist typing).
  · I3+ — Subway-map tracker (all existing spec-level themes deferred).
  · "Others" (comicverse-api adoption, GCD direct, tracker UX polish,
    Character-first-class promotion) — deferred beyond I2.
- **fidelities:** spec (CDD) — child stage keys: ux=mockup, ce=code, bdd=behavior
- **contexts (in play):** ux, clean_engineering, bdd
  (stories / ddd omitted this cycle — user scoped grill+sketch to CE + BDD + UX)
- **source of ask:** prior chat turn — verbatim summary in
  `.context/sessions/comic-story-line-tracker/cdd-sketch.md` under
  `Sources / context`

## Layout

- durable tool root: `sandbox/comic-tracker/` (docs → `.context/`, code → `src/`)
- sprint folder: `sandbox/comic-tracker/.context/sessions/comic-story-line-tracker/`
- files this cycle: `session.md`, `cdd-sketch.md`, `grill-answers.md`

## Rules honoured

- `cdd-owns-grill-sketch` — one CDD sketch drives all lenses; no nested child sketches.
- `views-agree-before-proceed` — flow recommends `more-same-stage` while ux + ce + bdd
  still have open blockers (see `flow.open`).
- `todo-trail-in-sketch` — TODO / doing / pass #label lives in `cdd-sketch.md`.
- `lens-from-child-template` — each lens block copies its own
  `templates/{lens}-sketch.md` notation, not free prose.
- `prove-read-before-asking` — grill entries cite the concrete files read.
