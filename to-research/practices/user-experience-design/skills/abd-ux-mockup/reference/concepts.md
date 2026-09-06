# abd-ux-mockup — Concepts

## What is a mockup

A **mockup** is a structural wireframe that makes interaction decisions explicit. Its scope is whatever the team needs to validate — the entire application, a section, a flow, an epic, or a single story. We tend to work in small increments (a story, a screen, a feature) not because the tool demands it but because we want to see and validate what we're building before committing further.

It shows:

- **IA regions** as containers — unchanged from the structural IA, not invented here.
- **Exact control types** for each field: tree view, listbox, text input, dropdown, checkbox, radio, textarea — not generic "field" boxes.
- **Exact button placement and weight**: primary vs secondary, icon buttons vs text buttons, which actions are available at rest vs after selection.
- **Conditional states**: validation error placeholders, empty list states, disabled controls, selection highlighting, clipboard states (ghost/dimmed for cut, chain icons for linked) — placed where they appear, labelled in domain terms.
- **Exact interactions implied by each action**: what triggers, what changes, what the user does next.
- **Hierarchical structure**: tree views rendered with proper indentation, expand/collapse chevrons, icons per node type — not flattened into tables.

It also shows, per screen:

- **In-scope user stories** — listed alongside or below the wireframe, matching the initial IA's per-screen story list.
- **Domain terms** — the UL terms visible on this screen, listed alongside or below the wireframe, matching the initial IA's per-screen domain term list.

These lists appear in the drawio diagram as annotation boxes beside each screen, so the wireframe is self-contained and reviewable without flipping to the companion `.md` file.

It does not show colour, typography, spacing, or brand polish. It does not implement code. It does not invent controls that no AC or story justifies.

**Critical principle:** The mockup must faithfully reproduce the production UI structure as shown in design images. Do NOT substitute tables for trees, do NOT use fields when a listbox is called for, do NOT flatten hierarchical views into flat lists. Match the design.

---

## Source: initial IA

The screen spec lives in `docs/ux/initial-ia.md`. Each screen section defines:
- **Layout** (`sidebar`, `form`, `split-screen`, `modal`, `flyout`) — maps directly to `drawio-mockup.mjs` `layout` field.
- **Regions** with `slot`, `type`, `fields`, and `actions` — map directly to state JSON regions.
- **Stories** and **domain terms** — determine which AC clauses and UL terms are in scope.

## Design image reference

Before building the state JSON, the agent MUST:
1. Read ALL design images for the relevant screens from `Design/` folders.
2. Catalog what UX elements are actually shown: tree views, listboxes, toolbars with icon buttons, context menus, filter bars, etc.
3. Note indentation levels, expand/collapse state, icon types, selection behaviour, and groupings.
4. The state JSON and wireframe MUST match these design images — no reinterpretation, no substituting simpler controls.

---

## UI element types

| State type | Renders as | State keys |
| --- | --- | --- |
| `tree` | hierarchical node list with indent, expand/collapse, icons | `nodes[].{label, indent, expanded, icon, selected}` |
| `listbox` | selectable item list (not a data grid) | `items[].{label, icon, selected, dimmed, badge}` |
| `context-menu` | right-click popup menu with grouped actions | `groups[].items[].{label, shortcut}` |
| `toolbar-icons` | horizontal row of icon-style square buttons | `buttons[].{icon, tooltip, active}` |
| `filter-bar` | text input with search/clear affordance | `placeholder`, `value` |
| `browse-panel` | grid of category icon buttons | `categories[].{label, icon}` |
| `form` | label-input pairs + button row | `fields[].input`, `buttons[]` |
| `list` | column headers + data rows + action buttons | `columns[]`, `rows`, `actions[]` |
| `nav-tabs` | horizontal tab strip | `tabs[].label`, `tabs[].active` |
| `toolbar` | horizontal text button row (header/footer) | `buttons[]` |
| `button-bar` | horizontal button row (inline) | `buttons[]` |
| `chrome` | plain labelled band (dimmed panels) | `name` |

### Tree state format

```json
{
  "type": "tree",
  "name": "character tree",
  "nodes": [
    { "label": "All Characters", "indent": 0, "expanded": true, "icon": "group" },
    { "label": "Crowd 1", "indent": 1, "expanded": true, "icon": "crowd" },
    { "label": "Character 1", "indent": 2, "icon": "character" },
    { "label": "Character 2", "indent": 2, "icon": "character", "selected": true },
    { "label": "Crowd 2", "indent": 1, "expanded": false, "icon": "crowd" }
  ]
}
```

**Icons:** `group` (all), `crowd` (multi-person), `character` (single person), `folder`, `file`, `ability`, `movement`, `power`, `fx`, `sound`, `sequence`
**Indent:** integer 0–N indicating nesting depth
**Expanded/collapsed:** `expanded: true` renders ▼, `expanded: false` renders ▶, omit for leaf nodes

### Listbox state format

```json
{
  "type": "listbox",
  "name": "active roster",
  "items": [
    { "label": "Character 1", "icon": "character" },
    { "label": "Character 2", "icon": "character", "selected": true },
    { "label": "Character 3", "icon": "character", "dimmed": true }
  ]
}
```

