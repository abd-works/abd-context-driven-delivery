## Language

*Ability* is one of the eight ability ranks. Changing it cascades linked skills, defenses, and attack modifiers.

### Ability

- Sets purchased rank, splits natural versus enhanced, applies absent restrictions or debilitated effects.
- **Invariant:** Voluntary rank never below -5. Below -5 is debilitated from an effect. Absent is not rank -5.

### Defense

- Derives a defense rank from a source ability and tracks ranks bought above that base.
- **Invariant:** Toughness cannot be bought above Stamina base.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# ability
- **Purpose:** Set eight ability ranks, cascade derived traits, and distinguish absent from debilitated.
- **Seam (terms):** Ability, Defense
- **Dependencies (one-way):** checks (`Trait`), character-construction (`Hero.spend_on`, PL ceiling)
- **Primary use case:** `ability.set_rank(purchased_rank)` then `ability.cascade_dependents()`; `defense.derive_base()`
- **Rationale:** Ability is a *Trait*. Check resolution owns the check formula.
- **Public API:** `Ability.set_rank`, `Ability.cascade_dependents`, `Ability.apply_absent_restrictions`, `Ability.apply_debilitated`, `Defense.derive_base`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` ability; stories Assign Abilities)

## Constraint

*Ability* is a *Trait*. Do not fork a second check formula here. Voluntary rank never goes below -5; absent is not rank -5.
