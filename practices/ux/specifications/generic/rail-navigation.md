# Rail Navigation

**Category:** Navigation & Navigation Housing
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `rail` · `body`

Ultra-skinny vertical icon-only sidebar for high-density apps.

## ASCII template

```
[Rail Navigation]
┌───┬───────────────────────────────────┐
│[*]│                                   │
│[*]│                                   │
│[*]│           Main Workspace          │
│[*]│                                   │
└───┴───────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `rail-navigation.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
