# Card Based

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `cards`

Entire screen comprised of modular moveable masonry blocks.

## ASCII template

```
[Card-Based Layout]
┌───────────────────────────────────────┐
│ ┌───────────┐ ┌───────────┐ ┌───────┐ │
│ │ Card A    │ │ Card B    │ │ Card C│ │
│ └───────────┘ └───────────┘ └───────┘ │
│ ┌───────────┐ ┌───────────┐ ┌───────┐ │
│ │ Card D    │ │ Card E    │ │ Card F│ │
│ └───────────┘ └───────────┘ └───────┘ │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `card-based.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
