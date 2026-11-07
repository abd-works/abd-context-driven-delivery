# Carousel Slider

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Areas:** `prev` · `cards` · `next`

Linear horizontal row of elements scrolled via touch/arrows.

## ASCII template

```
[Carousel / Slider Layout]
┌───────────────────────────────────────┐
│    ┌────────┐  ┌────────┐  ┌────────┐ │
│ <  │ Card 1 │  │ Card 2 │  │ Card 3 │>│
│    └────────┘  └────────┘  └────────┘ │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[area-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `carousel-slider.drawio` — grab the XML cells, fill area labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
