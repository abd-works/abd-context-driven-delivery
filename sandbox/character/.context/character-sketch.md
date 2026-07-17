# module character

# Character + Abilities — one module (Skills is a later peer module).
# Locked: Ability : Trait; Defense : Trait; named+iterable collections;
#         Ability absent + debilitated; enhanced → Powers;
#         Defense.rank = linkedAbility.rank + boughtRanks (Toughness: no PP buy);
#         PointTotals aggregates Point(source, amount); total == sum(amount);
#         mutate ranks / boughtRanks — PointTotals refreshes from containers (no buy/reduce ops).
# Deferred: active defenses → conditions/combat; PL checks → later slice.

Character
  abilities                       # Abilities — iterable + property by handbook name
  defenses                        # Defenses — iterable + property by handbook name
  pointTotals                     # PointTotals
  initiative                      # from Agility (+ advantages/powers later)
  # // e.g. character.abilities.strength / character.defenses.dodge
  # // TeamCheck helpers: Character owns traits
  # // combat consumes defense ranks — does not own them
  # // mutate Ability.rank / Defense.boughtRanks; pointTotals refreshes from containers

  ----
 Abilities
  # fixed handbook set as named properties; also iterable
  # // contributes Point(source=abilities, amount=…)

  ----
 Defenses
  # fixed handbook set as named properties; also iterable
  # // contributes Point(source=defenses, amount=…)

  ----
 PointTotals
  points                          # collection of Point
  total
  // invariant: total == sum(points.amount)

  ----
 Point
  source                          # abilities | defenses | skills | powers | …
  amount

  ----
 Ability : Trait
  rank                            # inherited — Rank (measurement)
  absent                          # no ability at all (construct/ghost rules)
  debilitated
  // invariant: debilitated == (rank < -5)
  # // enhanced portion deferred to Powers (nullify / power stunts)
  # // cost: 2 PP per +1 rank (handbook)

  ----
 Defense : Trait
  linkedAbility                   # Ability — base for rank
  boughtRanks                     # PP-bought delta (not for Toughness)
  rank                            # computed: linkedAbility.rank + boughtRanks
  # TODO: active defenses (Dodge/Parry vulnerable/defenseless)
  # // Toughness: boughtRanks via PP forbidden — advantages/powers only
  # // cost: 1 PP per +1 bought rank (handbook)
