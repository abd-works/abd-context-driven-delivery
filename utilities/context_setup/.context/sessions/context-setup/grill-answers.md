# Grill answers — context-setup (Increment 2: Capture From Live App)

**Session date:** 2026-08-13

---

## Q1: How should Stub External Dependencies decompose on the map?

**Answer:** Three stories.

- `AI Chat --> Classify External Dependencies` — reads the codebase and every external-facing
  call site, marks each dependency external (needs a stub) or in-scope (skip), and produces a
  classification table. The complex-stub-strategy trigger (5+ externals or domain-shaped returns)
  is a scenario variation within this story — it gates whether a story-map + AC + glossary
  pre-pass is required before writing any stubs.
- `Tool --> Write External Stubs` — writes stub code at the outermost boundary (HTTP adapter,
  SDK factory, module export) for every dependency classified as external.
- `Tool --> Smoke Test App` — starts the app, runs the automation-tool smoke test appropriate for
  the surface type (Playwright, pywinauto, requests), confirms every significant screen is
  reachable, and completes the stub inventory (`docs/stubs/stub-inventory.md`).

Source: `abd-context-app-sandbox/SKILL.md` — steps 1–7 of the Generate phase.

---

## Q2: Where does surface detection live on the map?

**Answer:** Inside `User --> Capture From Live App`.

The user names the repo path and either states the surface type (web / desktop / API) or the AI
Chat infers it from the repo at that point. No separate story is needed. Surface type is metadata
that flows into `Tool --> Scout App Pages` as a parameter.

Source: `abd-context-app-extractor/SKILL.md` step 1 — "Identify the surface. Inspect the target
repo for indicators."

---

## Q3: Phase 0 scout vs Phase N iteration — same story or two?

**Answer:** Two stories.

- `Tool --> Scout App Pages` — Phase 0: thin, fast pass over 10–20 representative pages or
  endpoints. Produces `extraction-overview.md` with one section per captured page.
- `Tool --> Complete App Capture` — Phase N: fills remaining views that the AI flagged as missing
  or incomplete during the review. Re-runs only the new captures.

Source: `abd-context-app-extractor/SKILL.md` steps 4–6.

---

## Q4: Should stubbing and capture phases become nested sub-epics?

**Answer:** Yes, nested sub-epics.

Structure:
```
(E) Capture From Live App
    (S) User --> Capture From Live App            // entry + surface detection
    (E) Stub External Dependencies
        (S) AI Chat --> Classify External Dependencies
        (S) Tool --> Write External Stubs
        (S) Tool --> Smoke Test App
    (E) Capture App Pages
        (S) Tool --> Scout App Pages
        (S) AI Chat --> Review Capture Coverage
        (S) Tool --> Complete App Capture
```

This respects `four-to-nine-children` at each level and makes the stub → capture handoff
explicit: `Capture App Pages` begins only after the stubbed app is proven reachable.
