---
name: bdd
description: "Provide guidance for creating behavior skeletons and development tests."
---

# bdd

Provide guidance for creating behavior skeletons and development tests.

If you took an action from the context versus being given an explicit one, confirm the use of the context. AskQuestion constrained to the actions in context_tools/actions: createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | validate.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities: modules | behavior | development.
Then run:
Pipe the fence to stdin. Do not write a request file. Do not remanifest — this skill is the catalog.
```yaml
toolset: context_tools.bdd.bdd:Bdd
```
python -m tools run -
