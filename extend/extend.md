---
extends:
  surface: open
  actions: []
  overrides: [create, satisfy, deploy]
---
# Surface extension

Extend another surface from this one at deploy time.

**Extend frontmatter**

- `extends.surface` — surface this one extends
- `extends.actions` — actions to take from that surface; empty list means all actions marked open on it
- `extends.overrides` — actions this surface chooses to override from the extended surface

## Extend

Extend another surface from **this** one. Name `{surface}` — the surface being extended onto. It gets `extends.surface` pointing here and must subclass `ExtendCli` in its API surface.

Sets `extends: {surface: <this-surface>, actions: [action, …]}` on `{surface}` frontmatter. Empty `extends.actions` means extend all actions marked open; pass an action list only when this surface is not fully open or you are extending actions not marked open.

**example:** capability extends onto `rules`:

```
python -m capability extend rules [<action> …]
```

## Override

Override actions from **this** surface onto `{surface}`. Name `{surface}` and the actions to override.

Pulls matching `##` sections from this surface into `{surface}`'s agentic surface — adapts names and keeps this surface's action order. Adds those actions to `extends.overrides`.

**example:** capability overrides `validate` and `create` onto `rules`:

```
python -m capability override rules validate create
```

At deploy, `{surface}` inherits infrastructure actions (`deploy`, `clean`, `open`, `extend`, `create`, `satisfy`) plus actions in this surface's `open.actions` — or all local actions when `open.actions` is empty.

## Satisfy

read in full → `open` § Satisfy

Run `open` § Satisfy, then verify:

- `extends.surface` is set and parent exists
- required `extends.overrides` from parent's `open.mustBeOveridden` are present

```
python -m extend satisfy
```

## Deploy

Same as `surface §deploy`, plus: actions this surface does not override deploy as `read @{extends.surface} § {action}`.

## Clean

Remove deployed artefacts. Inherited from `surface`.
