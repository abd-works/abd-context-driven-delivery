---
extends: surface
overrides: [generate, satisfy, deploy]
---

Surface extension — inherit actions from another surface at deploy time.

## Open

Mark specific actions as extensible on a source that implements `extend`.

Required: target path and explicit action list. Sets `open: [action, …]` in source frontmatter.

```
python -m extend open <target-path> <action> [<action> …]
```

## Extend

Scaffold `{target}` from `{source}`. Target must implement `extend`. Always requires an explicit action list.

Sets `extends:` and `overrides:` on target frontmatter and seeds `##` stubs.

At deploy, the child inherits infrastructure actions (`deploy`, `clean`, `open`, `extend`, `generate`, `satisfy`) plus parent-local actions listed in the parent's `open:` frontmatter.

```
python -m extend extend <source> <target-path> <action> [<action> …]
```

## Deploy

Same as `surface §deploy`, plus: for surfaces with `extends:` in frontmatter, inherited actions not in `overrides` deploy as `read @{parent} § {action}`.

## Clean

Remove deployed artefacts. Inherited from `surface`.
