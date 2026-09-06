# ARIA Pipeline — Mockup (Detailed) Fidelity

This skill promotes WAI-ARIA from **structural fidelity** (IA output) to **detailed fidelity** — the second stage of the ARIA design pipeline.

## Pipeline position

```
IA skill                      Mockup skill              Spec skill
aria.yaml (structural)   →   aria.yaml + .md      →   aria.yaml + .md
                             (detailed)               (complete)
```

ARIA input is optional. If structural `aria.yaml` exists from the IA skill the mockup skill reads it and promotes each node to detailed fidelity. If not, the skill constructs the detailed tree from `initial-ia.md` and the design image catalog. Either path produces the same output.

---

## Input resolution

Before generating, check:

1. **IA output** — does `docs/ux/ia/<screen-slug>.aria.yaml` exist for the in-scope screen?
   - If yes: read the structural tree. Promote every node to detailed fidelity per the table below. Use the promoted tree as the state source for the wireframe.
2. **No prior ARIA** — read the screen regions from `docs/ux/initial-ia.md` and the design image catalog. Construct the detailed tree directly from that context.

---

## Detailed fidelity — what to add at this stage

At mockup fidelity, every control is present with its exact type, all live states, and required relationship attributes.

**Promotion rules:**

| Structural (IA) | Detailed (Mockup) | What to add |
|---|---|---|
| `button "Create Campaign"` | `button "Create Campaign" [haspopup=dialog]` | `haspopup`, `expanded` where applicable |
| `list "Campaigns"` | `grid "Campaigns" [rowcount=N]` | Promote to `grid`; add `columnheader` and representative `row` with `gridcell` nodes |
| `navigation "Main"` | `navigation "Main" [label="Main navigation"]` | Explicit `aria-label` |
| `button "Toggle sidebar"` | `button "Toggle sidebar" [expanded=true] [controls=main-nav]` | `expanded`, `controls` |
| `dialog "Create Campaign"` (stub) | Full `dialog` with all fields, required markers, primary/secondary actions | Complete contents |

**Add at this stage:**

- Exact control type for every input: `textbox`, `combobox`, `checkbox`, `radio`, `searchbox`, `spinbutton`, `slider`
- All live states: `expanded`, `selected`, `checked`, `disabled`, `required`, `invalid`
- Relationship attributes that define interaction: `controls`, `owns`, `describedby`, `labelledby`
- Toolbar composition: named `toolbar` with individual button roles
- Grid/table structure: `columnheader` per column, representative `row` with `gridcell` nodes
- Dialog complete contents: all fields, required markers, primary and secondary actions

---

## Output format

One file per screen: `docs/ux/mockups/<screen-slug>.aria.yaml`

Use Playwright WAI-ARIA snapshot syntax. Screen slug matches the screen being mocked up.

**Example — Campaigns list at detailed fidelity:**

```yaml
- document:
  - banner:
    - button "Toggle sidebar" [expanded=true] [controls=main-nav]
    - button "Toggle theme"
    - img "TS" [haspopup=menu] [label="User menu"]
  - navigation "Main" [label="Main navigation"]:
    - link "Dashboard" [current=false]
    - link "Campaigns" [current=true]
    - link "Vouchers" [current=false]
  - main:
    - heading "Campaigns" [level=1]
    - toolbar [label="Campaign actions"]:
      - button "Create Campaign" [haspopup=dialog]
      - searchbox "Search campaigns"
      - combobox "Status" [expanded=false] [haspopup=listbox]
    - grid "Campaigns" [rowcount=25] [multiselectable=false]:
      - columnheader "Name"
      - columnheader "Status"
      - columnheader "Date range"
      - columnheader "Actions"
      - row [selected=false]:
        - gridcell "Summer Sale"
        - gridcell "Active"
        - gridcell "Jun 1 – Aug 31"
        - gridcell:
          - button "Edit"
          - button "Delete" [disabled=false]
```

---

## Two-pass rendering for drawio

Produce the wireframe drawio in two separate passes:

**Pass 1 — Promote and render:**
Promote the structural `aria.yaml` node by node to detailed fidelity. Write the detailed `aria.yaml`. Drive `drawio-mockup.mjs` from the detailed tree to render the wireframe layout, regions, controls, and states. Save after pass 1.

**Pass 2 — Annotate with AC and domain terms:**
Add AC clauses verbatim to `mockup.md` under each screen heading. Add the yellow stories box and green domain terms box to the drawio alongside each screen. These are additive edits only — no wireframe layout or control changes. Save after pass 2.

This separation keeps the wireframe layout clean and independently reviewable before annotations are applied.
