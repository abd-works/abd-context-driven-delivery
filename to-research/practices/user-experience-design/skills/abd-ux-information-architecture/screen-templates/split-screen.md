# Split Screen

**Category:** Screen & Core Page Skeletons
**CLI template:** `--layout split-screen`
**Slots:** `left` · `right`

50/50 or fixed/fluid dual-panel layout (e.g., Map + List).

## ASCII template

```
[Split-Screen Layout]
┌───────────────────┬───────────────────┐
│                   │                   │
│    Left Panel     │    Right Panel    │
│   (e.g., Map)     │   (e.g., List)    │
│                   │                   │
└───────────────────┴───────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `split-screen.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
