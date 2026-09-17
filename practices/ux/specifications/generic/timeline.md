# Timeline

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `events`

Central vertical/horizontal line tracking sequential events.

## ASCII template

```
[Timeline Layout]
┌───────────────────────────────────────┐
│ 2024 --(o)-- Project Kickoff Event    │
│          │                            │
│ 2025 --(o)-- Version 1.0 Launch Ready │
│          │                            │
│ 2026 --(o)-- Scale Infrastructure     │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `timeline.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
