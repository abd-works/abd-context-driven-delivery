# Toast Snackbar

**Category:** User Actions & Overlays
**CLI template:** *(reference only — not in drawio-ux)*
**Areas:** `message` · `action`

Low-priority micro-banner floating momentarily at a screen edge.

## ASCII template

```
[Toast / Snackbar Layout]
┌───────────────────────────────────────┐
│                                       │
│                                       │
│ ┌───────────────────────────────────┐ │
│ │ Item deleted permanently.  [Undo] │ │
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[area-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `toast-snackbar.drawio` — grab the XML cells, fill area labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
