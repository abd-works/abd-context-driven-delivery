# character

Owns a Mutants & Masterminds hero sheet for abilities, defenses, initiative, and power-point totals. Character creation traits from Secret Origins / Abilities live here; skills are a later peer module.

## Seam

The seam is `Character` with `abilities` / `defenses` (named + iterable collections), `point_totals`, and `initiative`. Callers read `character.abilities.strength` (and the other handbook names), mutate `Ability.rank` or `Defense.bought_ranks`, and read spent points from `PointTotals`. `Ability` and `Defense` are `Trait` subtypes so checks can use them directly.

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

Depends on `checks` for `Trait` and on `measurement` for `Rank`. Depended on by later skills, powers, conditions/combat, and by `checks.TeamCheck` helpers that own a trait. Does not own skills, powers, complications, or PL enforcement.
