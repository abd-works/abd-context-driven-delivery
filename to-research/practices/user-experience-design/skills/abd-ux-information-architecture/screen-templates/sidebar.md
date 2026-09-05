# Sidebar

**Category:** Navigation & Navigation Housing
**CLI template:** `--layout sidebar`
**Slots:** `panel` · `body`

Left/right fixed vertical panel beside a main workspace.

## ASCII template

```
[Sidebar Layout]
┌───┬───────────────────────────────────┐
│ L │ [Header]                          │
│ o ├───────────────────────────────────┤
│ g │                                   │
│ o │                                   │
├───┤          Main Workspace           │
│ M │                                   │
│ e │                                   │
│ n │                                   │
│ u │                                   │
└───┴───────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `sidebar.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
