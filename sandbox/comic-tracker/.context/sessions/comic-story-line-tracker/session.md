# Session: comic-story-line-tracker

## Start

- **date:** 2026-08-08
- **path:** sandbox/comic-tracker
- **goal:** Interactive Comic Story Line Tracker — segmented, constellation-style
  timeline that makes it easy to start reading a comic from a crossover event and
  flip across series when timelines intersect
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
