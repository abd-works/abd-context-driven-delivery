---
fidelity: [discovery]
artifact: [thin-slice]
---

# Generate — Thin Slice

## Pipeline

- **Before:** Story Map (shaping/discovery) — story map must exist to slice.
- **After:** Story Scenarios (exploration) — add story detail once priorities are set.

## Workflow order

1. Read inputs — story map / graph, PO or tech notes, risks and dependencies.
2. Mark spine vs optional — see `rules/map-sequential-spine-vs-optional-paths.md`.
3. Cut **vertical** slices — end-to-end demonstrable path per increment; avoid horizontal "finish epic A, then B."
4. Name increments for stakeholder-visible **capability**, not phase or stack labels.
5. Pull stories under each increment in **flow order** — verb-noun, copied **verbatim** from `story-map.md` / `story-graph.json` (character-for-character, including parentheticals). No actor prefix in story names.
6. Fill `templates/md/thin-slice.md`.

## Input traps

Assumptions, ambiguities, and missing context that commonly produce bad thin-slicing plans. Check each trap against available input before generating — flag gaps honestly; do not batch stories to hide uncertainty.

- **Spine vs optional** — which stories must be delivered together to show an end-to-end path, and which can follow later without blocking value?
- **Vertical not horizontal** — are you slicing by user-visible capability, or by technical layer — and would a stakeholder recognise your increment names?
- **Value assumption** — what makes you believe this increment is the smallest useful thing, rather than a comfortable batch?
- **Dependency trap** — which cross-epic dependencies are you hiding inside an increment instead of making them visible?
- **Ordering rationale** — why does increment N come before increment N+1 — is it risk, learning, or just the order you thought of them?
