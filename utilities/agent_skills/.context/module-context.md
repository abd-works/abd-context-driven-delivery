# agent_skills — module context

## Purpose
Scans the workspace for Python toolset files and deploys each as a IDE skill shim.
For every discovered toolset under `context_tools/` or `utilities/` it writes a
`SKILL.md` (under `.cursor/skills/` or `.github/skills/` depending on IDE), removes
stale shortcuts, and merges the manifest-gate hook into the IDE hooks config.

Packages under `context_tools/actions/` are **not** deployed as skills. Instead,
deploy writes Cursor commands (`.cursor/commands/{action}.md`) or VS Code prompts
(`.github/prompts/{action}.prompt.md`) for each host lifecycle action (`sketch`,
`iterate`, `grill`, `partition`, `repair`, `improve`) plus companion commands for
`echo` / `handoff`. Those compose with a context-tool skill already in play
(`/cdd` + `/sketch` → run CDD with `action: sketch`).

A saved deploy-state file lets subsequent runs re-deploy without re-asking for
parameters.

When a nearby multi-folder `.code-workspace` includes this repo, Cursor deploys
also write to `~/.cursor/skills` (user-level, available in every project) and each
matching workspace file's parent `.cursor/skills` (shared sibling layout such as
`paradise-mobile/`). Junction checkouts are handled by walking both absolute and
resolve() path forms.

## Seam
`AgentSkills`

## Dependencies
`primitives.actions`, `tools.tool`, `tools.toolset_header`, `focus._decorator`

## Mechanism
Static-analysis pass over each toolset's source file (`ast.parse`) extracts
`@focus`-decorated action names and their focus-group subdirectories, producing
per-focus shortcut descriptors used only for stale-slug cleanup (legacy
per-focus×action commands are removed, not written). Action-package detection uses
path membership under `context_tools/actions/`. Deploy-root resolution walks
ancestors (and sibling dirs) for `*.code-workspace` files; multi-folder matches
expand Cursor write targets beyond the repo root.
