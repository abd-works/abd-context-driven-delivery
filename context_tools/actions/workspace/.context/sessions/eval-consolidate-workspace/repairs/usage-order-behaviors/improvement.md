# usage-order-behaviors

- **tool:** Bdd
- **error:** Nested enabling event `that has an action run against it` before standing `with a workspace`. Grill tick 8: subject `a context tool` → standing `with a workspace` → domain entry event — not event-before-standing.
- **rule:** usage-order-behaviors
- **how:** OO §2 three levels: BaseContextTool composes Workspace (with a workspace) before action-run envelope; §4 openWorkSession + Turn.open then agent work. Design cites workspace-eval-oo-sketch.md only.
