---
extends:
  surface: surface
  actions: []
  overrides: [generate, satisfy, deploy]
open:
  actions: [open, override]
  mustBeOveridden: []
---
# Surface extension
Inherit actions from another surface at deploy time.

**Extension frontmatter**

- `extends.surface` — base surface
- `extends.actions` — actions to extend from base; empty list means extend all actions marked open on base
- `extends.overrides` — actions this capability chooses to override from the base
- `open.actions` — actions marked open for subs to inherit; empty list means all local actions open
- `open.mustBeOveridden` — actions subs must override when extending this surface; empty when overriding is optional

This capability extends `surface` (`extends.actions` empty — all open), chooses to override **Generate**, **Satisfy**, and **Deploy** (`surface` has no `open.mustBeOveridden`), and marks **Open** open for extension.

## Open

Mark this surface's actions as open for extension.

Sets `open.actions`. Empty list means all local actions are open.

**example:** capability marks `identify` and `discover` open:

```
python -m capability open identify discover
```

## Extend

Scaffold another surface from **this** surface. Name `{sub}` — the surface being created. This surface is the base; `{sub}` gets `extends.surface` pointing to this surface and must subclass `ExtendCli` in its API surface.

Sets `extends: {surface: <this-surface>, actions: [action, …]}` on `{sub}` frontmatter. Empty `extends.actions` means extend all actions marked open; action list required only when this surface or actions not open.

**example:** capability scaffolds `rules`:

```
python -m capability extend rules [<action> …]
```

## Override

Override actions from **this** surface onto `{sub}`. Name `{sub}` and the actions to override.

Pulls matching `##` sections from this surface into `{sub}`'s agentic surface — adapts names for `{sub}` and keeps this surface's action order. Adds those actions to `extends.overrides`.

**example:** capability overrides `validate` and `create` onto `rules`:

```
python -m capability override rules validate create
```

At deploy, `{sub}` inherits infrastructure actions (`deploy`, `clean`, `open`, `extend`, `generate`, `satisfy`) plus actions in this surface's `open.actions` — or all local actions when `open.actions` is empty.

## Deploy

Same as `surface §deploy`, plus: actions this surface does not override deploy as `read @{base} § {action}`.

## Clean

Remove deployed artefacts. Inherited from `surface`.
