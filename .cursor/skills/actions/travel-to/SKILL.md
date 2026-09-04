---
name: travel-to
description: "Tell an interesting story about how the car gets to {destination}."
disable-model-invocation: true
---

# travel-to

Run this action for any provided context tools, or on the context in general.

Scripted trip actions over one or more Car context tools.

Tell an interesting story about how the car gets to {destination}.

If you took guidance from the context and not a tool, confirm the use of the context. AskQuestion constrained to the context tools: agent_bdd | bdd | car | cdd | clean_engineering | create_context_tool | ddd | stories | ux | use existing context only.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: car_story.car_story:CarStory
action: travelTo
```
.\tools.ps1 run -
