# Comparison Matrix

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `features` · `plan-columns`

Side-by-side spec sheets/tables for product options.

## ASCII template

```
[Comparison Matrix Layout]
┌────────────┬────────────┬─────────────┐
│ Feature    │ Plan Basic │ Plan Pro    │
├────────────┼────────────┼─────────────┤
│ Storage    │ 10 GB      │ Unlimited   │
│ Support    │ Email      │ 24/7 Phone  │
└────────────┴────────────┴─────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `comparison-matrix.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
