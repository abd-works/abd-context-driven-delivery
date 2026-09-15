---
name: car-inspect
description: "Collect the trip plan into one string, call wrap_story, emit the fenced block only."
disable-model-invocation: true
---

# car-inspect

Run this action for any provided context tools, or on the context in general.

Scripted trip actions over one or more Car context tools.

Collect the trip plan into one string, call wrap_story, emit the fenced block only.

Do not execute the plan — inspection output is the entire result of this invocation.

With a straight prompt passed, run this action on the context in general. If you took a context tool from the context and not a straight prompt, confirm the use of the context. AskQuestion constrained to the context tools: agent-bdd | bdd | car | cdd | clean-engineering | create-context-tool | ddd | harness | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Use MCP tool: `car_story.inspect_trip(tools: 'list', plan: 'str') -> 'str'`