**Dimmed:** indicates cut-to-clipboard state (ghost). **Selected:** highlighted item.

### Context menu state format

```json
{
  "type": "context-menu",
  "name": "character actions",
  "groups": [
    { "items": [
      { "label": "New", "shortcut": "Ctrl+N" },
      { "label": "Edit", "shortcut": "Ctrl+E" },
      { "label": "Delete", "shortcut": "Del" },
      { "label": "Save", "shortcut": "Ctrl+S" }
    ]},
    { "items": [
      { "label": "Cut", "shortcut": "Ctrl+X" },
      { "label": "Clone", "shortcut": "Ctrl+C" },
      { "label": "Link", "shortcut": "Ctrl+L" },
      { "label": "Paste", "shortcut": "Ctrl+V" }
    ]},
    { "items": [
      { "label": "Spawn", "shortcut": "Alt+S" },
      { "label": "Place", "shortcut": "Alt+P" }
    ]}
  ]
}
```

Groups are separated by horizontal dividers.

### Toolbar-icons state format

```json
{
  "type": "toolbar-icons",
  "name": "explorer toolbar",
  "buttons": [
    { "icon": "new-file", "tooltip": "New" },
    { "icon": "cut", "tooltip": "Cut" },
    { "icon": "copy", "tooltip": "Copy" },
    { "icon": "paste", "tooltip": "Paste" },
    { "icon": "add-crowd", "tooltip": "Add Crowd", "active": true },
    { "icon": "edit", "tooltip": "Edit" }
  ]
}
```

Rendered as square icon buttons in a row — not pill-shaped text buttons.

### Filter-bar state format

```json
{
  "type": "filter-bar",
  "name": "character filter",
  "placeholder": "Search characters…",
  "value": "Spyder"
}
```

### Browse-panel state format

```json
{
  "type": "browse-panel",
  "name": "browse characters",
  "categories": [
    { "label": "All Characters", "icon": "group" },
    { "label": "Heroes", "icon": "hero" },
    { "label": "Villains", "icon": "villain" }
  ]
}
```

### Field input types

| Value | Renders as |
| --- | --- |
| `text` | empty bordered rectangle |
| `textarea` | taller bordered rectangle |
| `dropdown` | rectangle with ▾ suffix and first option |
| `checkbox` | `☐ Label` inline |
| `radio` | `○ Label` inline |

---

## Domain terms — verbatim, screen-scoped

Only terms whose stories appear on this screen may appear. Copy verbatim from the domain-language file.

## Acceptance criteria — verbatim

Placed beside the wireframe, character-for-character. No rewording, shortening, or paraphrasing.

---

## The shape of a good state file

```json
{
  "target": "docs/ux/mockups/character-explorer.drawio",
  "screens": [{
    "name": "character explorer",
    "layout": "sidebar",
    "col": 0, "row": 0,
    "regions": [
      {
        "name": "explorer toolbar",
        "slot": "header",
        "type": "toolbar-icons",
        "buttons": [
          { "icon": "new-file", "tooltip": "New" },
          { "icon": "cut", "tooltip": "Cut" },
          { "icon": "copy", "tooltip": "Copy" },
          { "icon": "paste", "tooltip": "Paste" },
          { "icon": "add-crowd", "tooltip": "Add Crowd" },
          { "icon": "add-character", "tooltip": "Add Character" },
          { "icon": "edit", "tooltip": "Edit" }
        ]
      },
      {
        "name": "character filter",
        "slot": "panel",
        "type": "filter-bar",
        "placeholder": "Search characters…",
        "value": "Spyder"
      },
      {
        "name": "character tree",
        "slot": "panel",
        "type": "tree",
        "nodes": [
          { "label": "All Characters", "indent": 0, "expanded": true, "icon": "group" },
          { "label": "Crowd 1", "indent": 1, "expanded": true, "icon": "crowd" },
          { "label": "Character 1", "indent": 2, "icon": "character" },
          { "label": "Character 2", "indent": 2, "icon": "character" },
          { "label": "Crowd 2", "indent": 1, "expanded": false, "icon": "crowd" }
        ]
      },
      {
        "name": "tab bar",
        "slot": "body",
        "type": "nav-tabs",
        "tabs": [
          { "label": "Identities", "active": true },
          { "label": "Abilities" },
          { "label": "Movements" }
        ]
      },
      {
        "name": "identity list",
        "slot": "body",
        "type": "listbox",
        "items": [
          { "label": "Identity 1", "icon": "identity" },
          { "label": "Identity 2", "icon": "identity", "selected": true },
          { "label": "Identity 3", "icon": "identity" }
        ]
      }
    ]
  }],
  "connections": []
}
```

---

## Rendering approach: CLI vs AI-crafted XML

The skill supports two rendering paths. Choose based on screen complexity.

### CLI path (drawio-mockup.mjs)

Use the CLI when the screen contains **only** these element types:
- Forms, lists (tabular), nav-tabs, toolbars, button-bars, chrome
- AND the new types: tree, listbox, context-menu, toolbar-icons, filter-bar, browse-panel

