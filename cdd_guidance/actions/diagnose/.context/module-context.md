# cdd_guidance/actions/diagnose
*Diagnose* is a disciplined hunt for a hard bug or performance regression, run by a background sub-agent so the chat can keep working: build a fast pass/fail feedback loop, reproduce, minimise, form hypotheses, instrument, fix, and add a regression test. Calling `diagnose.diagnose(guidance)` (slash `/diagnose`) with no guidance runs the six phases alone; passing practice guidance, such as `bdd` or `clean-engineering`, applies that practice's rules while fixing and while writing the regression test.

- **Purpose:** Find the root cause of a stubborn failure and prove the fix with a test, without blocking the conversation that hit it.
- **Seam (terms):** Diagnose, `diagnose.diagnose`
- **Dependencies (one-way):** `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*), `harness/agent_tools` (`@subAgent`), `harness/installation`, `harness/mcp`

## Constraint

Build the feedback loop before guessing at a cause; skip a phase only with a stated reason. Pass guidance only when the fix and its test should follow that practice. The work runs in a sub-agent, so do not wait on its result in the same turn.
