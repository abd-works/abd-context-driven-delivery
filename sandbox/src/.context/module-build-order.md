# Module build order — Heroes Handbook

**Fidelity:** modules  
**Session:** `sandbox/.context/sessions/discovery`  
**Rule:** one-way deps only; order by **dependency depth** (not folder). Cycles = hard fail.  
**Standing:** no opaque string/tag/id links.  
**Nesting:** parent owns shared base terms/classes (e.g. `powers` owns `Effect`); children nest under the parent path and depend on the parent — never sibling → sibling.  
**Gear:** `equipment` → `vehicles` → `headquarters` (HQ last under gear).  
**Powers children:** listed one module per step (peers may still build in any order within their dep class).  
**Stories thin-slice align:** turns after attack; sensory after attack/affliction family (before gear).

## Order

| # | Module | Depends on (one-way) | Notes |
|---|--------|----------------------|-------|
| 1 | `checks` | *(none)* | Trait, measurement, check-time Modifier |
| 2 | `character` | `checks` | Owns **ISource**; Ability/Defense : Trait |
| 3 | `conflicts/conditions` | `checks` | Contained under `conflicts` |
| 4 | `skills` | `character`, `checks` | Typed Ability via character |
| 5 | `advantages` | `character` | Implements ISource |
| 6 | `conflicts/actions` | `character` | Maneuver/modifier source : ISource |
| 7 | `powers` | `character`, `checks` | Owns **Effect** (shared base — not a submodule) |
| 8 | `powers/attack` | `powers`, `checks` | Damage / Affliction / Nullify / Weaken |
| 9 | `conflicts/turns` | `conflicts/actions`, `conflicts/conditions` | After attack; economy via IAction; allotment via Condition |
| 10 | `powers/control` | `powers`, `checks` | |
| 11 | `powers/defense` | `powers` | |
| 12 | `powers/movement` | `powers` | |
| 13 | `powers/general` | `powers` | |
| 14 | `powers/extras` | `powers` | |
| 15 | `powers/flaws` | `powers` | |
| 16 | `powers/sensory` | `powers` | After attack/affliction family |
| 17 | `gear/equipment` | `character`, `powers` | Typed Effect; no effect ids |
| 18 | `gear/vehicles` | `character`, `powers` | |
| 19 | `gear/headquarters` | `character` | Last under gear |

## Layers (summary)

```
0  checks
1  character | conflicts/conditions
2  skills | advantages | conflicts/actions | powers
3  powers/attack                         # inside powers
4  conflicts/turns                       # after attack; needs actions + conditions
5  powers/{control,defense,movement,general,extras,flaws}
6  powers/sensory
7  gear/{equipment,vehicles,headquarters}
```

Gear sequence: **equipment → vehicles → headquarters**.

## Index label reconcile (not a re-cut)

| Index row | Formal module |
|-----------|---------------|
| `measurement` | folded into `checks` |
| `characters` / `abilities` | `character` |
| `advantages` unlock tags | typed ISource on `character` |
| `conflicts/actions` advantage tags | typed ISource (not strings) |
| `powers/effect` (partition folder) | **`powers`** owns Effect — not a submodule |
| `gear/equipment` effect ids | `equipment → powers` |
| `skills` ability key | typed Ability via `character` |

## Graph (edges only)

```
checks
character -> checks
skills -> character, checks
advantages -> character
powers -> character, checks
powers/attack -> powers, checks
powers/control -> powers, checks
powers/defense -> powers
powers/movement -> powers
powers/sensory -> powers
powers/general -> powers
powers/extras -> powers
powers/flaws -> powers
conflicts/conditions -> checks
conflicts/actions -> character
conflicts/turns -> conflicts/actions, conflicts/conditions
gear/equipment -> character, powers
gear/vehicles -> character, powers
gear/headquarters -> character
```
