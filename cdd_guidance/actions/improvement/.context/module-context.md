# cdd_guidance/actions/improvement
*Improvement* repairs a practice's guidance when it produced the wrong artifact: `improvement.repair(guidance, asset, violation)` (slash `/repair`) opens a repair on each listed Guidance for the file that went wrong and the rule it broke, has the cause diagnosed with `actions/diagnose`, and asks for the change to the guidance before any test; `improvement.verify_fix(guidance, theme)` re-runs the regression check for one group of repairs after the fix. The repair loop itself is written in `repair.md` beside this module.

- **Purpose:** Fix the guidance that caused a bad artifact, not just the artifact, and check the same mistake does not come back.
- **Seam (terms):** Improvement, `improvement.repair`, `improvement.verify_fix`
- **Dependencies (one-way):** `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*), `harness/markdown` (`@markdown`), `harness/agent_tools`, `harness/installation`, `harness/mcp`

## Constraint

Pass the file under repair and the violation (a rule name or a report path) by path; never paste the artifact's body. State the proposed change to the guidance before writing a failing test at that seam, and do not list one-off fixes to the artifact as the repair. `repair` leaves the session turn open for the fix; it does not finish it.
