# Kanban Board

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `todo` · `in-progress` · `done`

Vertical columns representing workflow status stages.

## ASCII template

```
[Kanban Board Layout]
┌───────────┬───────────┬───────────────┐
│ To Do     │ In Prog   │ Done          │
├───────────┼───────────┼───────────────┤
│ [Task 1]  │ [Task 3]  │ [Task 5]      │
│ [Task 2]  │           │ [Task 6]      │
└───────────┴───────────┴───────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `kanban-board.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
