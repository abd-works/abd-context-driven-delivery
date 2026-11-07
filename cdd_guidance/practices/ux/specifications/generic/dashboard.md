# Dashboard

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Areas:** `header` · `nav` · `main`

Grid of modular widgets/cards for data viz and quick actions.

## ASCII template

```
[Dashboard Layout]
┌───────────────────────────────────────┐
│ [Header]                              │
├───────┬───────────────────────────────┤
│       │ [Metric 1] [Metric 2]         │
│ Nav   │ ┌────────┐ ┌────────┐         │
│ Bar   │ │ Graph  │ │ Recent │         │
│       │ │ Block  │ │ Activity         │
│       │ └────────┘ └────────┘         │
└───────┴───────────────────────────────┘
```

## Fill guide

Replace each `[area-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `dashboard.drawio` — grab the XML cells, fill area labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
