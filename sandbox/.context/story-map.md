---
fidelity: [discovery]
artifact: [story-map]
format: md
---

# Story Map — Play Core Mechanics

**Sources / context:** `sandbox/character/.context/module-context.md`, `sandbox/checks/.context/module-context.md`, `sandbox/.context/stories-sketch.md`, `sandbox/.context/grill-answers.md`

---

(E) Play Core Mechanics
    * approx 12-16 total stories
    (E) Manage Character Sheet
        (S) Player --> Create Character
        (S) Player --> Update Ability Rank
        (S) Player --> Refresh Point Totals
        (S) Player --> Update Defense Ranks
        * approx 2-3 more stories (initiative, absent, debilitated)
    (E) Resolve Checks
        (S) Player --> Resolve Ability Check
        (S) Player --> Resolve Opposed Check
        (S) Player --> Resolve Routine Check
        (S) Player --> Assist Team Check
        * approx 2-3 more stories (comparison, routine opposition, fail/crit paths)

---

## Scope boundary

**In scope:** Character sheet create / ability and defense rank updates / point totals; resolve Check / Opposed / routine; team assist.
**Out of scope:** Attack checks; Powers; Skills; active defenses (deferred to conditions/combat); UI display of abilities.

---

## Thin slices

### Increment 1: Hero resolves an ability check

**Outcome:** Player can create a Character, set an Ability rank, and resolve a Check that reports die, total, degree, and success.

**Stories:**
- Create Character
- Update Ability Rank
- Resolve Ability Check
