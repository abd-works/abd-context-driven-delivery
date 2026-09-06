# Spreadsheet

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `column-headers` · `row-headers` · `cells`

Infinite rows and columns of dense editable cells.

## ASCII template

```
[Matrix / Spreadsheet Layout]
┌───┬──────┬──────┬──────┬──────┬───────┐
│   │  A   │  B   │  C   │  D   │   E   │
├───┼──────┼──────┼──────┼──────┼───────┤
│ 1 │ Data │ Data │ Data │ Data │ Data  │
│ 2 │ Data │ Data │ Data │ Data │ Data  │
└───┴──────┴──────┴──────┴──────┴───────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `spreadsheet.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
