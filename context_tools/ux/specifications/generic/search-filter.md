# Search Filter

**Category:** User Actions & Overlays
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `search-bar` · `filters` · `results`

Search/Omnibox paired with a persistent filtering pane.

## ASCII template

```
[Search & Filter Layout]
┌───────────────────────────────────────┐
│ [ Search items...                 ]   │
├───────────┬───────────────────────────┤
│ Filters   │                           │
│ [ ] Cat A │     Search Results        │
│ [ ] Cat B │     Grid or List Area     │
└───────────┴───────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `search-filter.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
