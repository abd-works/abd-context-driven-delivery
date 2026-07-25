# conflicts/turns

Initiative, rounds, and turn economy (slots). Calls IAction to perform resolution; consults typed Condition for allotment (e.g. dazed) — no soft string reads.

## Modules fidelity

### Module `conflicts/turns`

- **Purpose:** Own turn order and action economy; orchestrate actions; read conditions for slots.
- **Seam (terms):** Initiative, Turn, Round
- **Dependencies (one-way):** `conflicts/actions`, `conflicts/conditions`
- **Build order:** see `sandbox/.context/sessions/discovery/module-build-order.md`
