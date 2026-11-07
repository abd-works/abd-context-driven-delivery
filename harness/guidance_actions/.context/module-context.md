# harness/guidance_actions
*GuidanceAction* is the shared start of every action an agent runs on practice guidance (Generate, Validate, Document, Sketch, Partition, ...): the action is subclassed once, and each call takes the guidance it works on, opens the session it works in, logs the call there, and runs the operation once for every guidance listed. An action works in one session: the session it was made for, the session a board command names, or the chat's current session.
*GuidanceArg* is what a caller passes as `guidance`: a slug they type (`stories`, `clean-engineering-model`), a list of slugs that runs the action once per slug, a `{toolset, fidelity}` reference, or any other string, which the action runs on once as text. Inside an operation the action reads that guidance back with `listed()` and runs work per item with `each(...)` and `run(...)`, so each listed practice is the one object its session holds.

- **Purpose:** Give every guidance action the same way to take guidance, open its session, and run once per listed guidance, so each action holds only its own words and steps.
- **Seam (terms):** GuidanceAction, GuidanceArg; `listed()`, `each(...)`, `run(...)`, `session`
- **Dependencies (one-way):** harness/agent_tools, harness/guidance, harness/hooks, harness/installation, space/session, space/work_state, tools/prompt_notify (imported through `sys.path` as `prompt_notify`). harness/agent_tools, harness/guidance, and space/session import this module back, so it sits in their dependency cycle (`.sessions/_backlog/break-module-dependency-cycles.md`).

## Constraint

Subclass *GuidanceAction* for a new action and mark its operations `@agent_tool` or `@agent_instructions`; take `guidance: GuidanceArg` as the parameter rather than parsing slugs yourself, so every action reads guidance the same way. Read the guidance a call is working on through `listed()`, not from a field set for one call, because the MCP server runs several calls on one action at once and each must answer for its own guidance. Pass `paths` to name files on an MCP call and let the action read them; leave the document body out of the call.
