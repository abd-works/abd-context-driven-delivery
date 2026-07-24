# conflicts/actions

Resolution of actions and maneuvers (Aid, Grab, etc.). Turn economy is not owned here — turns call IAction. Maneuver/modifier sources are typed ISource from character (no advantage-tag strings).

## Modules fidelity

### Module `conflicts/actions`

- **Purpose:** Resolve what happens when a slot is spent; expose IAction for turns.
- **Seam (terms):** Action, Maneuver, IAction (source : ISource)
- **Dependencies (one-way):** `character`
- **Build order:** see `sandbox/.context/sessions/discovery/module-build-order.md`
