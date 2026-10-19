# Z Pattern

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `logo` · `top-right` · `value-prop` · `cta`

Landing page elements placed along a diagonal zig-zag visual path.

## ASCII template

```
[Z-Pattern Layout]
┌───────────────────────────────────────┐
│ [Logo]-------------------------[Login]│
│                             /         │
│                           /           │
│                         /             │
│                       /               │
│ [Big Value Prop]----------------[CTA] │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `z-pattern.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
