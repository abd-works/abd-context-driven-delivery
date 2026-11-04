## Language

*Skill* is ranks on a linked ability, used to make a skill check.

### Skill

- Assigns ranks, makes a check through *Trait.perform_check*, and resolves untrained use.

Build order: `checks` → `character-construction` → `ability` → `skill` → `advantage` → `power` → `equipment` → `combat`

---

# skill
- **Purpose:** Assign skill ranks and make skill checks, including trained-only and untrained.
- **Seam (terms):** Skill
- **Dependencies (one-way):** checks (`Trait.perform_check`), ability (linked ability rank), character-construction (PL+10 skill modifier cap via `Hero.enforce_limit_pair`)
- **Primary use case:** `skill.assign_ranks(purchased_rank)` then `skill.make_check(dc)`
- **Rationale:** One d20 engine. A skill check is a trait check.
- **Public API:** `Skill.assign_ranks`, `Skill.make_check`, `Skill.resolve_untrained`
- **Sources / context:** `harness/transformers/fixtures/mm3e/mm3e-sketch.md` (`ce:` skill; stories Configure Skill Ranks / Resolve Skill Checks)

## Constraint

A skill check is `Trait.perform_check`. Do not fork a second d20 engine.
