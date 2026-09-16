---
name: travel-to
description: "Tell an interesting story about how the car gets to {destination}."
disable-model-invocation: true
---

# travel-to

Run this action for any provided context tools, or on the context in general.

Scripted trip actions over one or more Car context tools.

Tell an interesting story about how the car gets to {destination}.

Conditions: {conditions}. Start the engine, then decide what to do according to personality.

With a straight prompt passed, run this action on the context in general. If you took a context tool from the context and not a straight prompt, confirm the use of the context. AskQuestion constrained to the context tools: agent-bdd | bdd | car | cdd | clean-engineering | create-context-tool | ddd | harness | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Use MCP tool: `car_story.travelTo(tools: 'list', destination: 'str', conditions: 'str') -> 'str'`
