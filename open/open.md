---
extends:
  surface: surface
  actions: [create]
  overrides: [satisfy]
open:
  actions: [open]
  mustBeOveridden: []
---
# Open for extension

Mark this surface's actions as open for extension.

**Extension frontmatter**

- `extends.surface` — surface this one extends (`surface`)
- `extends.actions` — actions to take from that surface; empty list means all actions marked open on it
- `extends.overrides` — actions this surface chooses to override from the extended surface — e.g. `[satisfy]` adds **Satisfy** here instead of inheriting it from `surface`

**Open frontmatter**

- `open.actions` — actions marked open for other surfaces to inherit; must be valid `##` actions on this surface; empty list means all local actions open
- `open.mustBeOveridden` — actions another surface must override when extending this one; must be valid `##` actions on this surface; empty when overriding is optional


## Satisfy

read in full → `surface` § Satisfy

Run `surface` § Satisfy, then verify:

- `open.actions` and `open.mustBeOveridden` are lists of valid `##` actions on this surface — no orphans
- every surface with `extends.surface` pointing here has `extends.actions` ⊆ `open.actions` (or all local actions when `open.actions` is empty) — no orphans; actions may be local `##` sections or inherited via this surface's `extends.actions`
- every such surface has `extends.overrides` ⊇ `open.mustBeOveridden` — no mismatches; override targets must be actions available on this surface (local or inherited)

```
python -m open satisfy
```

## Open

Mark this surface's action or selected actions as open for extension and optionally actions that must be overriden to be extended.

Sets `open.actions`. Empty list means all actions on this surface are open, including actions included via extension.
Sets `open.mustBeOveridden`. Empty list means no actions require override on the extending surface.

```
python -m open open [<action> …]
```

**example:** capability marks `identify` and `discover` open:

```
python -m capability open identify discover
```
