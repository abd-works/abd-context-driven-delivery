# ARIA Pipeline — IA (Structural) Fidelity

This skill produces WAI-ARIA at **structural fidelity** — the first stage of the ARIA design pipeline.

## Pipeline position

```
extractor (optional)          IA skill                 Mockup skill              Spec skill
aria.yaml (raw)          →   aria.yaml + .md      →   aria.yaml + .md      →   aria.yaml + .md
                             (structural)               (detailed)               (complete)
```

ARIA input is optional. If a prior `aria.yaml` exists (from the extractor or another source) the skill reads it and promotes it to structural fidelity. If no prior ARIA exists the skill constructs it from the story map and domain language. Either path produces the same output.

---

## Input resolution

Before generating, check:

1. **Extractor output** — does `docs/extracted-context/from-application/pages/<slug>/aria.yaml` exist for any in-scope screen?
   - If yes: read the raw tree. Preserve landmark roles and accessible names. Strip implementation detail below region level (button IDs, CSS classes, data attributes). Use the cleaned tree as the structural seed for that screen.
2. **No prior ARIA** — construct the structural tree from scratch using the story trace table, domain term trace table, and screen regions identified in steps 1–10 of the method.

---

## Structural fidelity — what belongs in this file

Capture **what regions exist and how the user navigates** — not the exact controls within regions.

**Include:**

| ARIA role | When to include |
|---|---|
| `banner`, `navigation`, `main`, `complementary`, `contentinfo` | Every screen — omit only if genuinely absent |
| `heading` with `[level=N]` | The primary heading in each region |
| `link` nodes under `navigation` | Every navigation destination, with `[current=true]` for the active one |
| `button` (top-level per region) | Primary region-level actions only — "Create Campaign", "Save", "Cancel" |
| `list` with one `listitem` | Where a list of records is the region's content — one row shows data shape |
| `dialog` (closed state) | Where a dialog is triggered — heading and primary action only |

**Do not include at this stage:**

- Form field detail (which input type, validation, hints)
- Toolbar composition (individual icon buttons, groupings)
- States other than `current`, `expanded`, `disabled` at the region level
- Relationship attributes (`controls`, `owns`, `describedby`, `labelledby`)
- Grid/table column structure

---

## Output format

One file per screen: `docs/ux/ia/<screen-slug>.aria.yaml`

Use Playwright WAI-ARIA snapshot syntax. Screen slug matches the screen name slug in `initial-ia.md`.

**Example — Campaigns list screen:**

```yaml
- document:
  - banner:
    - button "Toggle sidebar"
  - navigation "Main":
    - link "Dashboard"
    - link "Campaigns" [current=true]
    - link "Vouchers"
  - main:
    - heading "Campaigns" [level=1]
    - button "Create Campaign"
    - list "Campaigns":
      - listitem "Campaign name · Status · Date range"
  - contentinfo:
    - text "© 2025 Vouchera"
```

---

## Two-pass rendering for drawio

Produce `initial-ia.drawio` in two separate passes:

**Pass 1 — Structure from ARIA:**
Drive all `drawio-ux.mjs` calls from the `aria.yaml` trees. Map landmarks to layout regions, navigation links to site-map arrows, and primary actions to verb rows. Do not add story or domain term annotations yet. Save after pass 1.

**Pass 2 — Annotate with stories and domain terms:**
Add yellow stories boxes and green domain terms boxes alongside each screen in the drawio. Update `initial-ia.md` story-trace and domain-term-trace tables. These are additive edits only — no layout or region changes. Save after pass 2.

This separation keeps layout concerns out of the annotation pass and makes the structure independently reviewable.
