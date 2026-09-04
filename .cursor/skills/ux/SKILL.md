---
name: ux
description: "Provide guidance for creating IA, mockups, and front-end code."
---

# ux

Provide guidance for creating IA, mockups, and front-end code.

With a straight prompt passed, take the action from the prompt. If you took an action from the context versus being given a straight prompt, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities: ia | mockup | front_end_code.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.ux.ux:Ux
```
.\tools.ps1 run -
