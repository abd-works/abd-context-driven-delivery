# Parallax

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Areas:** `layer-slow` · `layer-mid` · `layer-fast`

Multi-layered background/foreground scrolling at different speeds.

## ASCII template

```
[Parallax Layout]
┌───────────────────────────────────────┐
│ [Layer 3: Slow Foreground Stars]      │
│                                       │
│    [Layer 2: Midground Mountain]      │
│                                       │
│        [Layer 1: Fast Content Text]   │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[area-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `parallax.drawio` — grab the XML cells, fill area labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
