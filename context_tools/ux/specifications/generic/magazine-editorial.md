# Magazine Editorial

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `main-story` · `side-story-1` · `side-story-2`

Multi-column, varied-size grids mimicking news print.

## ASCII template

```
[Magazine / Editorial Layout]
┌───────────────────────────────────────┐
│              MAIN LOGO                │
├───────────────────────────────────────┤
│ ┌───────────────────┐ ┌─────────────┐ │
│ │    BIG STORY      │ │ Side Story  │ │
│ │    HEADLINE       │ └─────────────┘ │
│ │                   │ ┌─────────────┐ │
│ │ [Large Image]     │ │ Side Story  │ │
│ └───────────────────┘ └─────────────┘ │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `magazine-editorial.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
