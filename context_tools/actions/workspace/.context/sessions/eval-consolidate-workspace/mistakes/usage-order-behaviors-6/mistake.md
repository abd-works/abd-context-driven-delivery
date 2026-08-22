# usage-order-behaviors-6

- **entry_id:** ad49022f
- **artifact:** context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md
- **rule:** usage-order-behaviors
- **wrong:** Workspace pathOverrides behaviors were sketched as a detached prelude (with its workspace / that has been loaded) before any action run. Usage story starts when an action is run against a context tool; workspace opens for that run — load overrides and resolve path happen under that opening, not as a separate aggregate tour.
- **status:** open
