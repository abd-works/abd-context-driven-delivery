# usage-order-behaviors-2

- **entry_id:** 23dd937b
- **artifact:** context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md
- **rule:** usage-order-behaviors
- **wrong:** Sketch opened with "a context tool host" binding a workspace at a folder before any action runs. Target model — generate/validate envelope — starts when a context tool is invoked; session prelude is openWorkSession + turn.open inside that action, not a freestanding workspace-create step.
- **status:** fixed
