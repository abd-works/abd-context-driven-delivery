---
type: surface
surface-signature:
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

- `type` — which type this file implements (e.g. `surface`)
- `{type}-signature` — the type contract: **actions**, **properties**, and `type-definitions` (e.g. `surface-signature` for `type: surface`). Other frontmatter (`extends`, `open`, …) lives at the root alongside it
- **Action** (lowercase key inside `{type}-signature`; body has matching `##` section in Title Case) — optional typed `parameters` and `returns`
- **Property** (lowercase key inside `{type}-signature`; value is a type or type reference) — not an action, no `##` section
- `type-definitions` — inside `{type}-signature`; reusable named types referenced by actions and properties

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
- Nested types mirror `type-definitions` (`{Surface}.ValidationResult`, `{Surface}.Deployment`, …)
- Associations compose the API: `{surface}.type_contract`, `{surface}.alignment`, `{surface}.scaffold`, `{surface}.cli`
- Class `{Surface}.Cli` — nested on `{Surface}` or `{Surface}Cli` at module level; routes CLI subcommands
- Properties (`folder`, `name`, `agentic-surface`, `api-surface`, `deployments`, `is_satisfied`, …) mirror the type contract on `{Surface}` (`agentic-surface` → `agentic_surface`, `api-surface` → `api_surface`)

```
python -m {surface} <action> …
```

**example:**
This surface (`surface/`) has **generate** and **satisfy** (agent) and **deploy** and **clean** (api-enhanced). Properties include **folder**, **name**, **deployments**, **is_satisfied**.

## Generate

Generate changes to target `{surface}.md`, `{surface}.py` and all related files from the surface template. Output must satisfy **Valid surface** above.

Use `{Surface}.scaffold` — three operations **generate** and **satisfy** call as needed:

1. `scaffold.api_from_signature(mode=new|subset, subset=…)` — scaffold `.py` from type contract
2. `scaffold.md_from_signature(mode=new|subset, subset=…)` — scaffold `.md` from type contract
3. `scaffold.signature_from_api(mode=new|subset, subset=…)` — scaffold type contract from existing API

`mode=new` — whole surface; `mode=subset` — pass signature subset to add/merge.

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
