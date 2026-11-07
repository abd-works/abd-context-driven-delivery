# Fab Menu

**Category:** Navigation & Navigation Housing
**CLI template:** *(reference only — not in drawio-ux)*
**Areas:** `body` · `fab` · `fab-actions`

Circular floating trigger opening contextual action sub-menus.

## ASCII template

```
[Floating Action Button (FAB) Menu]
┌───────────────────────────────────────┐
│                                       │
│                                ( O )  │
│                                ( O )  │
│                                [ X ]  │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[area-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `fab-menu.drawio` — grab the XML cells, fill area labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
