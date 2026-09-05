# Single Page Spa

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `header` · `section-1` · `section-2`

One long-scrolling page with sticky anchor nav links.

## ASCII template

```
[Single-Page Layout (SPA)]
┌───────────────────────────────────────┐
│ Logo   [Link1]  *[Link2]*  [Link3]    │
├───────────────────────────────────────┤
│ [Section 1: Hero Intro]               │
│                                       │
│ ~ ~ ~ ~ ~ ~ ~ Scroll ~ ~ ~ ~ ~ ~ ~ ~  │
│ *[Section 2: Features]*  <-- Viewport │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `single-page-spa.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
