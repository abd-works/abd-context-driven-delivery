# Asymmetrical

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `large` · `small-a` · `small-b`

Unbalanced grid elements to break monotony and guide focus.

## ASCII template

```
[Asymmetrical Layout]
┌───────────────────────────────────────┐
│ [Header]                              │
├───────────────────┬───────────────────┤
│                   │  [Small Callout]  │
│    [Huge Bold     ├───────────────────┤
│     Headline]     │                   │
│                   │  [Image Box]      │
└───────────────────┴───────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `asymmetrical.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
