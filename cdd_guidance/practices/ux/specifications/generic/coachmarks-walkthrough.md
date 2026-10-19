# Coachmarks Walkthrough

**Category:** User Actions & Overlays
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `target-element` · `callout-text` · `step-nav`

Guided overlay highlighting interface features sequentially.

## ASCII template

```
[Coachmarks / Walkthrough Layout]
┌───────────────────────────────────────┐
│ ┌────────┐  Step 1 of 3               │
│ │ BUTTON │<-- This tool exports       │
│ └────────┘    your analytics data.    │
│               [Next]                  │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `coachmarks-walkthrough.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
