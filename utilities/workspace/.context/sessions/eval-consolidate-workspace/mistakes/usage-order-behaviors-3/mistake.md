# usage-order-behaviors-3

- **entry_id:** e4736325
- **artifact:** context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md
- **rule:** usage-order-behaviors
- **wrong:** Sketch listed turn.open(host) and turn observable before path resolution and openWorkSession observables. Target turn envelope is openWorkSession then turn.open after session prelude (path resolve, work session, WorkSession.open git).
- **status:** fixed
