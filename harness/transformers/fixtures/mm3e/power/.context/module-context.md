## Language

*Power* is selected effects, descriptors, and an optional array, with cost from extras and flaws.

### Power

- Holds descriptors, an array, and cost: (base + extras − flaws) × rank + flat.

### Effect

- A power effect whose rank is a trait rank, resolved through checks.
- **Invariant:** After flaws, at least 1 PP per rank (or fractional ranks) and at least 1 PP total.

### Extra

- A per-rank extra that raises an effect's cost.

### Flaw

- A per-rank or removable flaw that lowers an effect's cost.

### Array

- Holds a base effect and alternates.
- **Invariant:** Non-dynamic array effects are mutually exclusive.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# power
- **Purpose:** Select an effect, cost it, and resolve it through checks.
- **Seam (terms):** Power, Effect, Extra, Flaw, Array
- **Dependencies (one-way):** checks (resistance, opposed, conditions), ability (Enhanced Trait portion), character-construction (PP, PL on built effects)
- **Primary use case:** `effect.resolve()`; `array.switch_active()` / `array.reallocate()`
- **Rationale:** Effect rank is a *Trait* rank. Resistance DC is 10 + effect rank in checks.
- **Public API:** `Effect.resolve`, `Array.switch_active`, `Array.reallocate`, `Power.cost`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` power; stories Configure Attack/Defense/Mobility/Sensory/Control/General Effect)

## Constraint

Do not invent a second check engine. Resistance uses checks. Descriptors stay a property on *Power*, not a parallel type.
