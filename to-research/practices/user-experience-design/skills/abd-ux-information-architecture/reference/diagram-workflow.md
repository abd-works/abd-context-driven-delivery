# Diagram workflow — abd-ux-information-architecture

Shared commands: [`../../../reference/diagram-workflow.md`](../../../reference/diagram-workflow.md)

**This skill:** produces `docs/ux/initial-ia.drawio` — two pages: Page 1 (Detailed IA, full screen layouts) and Page 2 (Site Map, one box per screen with labeled arrows). Must exist on disk before the cell is marked done.

Build in two passes after `initial-ia.md` and all `aria.yaml` files are written:

**Pass 1 — Structure from ARIA (Mode A — CLI from skill's `scripts/`):**

```bash
node scripts/drawio-ux.mjs open docs/ux/initial-ia.drawio
node scripts/drawio-ux.mjs add-screen "<screen-name>" --layout sidebar --col <c> --row <r>
node scripts/drawio-ux.mjs add-list "<screen-name>" "<region>" --slot body --fields "..." --actions "..."
node scripts/drawio-ux.mjs connect "<source>" "<target>" --label "<trigger>"
node scripts/drawio-ux.mjs save
```

Repeat `add-screen`, `add-list`, and `connect` calls for every screen. `save` always writes both pages.

**Pass 2 — Annotate (no layout changes):** Add yellow stories boxes and green domain terms boxes alongside each screen in the drawio. Save.

**Mode B (no CLI available):** Pass the `aria.yaml` trees and the prompt template from `reference/concepts.md` to an external AI to generate the drawio XML directly.
