## Language

*Advantage* is a purchased trait that applies a combat, fortune, or skill effect.

### Advantage

- Purchases a ranked advantage and applies it.

### AttackTradeOff

- Moves an amount from one attack or defense stat to the other.

### Luck

- Tracks luck uses this session, re-rolls, and refresh.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# advantage
- **Purpose:** Purchase an advantage and apply combat, fortune, or skill advantage effects.
- **Seam (terms):** Advantage, AttackTradeOff, Luck
- **Dependencies (one-way):** checks, character-construction (PP, PL cap on attack bonus)
- **Primary use case:** `advantage.purchase()` then `advantage.apply()`; `luck.re_roll()` / `luck.refresh()`
- **Rationale:** Equipment, Minion, and Sidekick budgets live with Equipment. Luck uses live here.
- **Public API:** `Advantage.purchase`, `Advantage.apply`, `Luck.re_roll`, `Luck.refresh`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` advantage; stories Acquire Advantage)

## Constraint

Do not keep Equipment, Minion, or Sidekick budgets here. Combat consumes *AttackTradeOff*; this module does not import combat.
