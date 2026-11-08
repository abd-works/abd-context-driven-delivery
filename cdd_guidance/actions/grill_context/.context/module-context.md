# cdd_guidance/actions/grill_context
*Grill* is an interview about a plan that is grounded in the project's context files: every question names the files it was drawn from and frames the decision before offering options, and each resolved answer is written straight to the session root's `.context/grill-answers.md`, so the answers outlast the chat. `grill-context.grill(guidance)` (slash `/grill`) interviews the plan and then generates each listed Guidance; the `grill_with_context` instructions are the interview alone, and the grill ends with the instructions of a *Generate* it starts on the same guidance (`instructions(self._generate().generate)`). `actions/sketch` names `grill_with_context` and its own generate around its sketch cadence; `actions/iterate` names the whole `grill` for each cycle. The answers file is `Session.context_folder() / "grill-answers.md"`.

The MCP tools `grill-context.explore_context_files(folder)`, `grill-context.read_context_file(path)`, and `grill-context.write_grill_answer(heading, body)` find context files under the session's root, confirm a file before it is read, and record an answer.

- **Purpose:** Turn a vague plan into decisions grounded in what the codebase already says, one framed question at a time, with every answer kept.
- **Seam (terms):** GrillContext, `grill-context.grill`, `grill_with_context`, `grill-context.explore_context_files`, `grill-context.read_context_file`, `grill-context.write_grill_answer`
- **Dependencies (one-way):** `cdd_guidance/actions` (*Generate*), `harness/guidance_actions` (*GuidanceAction*, *GuidanceArg*), `harness/agent_tools`, `harness/installation`, `harness/mcp`

## Constraint

Read the cited context files before asking: a question must name the files read and use their terms, because a question from a skim or from memory asks the person to decide without the facts. Ask one framed question at a time and write each answer as soon as it is resolved; do not batch answers at the end.
