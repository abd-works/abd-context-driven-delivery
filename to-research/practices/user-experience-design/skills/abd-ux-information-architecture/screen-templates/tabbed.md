# Tabbed

**Category:** Navigation & Navigation Housing
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `tab-bar` · `body`

Inline tab headers used to switch views inside a wrapper.

## ASCII template

```
[Tabbed Layout]
┌───────────────────────────────────────┐
│  [ Tab 1 ]  *[ Tab 2 ]*   [ Tab 3 ]  │
├───────────────────────────────────────┤
│ ┌───────────────────────────────────┐ │
│ │ Active Content for Tab 2          │ │
│ │                                   │ │
│ └───────────────────────────────────┘ │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `tabbed.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
