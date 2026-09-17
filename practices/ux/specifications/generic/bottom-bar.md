# Bottom Bar

**Category:** Navigation & Navigation Housing
**CLI template:** *(reference only — not in drawio-ux)*
**Slots:** `body` · `nav-bar`

Mobile-first sticky bottom navigation for thumb-reachability.

## ASCII template

```
[Bottom Bar Layout]
┌───────────────────────────────────────┐
│                                       │
│             Mobile Content            │
│                                       │
├───────────────────────────────────────┤
│  [Home]  [Search]  [Inbox]  [Profile] │
└───────────────────────────────────────┘
```

## Fill guide

Replace each `[slot-name]` zone with the actual region content:
- **List region:** bold header + 2 representative data rows + verb row
- **Form region:** bold header + field label rows
- **Chrome region (repeated):** use `············` dotted lines instead of solid `---`/`|`
  to signal the region is dimmed (repeats unchanged from the primary tab screen)

Companion drawio fragment: `bottom-bar.drawio` — grab the XML cells, fill slot labels,
reposition the screen cell (x/y), rename IDs, paste into your target `.drawio` file.
