---
name: grill
description: "Grill then generate - pure grill loop, then the host generate body."
disable-model-invocation: true
---

# grill

Run this action for any provided context tools, or on the context in general.

Interview a plan relentlessly against the codebase context until reaching shared understanding.

Grill then generate - pure grill loop, then the host generate body.

With a straight prompt passed, run this action on the context in general. If you took a context tool from the context and not a straight prompt, confirm the use of the context. AskQuestion constrained to the context tools: agent_bdd | bdd | car | cdd | clean_engineering | create_context_tool | ddd | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Pipe the block to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```
toolset: grill_context.grill_context:GrillContext
action: grill
```
.\tools.ps1 run -
