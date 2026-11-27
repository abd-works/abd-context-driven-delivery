# Graph rule validation

**Generated:** 2026-11-18 21:08:12 UTC
**Project:** spider-man-shopping
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-my-first-feature\.sessions\my-first-feature\.context\checked-graphs\stories-story-map-20261118T210810\graph.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 12

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `verb-noun-format`

Rule text: [stories/stories.md:80](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L80)

### `story-name-captures-system-mechanic`

Rule text: [stories/stories.md:81](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L81)

### `four-to-nine-children`

Rule text: [stories/stories.md:82](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L82)

### `story-scenarios-at-most-seven`

Rule text: [stories/stories.md:83](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L83)

### `branch-on-mechanical-uniqueness`

Rule text: [stories/stories.md:84](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L84)

### `right-size-story-nodes`

Rule text: [stories/stories.md:85](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L85)

### `behaviours-not-one-time-tasks`

Rule text: [stories/stories.md:86](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L86)

### `kebab-case-paths`

Rule text: [stories/stories.md:87](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L87)

### `story-map-links-to-markdown`

Rule text: [stories/stories.md:88](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L88)

## Judgment — `demos/spider-man-shopping/.context/story-map.md`

### `do-not-invent-requirements` — Fail
- story-map.md:12 `Charge Order Payment`: the request asked only for Spider-Man shopping; no source names a Payment Service or requires a system-to-system charge, so this boundary story is an assumed interaction. Keep it only if the person confirms the demo should show a system story.

**Passes:** vocabulary-traces-to-domain-source (no domain model exists; plain shopping terms used), read-all-source-context-in-full (the one source, the chat request, is named), verb-noun-format, story-name-captures-system-mechanic, four-to-nine-children (the epic has 4 stories), story-scenarios-at-most-seven (no scenarios yet), branch-on-mechanical-uniqueness, right-size-story-nodes, behaviours-not-one-time-tasks, kebab-case-paths (no story files yet), story-map-links-to-markdown (headings at column 0; stories are plain text because no story files exist).
