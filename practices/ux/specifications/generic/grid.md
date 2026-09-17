# Grid

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `items`

Symmetrical rows and columns of uniform cards or asset previews.

## ASCII template

```
[Grid Layout]
┌───────────────┬───────────────┬───────┐
│ ┌───────────┐ │ ┌───────────┐ │ ┌───┐ │
│ │   Item    │ │ │   Item    │ │ │   │ │
│ └───────────┘ │ └───────────┘ │ └───┘ │
├───────────────┼───────────────┼───────┤
│ ┌───────────┐ │ ┌───────────┐ │ ┌───┐ │
│ │   Item    │ │ │   Item    │ │ │   │ │
│ └───────────┘ │ └───────────┘ │ └───┘ │
└───────────────┴───────────────┴───────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `grid.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
