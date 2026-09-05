# Full Screen Media

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `logo` · `menu` · `headline` · `cta`

Immersive background video/image with minimal overlay text.

## ASCII template

```
[Full-Screen Media Layout]
┌───────────────────────────────────────┐
│ [Logo]                       [Menu]   │
│                                       │
│        =======================        │
│        │ BACKGROUND VIDEO/IMG│        │
│        │  Centered Headline  │        │
│        │     [Button]        │        │
│        =======================        │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `full-screen-media.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
