# `docs/ux/initial-ia.md` stays in sync with the canvas

The markdown spec and the canvas are two views of the same initial information architecture. They must agree at every commit. The canvas has two pages: **Detailed IA** (full screen layouts) and **Site Map** (one box per screen, labeled arrows). Both pages must match the markdown.

**DO** author or update `docs/ux/initial-ia.md` **before** driving the canvas — the markdown is the structured input the canvas is drawn from. Author the **Screen flow — complete connection map** section before running `save`; the Site Map page is generated from the same state that drives the Detailed IA page.

**DO** read the updated canvas after the agent finishes and reflect any structural change (renamed region, added or removed screen, added or removed transition, regrouped system story, added or renamed navigational component, added or renamed content type, changed key actions) back into `docs/ux/initial-ia.md` in the same skill run.

**DO** append a row to the change log in `docs/ux/initial-ia.md` every time the canvas changes, recording date, direction (`md → canvas` or `canvas → md`), and a one-line summary.

**DO NOT** commit a `.tldr` or `.svg` whose screens, regions, transitions, navigational components, or content types disagree with `docs/ux/initial-ia.md`. If they disagree, decide which one is right, fix the other, and only then commit.

**DO NOT** treat the markdown as a write-once template. Every skill run touches it: created on first run, updated on every subsequent run.