The CLI generates correct drawio XML programmatically from the state JSON.

```powershell
node "<skill-root>/scripts/drawio-mockup.mjs" `
  save `
  --state "docs/ux/mockups/<screen-slug>-state.json" `
  --out   "docs/ux/mockups/<screen-slug>.drawio"
```

### AI-crafted XML path

Use AI-crafted drawio XML when:
- The screen has complex compositions not expressible in state JSON (overlapping panels, drag handles, unusual nesting)
- The design image shows layouts that the CLI grid system cannot reproduce
- You need pixel-level fidelity to a specific design image

Process:
1. Start from a screen-template `.drawio` fragment (from `screen-templates/`)
2. Read the production design images to understand exact layout
3. Hand-craft mxGraph XML cells for each element
4. Use the mxGraph XML patterns documented below

### mxGraph XML patterns for UX elements

**Tree node (leaf):**
```xml
<mxCell value="    Character 1" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=10;spacingLeft=20;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="W" height="22" as="geometry"/>
</mxCell>
```

**Tree node (expanded parent — ▼):**
```xml
<mxCell value="▼ Crowd 1" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=10;fontStyle=1;spacingLeft=INDENT;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="W" height="22" as="geometry"/>
</mxCell>
```

**Tree node (collapsed — ▶):**
```xml
<mxCell value="▶ Crowd 2" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=10;fontStyle=1;spacingLeft=INDENT;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="W" height="22" as="geometry"/>
</mxCell>
```

**Listbox item (normal):**
```xml
<mxCell value="Character 1" style="whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#e0e0e0;fontSize=10;verticalAlign=middle;align=left;spacingLeft=8;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="W" height="26" as="geometry"/>
</mxCell>
```

**Listbox item (selected):**
```xml
<mxCell value="Character 2" style="whiteSpace=wrap;html=1;fillColor=#c8e6c9;strokeColor=#4caf50;fontSize=10;fontStyle=1;verticalAlign=middle;align=left;spacingLeft=8;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="W" height="26" as="geometry"/>
</mxCell>
```

**Context menu container:**
```xml
<mxCell value="" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#000000;strokeWidth=1;shadow=1;" vertex="1" parent="1">
  <mxGeometry x="X" y="Y" width="180" height="H" as="geometry"/>
</mxCell>
```

**Context menu item:**
```xml
<mxCell value="Edit          Ctrl+E" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=10;fontFamily=monospace;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="170" height="22" as="geometry"/>
</mxCell>
```

**Context menu separator:**
```xml
<mxCell value="" style="line;strokeWidth=1;strokeColor=#cccccc;fillColor=none;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="170" height="1" as="geometry"/>
</mxCell>
```

**Story list annotation (placed below or beside the screen):**
```xml
<mxCell value="Stories&#xa;─────────────────&#xa;• Story Title 1&#xa;• Story Title 2&#xa;• Story Title 3" style="text;html=0;align=left;verticalAlign=top;fontSize=10;fontFamily=monospace;fillColor=#fffde7;strokeColor=#f9a825;rounded=1;arcSize=8;spacingLeft=6;spacingTop=4;spacingRight=6;spacingBottom=4;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="X" y="Y" width="260" height="H" as="geometry"/>
</mxCell>
```

**Domain terms annotation (placed below the story list):**
```xml
<mxCell value="Domain terms&#xa;─────────────────&#xa;• term 1&#xa;• term 2&#xa;• term 3" style="text;html=0;align=left;verticalAlign=top;fontSize=10;fontFamily=monospace;fillColor=#e8f5e9;strokeColor=#4caf50;rounded=1;arcSize=8;spacingLeft=6;spacingTop=4;spacingRight=6;spacingBottom=4;whiteSpace=wrap;" vertex="1" parent="1">
  <mxGeometry x="X" y="Y" width="260" height="H" as="geometry"/>
</mxCell>
```

Annotation boxes use light yellow (stories) and light green (domain terms) to distinguish them from the wireframe elements. Place them below or to the right of the screen they annotate.

**Icon toolbar button (square):**
```xml
<mxCell value="✂" style="rounded=1;arcSize=10;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;fontSize=14;verticalAlign=middle;align=center;" vertex="1" parent="PARENT">
  <mxGeometry x="X" y="Y" width="28" height="28" as="geometry"/>
</mxCell>
```

---

## CLI reference

```
drawio-mockup.mjs save --state <state.json> --out <file.drawio>
drawio-mockup.mjs init --out <state.json>
```

### Layouts

| Layout | Columns (slot → width) |
| --- | --- |
| `sidebar` | panel 33% · body 67% |
| `split-screen` | left 50% · right 50% |
| `form` | body 100% |
| `modal` | body 100% (rounded border) |
| `flyout` | body 65% · panel 35% |
| `stack` | body 100% |

### Grid positioning

Use `col` and `row` integers on each screen to arrange screens in a grid:
- **Linear flow** (user must pass through): increment `col` left to right.
- **Optional branch** (user may choose): increment `row` top to bottom within the same `col`.

This matches the convention established in `drawio-ux.mjs` (the IA diagram CLI).
