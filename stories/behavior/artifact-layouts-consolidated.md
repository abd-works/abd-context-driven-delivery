# Artifact Layout — Consolidated

Multiple partial documents, typically sliced by increment or epic. Each iteration produces its own scenario doc, and these partials are merged back into a main file when the increment ships. Natural for docs (markdown, drawio, miro) where work is organised by iteration.

## Output locations

One file per artifact type at the project root: `stories-map.md` (or `.drawio`), `stories-thin-slice.md`, `stories-scenarios.md`.

**Story scenarios is the only artifact that gets parcelled and merged.** Story map and thin slice stay as single files — they are not sliced by iteration or epic.

## Working with scenario partials

- New scenarios for an iteration or epic go into a partial file — e.g. `iteration-1-stories-scenarios.md`, `epic-manage-orders-stories-scenarios.md` — do not touch `stories-scenarios.md` mid-increment
- When the increment is complete, merge the partial into `stories-scenarios.md` and delete the partial

## Filtered views

A **filtered view** is a named slice for a specific activity, iteration, or level (e.g. `iteration-1-stories-scenarios.md`, `manage-orders-stories-specification.md`). Filtered views come in two flavours:

- **Increment partials** — canonical while they hold scenarios that have not yet been merged back into `stories-scenarios.md` (see *Working with scenario partials* above)
- **On-demand slices** — regenerated from the main file at any time for reading or hand-off; not canonical, and regenerating from the main file always wins

## Not valid for tests

Test packaging must follow the story map folder hierarchy, not iteration slices — tests use Expanded or Flat layout, never Consolidated.
