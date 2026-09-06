# Mockup — {{SCOPE_NAME}}

> **Companion to** `docs/ux/mockups/{{SLUG}}.drawio`. Author or update **this file first**, then regenerate the wireframe from the state file. After any manual edits in Draw.io, sync changes back here.

## Metadata

| Field | Value |
| --- | --- |
| Scope | {{SCOPE_NAME}} — describe the screens, epic, or stories covered |
| Initial IA | `docs/ux/initial-ia.md` |
| AC source | {{ACCEPTANCE_CRITERIA_PATH}} |
| Domain terms | {{DOMAIN_TERMS_PATH}} |
| State file | `docs/ux/mockups/{{SLUG}}-state.json` |
| Wireframe | `docs/ux/mockups/{{SLUG}}.drawio` |
| Last updated | {{ISO_DATE}} |

## Description

{{ONE_PARAGRAPH}}

What screens are in scope, what the u er does on them, which stories are represented, what interaction decisions this pass resolves.

---

## Design reference

Before building the state JSON, all relevant design images were reviewed. This section catalogs what UX elements appear in the production design.

| Design image | Panel/Region | UX element type | Key observations |
| --- | --- | --- | --- |
| `Design/{{FOLDER}}/{{IMAGE}}.png` | {{region name}} | {{tree / listbox / toolbar-icons / context-menu / filter-bar / browse-panel / form / list}} | {{indent levels, icon types, selection state, groupings, shortcuts, etc.}} |

<!-- One row per region observed in design images. This catalog constrains the state JSON below. -->

**Design principles applied:**
- Trees are trees (hierarchical with expand/collapse) — never flattened into tables
- Listboxes are listboxes (selectable item lists) — never rendered as form fields
- Icon toolbars are icon toolbars (square icon buttons) — never rendered as text pill buttons
- Context menus have grouped actions with keyboard shortcuts — never flattened into button bars

---

## Screens

For each screen in scope, copy its layout and regions from `initial-ia.md` and add the interaction decisions made in this pass.

### {{SCREEN_NAME}}

**Layout:** {{layout}}

**Stories:**
- (U) {{Epic}} → {{Story title}}
- (S) {{Epic}} → {{Story title}}

**Domain terms:** {{Term A}} · {{Term B}} · {{Term C}}

| Region | Slot | Type | Controls | Interaction decisions |
| --- | --- | --- | --- | --- |
| {{region name}} | {{slot}} | {{tree\|listbox\|toolbar-icons\|context-menu\|filter-bar\|browse-panel\|form\|list\|nav-tabs\|toolbar}} | {{controls, verbatim domain labels}} | {{what this pass decided: disabled state, error placement, primary/secondary weight, conditional visibility, indent levels, expand/collapse default}} |

**Conditional states:**
- {{State name}}: {{what changes — e.g. selection highlighting, clipboard ghost, expanded/collapsed}}

<!-- duplicate ### block for each screen -->

---

## Affordance trace

Every control traces to an AC clause. Reviewers verify coverage here without opening the AC file.

| Affordance | AC story | AC clause |
| --- | --- | --- |
| {{control label}} | {{story title}} | AC {{n}} — {{one-line summary of the clause}} |

<!-- Row per control. Label must be verbatim domain term. -->

---

## CLI

```powershell
node "C:\dev\agilebydesign-skills\skills\user-experience-design\abd-ux-mockup\scripts\drawio-mockup.mjs" `
  save `
  --state "docs/ux/mockups/{{SLUG}}-state.json" `
  --out   "docs/ux/mockups/{{SLUG}}.drawio"
```

---

## Change log

| Date | Direction | Summary |
| --- | --- | --- |
| {{ISO_DATE}} | initial | First draft. |
