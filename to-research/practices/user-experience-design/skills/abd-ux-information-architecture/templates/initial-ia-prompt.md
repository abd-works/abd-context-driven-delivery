# initial-ia external prompt template

This template produces a **draw.io XML diagram** of the information architecture.
Fill every `{{SLOT}}` from `docs/ux/initial-ia.md`, then paste the filled prompt into any AI chat
(ChatGPT, Claude.ai, Copilot, Cursor, etc.) and ask it to return the result as raw draw.io XML.
Save the returned XML to `docs/ux/initial-ia.drawio`.

---

```
Draw the initial information architecture for {{SCOPE}} as a draw.io diagram.

Return ONLY the raw mxGraph XML — no explanation, no markdown fences.
Start the response with: <?xml version="1.0" encoding="UTF-8"?>

══════════════════════════════════════════════════════════════
STYLE CONTRACT — apply to every element without exception
══════════════════════════════════════════════════════════════

SCREENS
  shape:    rectangle
  fill:     #ffffff (white)
  stroke:   #000000 (black), 2px
  label:    BOLD, fontSize=13, top-aligned
  special:  modal screens use rounded=1; arcSize=4

REGION BANDS (subdivisions inside a screen rectangle)
  fill:     #ffffff (white)
  stroke:   #000000 (black), 1px
  label:    fontSize=11, top-left aligned
  chrome bands (toolbar, header, footer, sidebar, crowd tree, status bar):
    label style: ITALIC — no content written inside them, label only

TRANSITIONS (arrows between screens)
  style:    orthogonalEdgeStyle, endArrow=block, endFill=1
  stroke:   #000000
  label:    fontSize=10, short trigger phrase
  tab-switch arrows: dashed=1

ANNOTATIONS (Stories / Domain terms boxes below each screen)
  fill:     none
  stroke:   none
  fontSize: 10

NO colour fills other than white.
NO shadows. NO rounded corners except modal screens.
Canvas: 3300 × 2550. Primary flow left-to-right. Tab siblings below parent row.

══════════════════════════════════════════════════════════════
DRAWING MODEL — follow these rules without exception
══════════════════════════════════════════════════════════════

1. SCREENS
   Every screen is a large rectangle with a BOLD name at the top.
   Tab-state siblings (e.g. "crowd manager — identities", "crowd manager — abilities")
   are drawn as separate screen boxes — never as sub-regions of one box.
   Inactive tab names appear as greyed labels in a tab bar inside each sibling box.

2. REGION BANDS
   Inside each screen rectangle draw stacked rectangular bands for each region.
   Chrome bands (toolbar, sidebar, header, footer, crowd tree, status bar):
     — LABEL ONLY (italic). Write nothing inside them.

3. LIST / COLLECTION REGIONS
   Draw 2–3 representative item rows as small inner rectangles.
   Each row contains only the VISIBLE FIELD NAMES separated by ·
   Example: [ name · activation key · persistent · attack ]
   Below the rows draw one verb-row strip: create · remove · play · stop · edit · reorder
   Never write "per item: …" prose. Never put actions inside row boxes.

4. EDIT → NEW SCREEN
   When the verb row contains "edit" or "configure", draw a transition arrow to a
   named detail screen labeled "{{item}} editor". That detail screen is a full site-map
   node with its own region bands.

5. TRANSITIONS
   Primary flow: left-to-right horizontal arrows.
   Tab switches: short horizontal or vertical arrows between sibling boxes, dashed.
   Branch/optional screens: vertical arrows above or below the main row.
   Return transitions: curved arcs back over the main row.
   Every arrow has a short trigger label.

6. ANNOTATIONS (below each screen box, not inside it)
   Two plain-text boxes per screen:
   • Stories: list the ~4 story titles (titles only — no acceptance criteria)
   • Domain terms: list only terms visible as field labels or row-type names (max ~5)

══════════════════════════════════════════════════════════════
SCREENS
══════════════════════════════════════════════════════════════

{{SCREEN_BLOCKS}}

Each screen block follows this pattern when filling:

  SCREEN: [name]
  Layout: [layout descriptor — e.g. modal dialog / header + left panel + body + footer]
  Inactive tabs (greyed, if any): [other tab names]

  Chrome bands (italic label only — NO content):
    [region name], [region name], ...

  Content bands:
    [region name]
      rows: [field 1] · [field 2] · [field 3]
      verb row: [action 1] · [action 2] · [action 3]
      edit → new screen: [detail screen name]   ← only if edit is in verb row

  Stories: [title 1] · [title 2] · [title 3] · [title 4]
  Domain terms: [term 1] · [term 2] · [term 3]

══════════════════════════════════════════════════════════════
TRANSITIONS
══════════════════════════════════════════════════════════════

{{TRANSITIONS}}

Format: screen-a ──► screen-b   trigger: "label"
Tab switches (dashed arrow): sibling-a ──► sibling-b   trigger: "selects {{tab}} tab"
Edit opens: screen ──► detail-screen   trigger: "opens {{name}} editor"

══════════════════════════════════════════════════════════════
DRAW THIS NOW
══════════════════════════════════════════════════════════════
- Every screen: white rectangle, black border, bold name
- Chrome bands: italic label only, no content
- Content bands: 2–3 item rows (field labels · separated) + verb row below
- Tab siblings: separate screen boxes with greyed inactive tab labels
- Edit actions: dashed arrow to a named detail screen
- Every transition: directed labeled arrow, black
- Stories annotation: ~4 titles below each screen, no border
- Domain terms annotation: visible-field terms only, max ~5, no border
- No prose descriptions. No colour fills. No acceptance criteria. No controls.
```

---

## Slot reference

| Slot | Source | Notes |
| --- | --- | --- |
| `{{SCOPE}}` | user-supplied | e.g. `Full Application`, `Crowd Manager epic` |
| `{{SCREEN_BLOCKS}}` | `initial-ia.md` → screens | One block per screen. Tab siblings get their own block. Primary flow L→R; tab siblings below parent row. |
| `{{TRANSITIONS}}` | `initial-ia.md` → transitions | One line per arrow (outgoing only, to avoid duplicates). Include tab-switch and edit-opens arrows explicitly. |
