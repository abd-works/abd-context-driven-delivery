---
description: "Whenever you place controls and wire story steps on a greybox, or change shipping UI that those mockups support. Follow these rules."
paths:
  - "**/*.html"
  - "**/*mockup*"
  - "**/*-sketch.md"
---

#### Rules



Whenever you place controls and wire story steps on a greybox, or change shipping UI that those mockups support. Follow these rules.

If this change will not stay here, follow `practices/ux/ia.mdc`.

- **`controls-match-interaction-decisions`** — Exact control types; no invented affordances.
- **`story-domain-js-imported`** — Import real modules; do not invent a UX-only adapter shape.
- **`key-interactions-wired`** — Nav/tabs via `data-goto` / interactions; story tracing via Story Demo mount (not bespoke product stubs).
- **`story-demo-control-for-gwt`** — GWT-bound controls are `StoryDemoControl` in the model so HTML gets `data-story-steps`.
- **`shell-from-template`** — Use `mockup_shell.html` / render channel; do not drop the explorer when generating screens.
- **`in-scope-epics-only`** — Screens and `data-goto` targets follow the in-scope epics. A deferred epic in `ux-context.md` does not get screens or buttons.
- **`brand-is-opt-in`** — Do not add css / design tokens / brand unless asked or pre-existing. Greybox is the default output.
- **`stub-catalogue-honest`** — Every faked behaviour is listed in the html or a companion context note.

---