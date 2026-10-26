## Language

*ActionRound* is initiative order and the action slots of a turn, plus attack, damage, hero point, and extra effort.

### ActionRound

- Orders turns and rolls initiative.

### Turn

- Holds the standard, move, free, and reaction slots of one turn.

### Attack

- Resolves an attack check against a parry or dodge class and confirms a critical.

### Damage

- Applies damage degrees from a graded Toughness resistance.

### HeroPoint

- Spends a hero point.

### ExtraEffort

- Declares an extra-effort benefit and applies fatigue.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# combat
- **Purpose:** Initiative, action economy, attack versus defense class, damage degrees, hero point, extra effort.
- **Seam (terms):** ActionRound, Turn, Attack, Damage, HeroPoint, ExtraEffort
- **Dependencies (one-way):** checks (Check, GradedCheckResult, Condition), ability (defenses, initiative from Agility), skill (Close Combat, Ranged Combat, Deception feint), advantage (trade-offs, Improved Critical), power (area/perception bypass attack check)
- **Primary use case:** `action_round.roll_initiative()`; `attack.resolve()` then `attack.confirm_critical()`; `damage.apply_degree()`; `hero_point.spend()`; `extra_effort.declare_benefit()`
- **Rationale:** An attack check is a *Check* against Parry or Dodge class. Damage is a graded Toughness resistance.
- **Public API:** `ActionRound.roll_initiative`, `Attack.resolve`, `Attack.confirm_critical`, `Damage.apply_degree`, `HeroPoint.spend`, `ExtraEffort.declare_benefit`, `ExtraEffort.apply_fatigue`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` combat; stories Manage Turn Order / Execute Attacks)

## Constraint

An attack check is a *Check* against Parry or Dodge class. Damage is a graded Toughness resistance. Do not fork a second d20 engine.
