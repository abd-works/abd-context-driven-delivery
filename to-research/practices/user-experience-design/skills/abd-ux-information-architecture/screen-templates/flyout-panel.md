# Flyout Panel

**Category:** User Actions & Overlays
**CLI template:** `--layout flyout`
**Slots:** `body` · `panel`

Contextual side-sheet sliding out over the main content.

## ASCII template

```
[Detail View / Flyout Panel]
┌───────────────────────────────────┬───┐
│                                   │ D │
│                                   │ e │
│       Main App Grid View          │ t │
│       (Dimmed out)                │ a │
│                                   │ i │
│                                   │ l │
└───────────────────────────────────┴───┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `flyout-panel.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
