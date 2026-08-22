# usage-order-behaviors

- **tool:** Bdd
- **error:** Nested enabling event `that has an action run against it` before standing `with a workspace`. Grill tick 8: subject `a context tool` → standing `with a workspace` → domain entry event — not event-before-standing.
- **rule:** usage-order-behaviors
- **how:** Restore tick 8 order: with a workspace before that has an action run against it; sync eval copy.
