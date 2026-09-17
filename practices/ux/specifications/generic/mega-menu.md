# Mega Menu

**Category:** Navigation & Navigation Housing
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `header` · `category-1` · `category-2` · `category-3`

Massive multi-column dropdown panel exposed from main header.

## ASCII template

```
[Mega Menu Layout]
┌───────────────────────────────────────┐
│ [Logo]  *[Shop]*  About  Contact      │
├───────────────────────────────────────┤
│ │ Category 1 │ Category 2 │ Cat 3   │ │
│ │ - Item A   │ - Item X   │ - Ultra │ │
│ │ - Item B   │ - Item Y   │ - Mega  │ │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `mega-menu.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
