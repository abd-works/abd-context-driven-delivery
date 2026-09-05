# Drawer Hamburger

**Category:** Navigation & Navigation Housing
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `nav-links` · `dimmed-content`

Off-screen overlay panel that slides into view when triggered.

## ASCII template

```
[Drawer / Hamburger Layout]
┌───────┬───────────────────────────────┐
│ Menu  │                               │
│ Link1 │                               │
│ Link2 │         Dimmed Main           │
│ Link3 │           Content             │
│       │                               │
│ Close │                               │
└───────┴───────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `drawer-hamburger.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
