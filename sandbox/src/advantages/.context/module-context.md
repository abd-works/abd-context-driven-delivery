# advantages

Owns Mutants & Masterminds advantages purchased on the hero sheet. Advantages implement character’s ISource so maneuvers can enhance or grant via typed source links (no unlock-tag strings).

## Modules fidelity

### Module `advantages`

- **Purpose:** Take advantages; provide ISource for maneuver modifiers and granted maneuvers.
- **Seam (terms):** Advantage (implements ISource)
- **Dependencies (one-way):** `character`
- **Build order:** see `sandbox/.context/sessions/discovery/module-build-order.md`
