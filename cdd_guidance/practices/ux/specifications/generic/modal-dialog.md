# Modal Dialog

**Category:** User Actions & Overlays
**CLI template:** `--layout modal`
**Slots:** `body`

Locked, centered modal window dimming out the backdrop.

## ASCII template

```
[Modal / Dialog Layout]
┌───────────────────────────────────────┐
│ ╔════════ MODAL WINDOW ═════════════╗ │
│ ║                                   ║ │
│ ║   Are you sure you want to exit?  ║ │
│ ║                                   ║ │
│ ║   [ Cancel ]       [ Confirm ]    ║ │
│ ╚═══════════════════════════════════╝ │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `modal-dialog.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
