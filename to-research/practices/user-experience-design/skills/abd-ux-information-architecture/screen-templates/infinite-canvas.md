# Infinite Canvas

**Category:** Screen & Core Page Skeletons
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `nodes` · `frames` · `viewport`

Borderless 2D pan/zoom workspace (e.g., Miro, Figma).

## ASCII template

```
[Infinite Canvas]
   - - - - - - - - - - - - - - - -
  │    [Node] ------> [Node]      │
  │      ^                        │
  │      |         ┌────────┐     │
  │    [Node]      │ Frame  │     │
   - - - - - - - - └────────┘ - -
  (Viewable area pans in any direction)
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `infinite-canvas.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
