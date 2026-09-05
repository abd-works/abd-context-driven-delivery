# User Experience Design — Diagram Workflow (shared)

UX diagrams use skill-local CLI scripts. Each skill ships `reference/diagram-workflow.md` with paths and commands; this file summarizes shared patterns.

---

## Information architecture (`abd-ux-information-architecture`)

**Output:** `docs/ux/initial-ia.drawio` — Page 1 Detailed IA, Page 2 Site Map.

**CLI:** `node scripts/drawio-ux.mjs` from the skill package.

```bash
node scripts/drawio-ux.mjs open docs/ux/initial-ia.drawio
node scripts/drawio-ux.mjs add-screen "<screen-name>" --layout sidebar --col <c> --row <r>
node scripts/drawio-ux.mjs add-list "<screen-name>" "<region>" --slot body --fields "..." --actions "..."
node scripts/drawio-ux.mjs connect "<source>" "<target>" --label "<trigger>"
node scripts/drawio-ux.mjs save
```

Build in two passes after `initial-ia.md` and all `aria.yaml` files: (1) structure from ARIA, (2) annotate stories and domain terms. See skill `reference/diagram-workflow.md`.

---

## Mockup (`abd-ux-mockup`)

**Output:** `docs/ux/mockup/screens/<screen-slug>.drawio` from state JSON.

```powershell
node "<skill-root>/scripts/drawio-mockup.mjs" `
  save `
  --state "docs/ux/mockup/screens/<screen-slug>-state.json" `
  --out   "docs/ux/mockup/screens/<screen-slug>.drawio"
```

Run once per screen after state JSON is written. State JSON is source of truth.
