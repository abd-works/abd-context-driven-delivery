---
type: surface
generate:
  returns: surface
satisfy:
  returns: surface
is_satisfied: validation-result
deploy:
  parameters:
    ide: cursor|vscode
    target_root: string
  returns: void
clean:
  parameters: none
  returns: void
folder: path
name: string
deployments: deployment[]
type-definitions:
  deployment:
    ide: cursor|vscode
    target_root: string
    deployed_at: timestamp
  validation-result:
    success: boolean
    violations: string[]
  agentic-surface:
    signature
  api-surface:
    signature
  signature:
    actions:
      [
        name
        parameters: [
          name: string
          type: string 
        ]
        return: string
      ]
    properties:
      [
        name
        type
      ]
---
## Surface

Minimal CDD primitive — a folder `{surface}/` with paired agentic and API surfaces.

## Valid surface

A folder is a valid *surface* when all of the following hold:

**Files and identity**

- `{surface}/.cdd-config.json` exists
- `{surface}/{surface}.md` and `{surface}/{surface}.py` exist
- Folder name matches both file stems (e.g. folder `surface` → `surface.md`, `surface.py`)

**Type frontmatter (`{surface}.md`)**

- `type` — which type this file implements (e.g. `surface`); the rest of the frontmatter **is** the type contract — no separate `signature` block
- **Action** (lowercase key; body has matching `##` section in Title Case) — optional typed `parameters` and `returns` (scalar, named type, or inline `{ field: type }`)
- **Property** (lowercase key; value is a type or type reference) — not an action, no `##` section
- `type-definitions` — reusable named types referenced by actions and properties (e.g. `validation-result`, `deployment`)

**Type conformance (`{surface}.py` mirrors frontmatter)**

- Every action in frontmatter has a matching `##` section in the body
- Action **with** `parameters` (including `none`) → `{Surface}` method + `{Surface}Cli` subcommand + fenced `python -m {surface} <action> …` under `##`
- Action **without** `parameters` → agent only: `##` prose, no CLI, no public API method
- Every property in frontmatter (`folder`, `name`, `deployments`, `is_satisfied`, …) exists on `{Surface}` with a compatible shape
- `is_satisfied` returns `validation-result`

**Agent execution**

Read `{surface}.md` frontmatter. For each action: if the action has `parameters` and `{surface}.py` implements the matching method (verified by satisfy), **call the API**; otherwise follow the `##` prose.

**API surface (`{surface}.py`)**

- Class `{Surface}` — PascalCase of `{surface}`; implements methods for api-enhanced actions only
- Class `{Surface}Cli` — routes CLI subcommands to `{Surface}` methods; no business logic in the CLI
- Properties (`folder`, `name`, `deployments`, `is_satisfied`, …) mirror the type contract on `{Surface}`

```
python -m {surface} <action> …
```

**example:**
This surface (`surface/`) has **generate** and **satisfy** (agent) and **deploy** and **clean** (api-enhanced). Properties include **folder**, **name**, **deployments**, **is_satisfied**.

## Generate

Generate changes to target `{surface}.md`, `{surface}.py` and all related files from the surface template. Output must satisfy **Valid surface** above.

read the template in full → `surface/{surface}.md` and follow all instructions.

## Satisfy

Verify the folder satisfies **Valid surface** above.

```
python -m pytest surface/test_surface.py
```

## Deploy

Discover all surfaces under the repo root and deploy each to the IDE area. Copies source to `.cdd/` and emits a SKILL.md pointer to the full `{surface}.md`. Surfaces on the `extend` chain get section wiring from `extend`.

```
python -m surface deploy <cursor|vscode> <target-root>
```

## Clean

Remove deployed artefacts for all discovered surfaces (uses each surface's deploy record when target is omitted).

```
python -m surface clean
```
