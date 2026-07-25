# character

Owns a Mutants & Masterminds hero sheet for abilities, defenses, initiative, and power-point totals. Owns **ISource** so advantages (and later others) can be typed sources for maneuvers. Character creation traits from Secret Origins / Abilities live here; skills, advantages, powers, and gear depend on this module.

## Modules fidelity

### Module `character`

- **Purpose:** Hero sheet; abilities, defenses, points; owns ISource.
- **Seam (terms):** Character, Ability, Defense, PointTotals, Point, ISource
- **Dependencies (one-way):** `checks`
- **Build order:** see `sandbox/.context/sessions/discovery/module-build-order.md`

## Seam

The seam is `Character` with `abilities` / `defenses` (named + iterable collections), `point_totals`, `initiative`, and **`ISource`**. Callers read `character.abilities.strength` (and the other handbook names), mutate `Ability.rank` or `Defense.bought_ranks`, and read spent points from `PointTotals`. `Ability` and `Defense` are `Trait` subtypes so checks can use them directly. Advantages (and later others) implement `ISource` for typed maneuver sources.

Constraint: do not buy/reduce through dedicated spend ops — mutate ranks (and defense bought ranks); `PointTotals` refreshes from containers. Do not enforce power level here. Active defense (vulnerable/defenseless) is not applied on `Defense.rank` — conditions/combat own that. Enhanced ability ranks wait for Powers. Toughness cannot take `bought_ranks` via power points.

## Public API

### Character

Callers hold the sheet: abilities, defenses, point totals, and initiative (from Agility). Team checks and ability checks use abilities/defenses as traits.

## Public API (specification)

Seam contracts are `ICharacter`, `IAbility` / `IAbilities`, `IDefense` / `IDefenses`, `IPoint` / `IPointTotals`. Production classes implement those contracts in the same files (`Ability` / `Defense` extend `Trait`).

Stories factories live in sibling files (`character_example_factory.js`, `ability_example_factory.js`) — not in the production family files. Factories build `ICharacter` / `IAbility` in **fake** / **isolated** / **production** modes (`examples[{example_key}]` bundles).

### Abilities / Defenses

Named + iterable collections of the fixed handbook sets. Containers contribute a `Point` into `PointTotals`.

### Ability

`Trait` with `rank`, `absent`, and `debilitated` (`debilitated == (rank < -5)`). Cost: 2 PP per +1 rank.

### Defense

`Trait` whose `rank` is `linked_ability.rank + bought_ranks`. Cost: 1 PP per bought rank; Toughness forbids PP bought ranks.

### PointTotals / Point

Collection of `Point(source, amount)` with `total` equal to the sum of amounts. Sources include abilities, defenses, and later skills/powers.

## Dependencies

**Formal (modules):** `checks` (`Trait`; Rank/measurement owned there). Owns **ISource**. Depended on by skills, advantages, powers, conflicts/actions, and gear/* (sheet ownership). Does not own skills, powers, complications, or PL enforcement.
