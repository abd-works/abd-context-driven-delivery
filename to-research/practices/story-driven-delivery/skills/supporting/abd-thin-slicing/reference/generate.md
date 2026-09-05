# Generate — abd-thin-slicing

## Pipeline

- **Before:** `abd-story-mapping` — story map must exist to slice.
- **After:** `abd-story-acceptance-criteria`, `abd-story-specification` — add story detail once priorities are set.

## Workflow order

1. Read inputs — story map / graph, PO or tech notes, risks and dependencies.
2. Mark spine vs optional — see `rules/map-sequential-spine-vs-optional-paths.md`.
3. Cut **vertical** slices — end-to-end demonstrable path per increment; avoid horizontal "finish epic A, then B."
4. Name increments for stakeholder-visible **capability**, not phase or stack labels.
5. Pull stories under each increment in **flow order** — verb-noun, copied **verbatim** from `story-map.md` / `story-graph.json` (character-for-character, including parentheticals). No actor prefix in story names.
6. Fill `templates/thin-slicing.md`.

## Pre-validate scanner

Before [`common/reference/rule-checklist.md`](../../../../../common/reference/rule-checklist.md), run:

```bash
python <skill-root>/scanners/story-name-exact-match-scanner.py --workspace <path-to-project>
```

Exit code 1 — fix name mismatches before proceeding.
