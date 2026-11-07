# Masonry

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Areas:** `col-1` · `col-2` · `col-3`

Staggered-height columns fitting uneven content fluidly (Pinterest).

## ASCII template

```
[Masonry Layout]
┌────────────┬────────────┬────────────┐
│ ┌────────┐ │ ┌────────┐ │ ┌────────┐ │
│ │ Short  │ │ │ Tall   │ │ │ Medium │ │
│ └────────┘ │ │        │ │ └────────┘ │
│ ┌────────┐ │ │        │ │ ┌────────┐ │
│ │ Medium │ │ └────────┘ │ │ Short  │ │
│ └────────┘ │ ┌────────┐ │ └────────┘ │
└────────────┴────────────┴────────────┘
```

## Fill guide

Replace each `[area-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `masonry.drawio` — grab the XML cells, fill area labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
