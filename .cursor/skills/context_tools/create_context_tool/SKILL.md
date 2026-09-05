---
name: create_context_tool
description: "Provide guidance for scaffolding new context-tool domains."
---

# create_context_tool

Provide guidance for scaffolding new context-tool domains.

If you took an action from the context versus being given an explicit one, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.create_context_tool.create_context_tool:CreateContextTool
```
.\tools.ps1 run -
