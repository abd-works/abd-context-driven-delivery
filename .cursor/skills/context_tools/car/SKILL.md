---
name: car
description: "Provide guidance for in-character road stories at the current fidelity."
---

# car

Provide guidance for in-character road stories at the current fidelity.

If you took an action from the context versus being given an explicit one, confirm the use of the context. AskQuestion constrained to these actions: car-inspect | createRule | document | generate | grill | iterate | partition | render | repair | satisfy | scan | sketch | travel-to | validate.
If the fidelity does not belong to the in-scope tool or has not been provided, guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities: trip_outline | road_story | full_journey.
Then run:
Pipe the fence to stdin from the repo root. Do not write a request file. Do not remanifest — this skill is the catalog. Follow response.instructions only.
```yaml
toolset: context_tools.car.car:Car
```
.\tools.ps1 run -
