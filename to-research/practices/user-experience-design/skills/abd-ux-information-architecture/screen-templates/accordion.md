# Accordion

**Category:** Content & Data Organization
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `section-headers` · `expanded-content`

Vertically stacked headers that expand to reveal content blocks.

## ASCII template

```
[Accordion Layout]
┌───────────────────────────────────────┐
│ [+] Section Title One                 │
├───────────────────────────────────────┤
│ [-] Section Title Two                 │
│   Hidden details and paragraphs       │
│   expand smoothly right here.         │
├───────────────────────────────────────┤
│ [+] Section Title Three               │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `accordion.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
