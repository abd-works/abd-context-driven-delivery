# Holy Grail

**Category:** Screen & Core Page Skeletons
**CLI template:** `--layout holy-grail`
**Slots:** `header` · `nav` · `body` · `aside` · `footer`

Header + footer + three columns: left nav, body, right aside.

## ASCII template

```
[Holy Grail Layout]
┌───────────────────────────────────────┐
│                Header                 │
├───────────┬───────────────┬───────────┤
│  Left Nav │  Main Content │ Right Bar │
│           │               │           │
├───────────┴───────────────┴───────────┤
│                Footer                 │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `holy-grail.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
