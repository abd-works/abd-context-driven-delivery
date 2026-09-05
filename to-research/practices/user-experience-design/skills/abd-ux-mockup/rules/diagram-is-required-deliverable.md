# Rule: Diagram is a required deliverable

**DO NOT** mark a mockup step complete when only the markdown spec exists.

The drawio wireframe is not optional and is not a follow-up step — it is the primary deliverable of the mockup skill. The markdown spec (`mockup.md`) is the companion document that explains the wireframe.

## Required outputs — all three must exist before the cell is marked done

1. `<screen-slug>-state.json` — the state source of truth (machine-readable, re-runnable)
2. `<screen-slug>.drawio` — the generated wireframe diagram
3. `<screen-slug>.md` — the structured spec (regions, stories, domain terms, affordance trace)

## DO

- Build the state JSON and run the CLI in the same step as writing the markdown spec.
- Treat the missing `.drawio` as a blocker — do not mark the cell done without it.
- Re-run the CLI whenever the state JSON changes; keep all three files in sync.

**CLI:**

```powershell
node "<skill-root>/scripts/drawio-mockup.mjs" save `
  --state "docs/ux/mockups/<screen-slug>-state.json" `
  --out   "docs/ux/mockups/<screen-slug>.drawio"
```

## DO NOT

- Do not produce the markdown spec and defer the diagram to a later step.
- Do not mark the UX mockup cell done in the CDD progress checklist unless the `.drawio` file exists on disk.
- Do not generate the diagram only when the user asks for it.

## Example (wrong)

Produced `vouchera-mockups.md` covering all screens, listed stories and domain terms, marked Exploration: UX complete. No `vouchera-state.json` or `vouchera-mockups.drawio` existed. User had to ask for the diagrams explicitly.

## Example (correct)

In one step: wrote `vouchera-mockups.md`, built `vouchera-state.json`, ran `drawio-mockup.mjs save` → `vouchera-mockups.drawio` (14 screens, 14 connections). Checked all three files existed before marking Exploration: UX done.
