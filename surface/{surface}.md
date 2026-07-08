<!--
HOW TO USE THIS TEMPLATE
========================
1. Copy this file to `{surface}/{surface}.md` and create the matching `{surface}.py`
2. Replace `{surface}` and `{Surface}` everywhere
3. Copy the type contract frontmatter from `surface/surface.md` — do not invent a divergent shape
4. Add one `##` section per action (Title Case of the action key)
5. Actions with `parameters` (including `none`) need a fenced `python -m {surface} <action> …` under that `##`
6. Implement `{Surface}` methods and `{Surface}Cli` subcommands only for actions with `parameters`
7. Mirror properties (`folder`, `name`, `deployments`, `is_satisfied`, …) on `{Surface}`
8. Read frontmatter before acting: call API when action has `parameters` and `.py` matches; else follow `##` prose
-->

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

{One or two sentences describing what this surface does.}

## Valid surface

A folder is a valid *surface* when it satisfies **Valid surface** on `surface/surface.md`, including type conformance between this frontmatter and `{surface}.py`.

## Generate

Read `{surface}.md` frontmatter. Generate `{surface}.md`, `{surface}.py` and related files. Output must satisfy **Valid surface**.

read in full → `surface/{surface}.md` and `surface` § Generate

## Satisfy

Verify the folder satisfies **Valid surface**, including type conformance. Check `{Surface}.is_satisfied`; violations list any mismatch between frontmatter, body, and API.

```
python -m pytest surface/test_surface.py
```

## Deploy

{One sentence describing deploy behavior when overridden; omit section when inherited at deploy.}

If `deploy` has `parameters` in frontmatter and `{Surface}.deploy` exists, call the API:

```
python -m {surface} deploy <cursor|vscode> <target-root>
```

## Clean

{One sentence describing clean behavior when overridden; omit section when inherited at deploy.}

If `clean` has `parameters` in frontmatter and `{Surface}.clean` exists, call the API:

```
python -m {surface} clean
```
