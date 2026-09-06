# Diagram workflow — abd-ux-mockup

Shared commands: [`../../../reference/diagram-workflow.md`](../../../reference/diagram-workflow.md)

**This skill:** produces `docs/ux/mockups/<screen-slug>.drawio` from the state JSON. Must exist on disk before the cell is marked done.

```powershell
node "<skill-root>/scripts/drawio-mockup.mjs" `
  save `
  --state "docs/ux/mockups/<screen-slug>-state.json" `
  --out   "docs/ux/mockups/<screen-slug>.drawio"
```

Run once per screen in scope after `<screen-slug>-state.json` is written. To regenerate, re-run the same command — the state JSON is the source of truth.
