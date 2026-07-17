---
fidelity: [discovery]
artifact: [thin-slice]
format: md
---

# Thin slicing — Play Core Mechanics incremental backlog

## Product / context

**Product:** Mutants & Masterminds sandbox — Character sheet + Check resolution.

**Slicing intent:** First vertical slice proves the Character→Trait→Check seam end-to-end before opposed checks, team assist, or power-point accounting.

**Spine vs optional:** Spine is **create Character → update Ability rank → resolve Ability Check**. PointTotals, defenses, opposed/routine, and team assist are named on the map but not required for Increment 1.

## Increments

### Increment 1: Hero resolves an ability check

**Outcome:** A Player can create a Character with handbook Abilities at rank 0, update an Ability rank, and resolve a Check on that Ability — seeing die roll, total, degree, and succeeded.

**Slicing notes:** Stubbed dice for determinism. No PointTotals assertion on rank update. No UI. Object-level Check BDD in `checks/check_spec.py` remains; this slice is acceptance above the Character seam.

**Stories in this increment** *(order reflects flow within the slice):*

- *Create Character*
- *Update Ability Rank*
- *Resolve Ability Check*
