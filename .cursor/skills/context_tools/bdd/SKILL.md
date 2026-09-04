---
name: bdd
description: "Provide guidance for creating behavior skeletons and development tests."
---

# bdd

Provide guidance for creating behavior skeletons and development tests.

If you took an action from the context versus being given an explicit one, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities: modules | behavior | development.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.bdd.bdd:Bdd
```
.\tools.ps1 run -
