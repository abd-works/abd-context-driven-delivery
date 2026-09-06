# Empty State

**Category:** User Actions & Overlays
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `icon` · `headline` · `subtext` · `cta`

Educational, graphic-rich layout shown when no data exists yet.

## ASCII template

```
[Empty State Layout]
┌───────────────────────────────────────┐
│                                       │
│                (  !  )                │
│           No Messages Yet             │
│    Click the plus button below to     │
│         start a conversation.         │
│                                       │
│             [ + Start ]               │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `empty-state.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
