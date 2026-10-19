# List

**Category:** Content & Data Organization
**CLI template:** `--layout stack`
**Slots:** `rows`

Single-column vertical stack ideal for scanning text-dense items.

## ASCII template

```
[List Layout]
┌───────────────────────────────────────┐
│ [Img]  Title Row - Subtitle Info      │
├───────────────────────────────────────┤
│ [Img]  Title Row - Subtitle Info      │
├───────────────────────────────────────┤
│ [Img]  Title Row - Subtitle Info      │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `list.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
