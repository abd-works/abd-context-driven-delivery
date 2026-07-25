# measurement

Converts Mutants & Masterminds ranks to real-world measures and applies handbook rank formulas (distance, time, throw). Lift is rank → mass via the table.

## Seam

The seam is `Rank` / `MeasurementsTable` / `Measure` — `to_measure`, distance/time/throw formulas, and table lookup. Callers convert ranks here so they never add ranks as if they were measures.

Constraint: do not add ranks by hand to get a combined measure; convert via `Rank` / `MeasurementsTable`. This module does not roll checks.

## Public API

### Rank / MeasurementsTable / Measure

Callers convert ranks to measures and run distance/time/throw formulas without owning the table. Lift is `toMeasure(mass)`.

## Public API (specification)

Seam contracts are `IRank`, `IMeasurementsTable`, `IMeasure`. Production classes implement those contracts in the same files. Private helpers (`#approxRangeForRank`, `#addRanks`, …) stay empty until code fidelity. Handbook table row data for reverse lookup is deferred to code.

Stories factory for `Rank` lives in `rank_example_factory.js` — not in `rank.js`. Builds `IRank` in **fake** / **isolated** / **production** modes.

## Dependencies

Foundation values module: no upstream dependencies. Depended on by `check` (for `Trait.rank`). Does not depend on character sheets, powers, or session/scenes.
