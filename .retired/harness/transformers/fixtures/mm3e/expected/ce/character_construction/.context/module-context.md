## Language

*Hero* is the power-point budget and power-level caps for one hero in a series.

### Hero

- Spends power points on traits, validates spent versus starting budget, and rejects allocations that break a limit pair.

### PowerLevel

- Caps every player hero in the series and derives starting power points.

### Complication

- Records a narrative hook the hero must live with, including type and trigger.

### TradeOff

- Moves ranks from one side of a limit pair to the other without changing the pair sum.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# character-construction
- **Purpose:** Set series power level, spend power points, enforce limit pairs, hold complications.
- **Seam (terms):** Hero, PowerLevel, Complication, TradeOff
- **Dependencies (one-way):** checks (`Trait` as the thing `Hero.spend_on` pays for)
- **Primary use case:** `hero.spend_on(trait)`, `hero.validate_balance()`, `hero.enforce_limit_pair()`
- **Rationale:** One budget and one set of PL caps. Ability, Skill, Advantage, and Power do not invent a second budget.
- **Public API:** `Hero.spend_on`, `Hero.validate_balance`, `Hero.enforce_limit_pair`, `PowerLevel.starting_power_points`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` character-construction; stories Construct Hero)

## Constraint

This module owns PP currency and PL caps. Callers pass a *Trait*; they do not keep a second spend ledger on Ability, Skill, Advantage, or Power.
