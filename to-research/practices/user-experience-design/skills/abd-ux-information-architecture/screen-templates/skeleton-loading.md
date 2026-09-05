# Skeleton Loading

**Category:** User Actions & Overlays
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `placeholder-rows`

Wireframe-like shapes animating while actual data fetches.

## ASCII template

```
[Skeleton Loading Layout]
┌───────────────────────────────────────┐
│ [///]  //////////////////////////////  │
├───────────────────────────────────────┤
│ [///]  //////////                      │
├───────────────────────────────────────┤
│ [///]  /////////////////               │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `skeleton-loading.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
