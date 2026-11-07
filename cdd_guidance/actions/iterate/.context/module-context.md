# cdd_guidance/actions/iterate
*Iterate* builds the formal artifacts in short cycles: a few grill questions, then only the slice of the deliverable those answers unlocked, validated, with one fix pass and the person's feedback before the next questions. `iterate.iterate(guidance, tools)` (slash `/iterate`) runs the cycles for each listed Guidance; `iterate.mark_iterate_tick` records that a cycle's generate-validate-fix step is due.

- **Purpose:** Deliver a large artifact in small agreed slices instead of one unreviewed dump.
- **Seam (terms):** Iterate, `iterate.iterate`, `iterate.mark_iterate_tick`
- **Dependencies (one-way):** `cdd_guidance/actions/grill_context` (*GrillContext*), `cdd_guidance/actions` (*Generate*), `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*), `harness/agent_tools`, `harness/installation`, `harness/mcp`

## Constraint

Generate only after two or three answers name one concrete slice, and stop after that slice's validation and fix pass for feedback. Never chain cycles or write output ahead of the questions. Iterate works on the formal artifacts; use `actions/sketch` for a rough draft.
